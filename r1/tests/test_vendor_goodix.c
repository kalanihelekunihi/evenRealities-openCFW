/*
 * Host coverage for the openR1 Goodix GH3X2X democode port
 * (r1/port/goodix_gh3x2x/).  Runs the pinned vendor democode subset
 * against a fake I2C register file; no hardware required.
 *
 * Covered:
 *   - port bind/unbind and fail-closed behavior of every trampoline
 *   - HAL translation (device id 0x28, big-endian register wire format,
 *     read-modify-write bit fields, communicate-confirm magic checks)
 *   - error mapping (democode GH3X2X_RET_* codes through the bind ops)
 *   - checked algorithm ABI dispatch plus fail-closed unbound paths
 *   - goodix_mem integrator surface (Gh3x2xPoolIsNotEnough glue)
 *   - end-to-end Gh3x2xDemoInit + start/stop sampling against the fake
 */

#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "openr1/r1_goodix.h"
#include "r1_gh3x2x_algo_bridge.h"
#include "r1_gh3x2x_bind.h"
#include "r1_gh3x2x_port.h"
#include "r1_gh3x2x_primitive_adapter.h"
#include "r1_gh3x2x_provider_composer.h"
#include "r1_gh3x2x_reconstructed_roots.h"
#include "model_data/r1_model_data.h"

#include "gh_demo.h"
#include "gh_demo_inner.h"
#include "gh3x2x_demo_algo_call.h"
#include "gh_drv_control.h"
#include "gh_drv_interface.h"
#include "gh_uprotocol.h"
#include "goodix_hba.h"
#include "goodix_hrv.h"

/* the kernel template wrappers live in gh_demo_user.c without a header */
GU8 hal_gh3x2x_i2c_write(GU8 device_id, const GU8 write_buffer[],
                         GU16 length);
GU8 hal_gh3x2x_i2c_read(GU8 device_id, const GU8 write_buffer[],
                        GU16 write_length, GU8 read_buffer[],
                        GU16 read_length);

/* --- fake GH3X2X device: 16-bit register file behind the I2C hooks --- */

#define FAKE_REG_COUNT 0x10000u
#define FAKE_REG_COMM_CONFIRM 0x0036u
#define FAKE_REG_COMM_CONFIRM_MAGIC 0xAA55u
#define FAKE_REG_SCAN_DONE 0x0718u
#define FAKE_I2C_CMD_ADDR 0xDDDDu
#define FAKE_FIFO_REG_ADDR 0xAAAAu

typedef struct {
    uint16_t regs[FAKE_REG_COUNT];
    uint8_t last_command;
    unsigned int write_calls;
    unsigned int read_calls;
    unsigned int command_calls;
    uint8_t last_device_id;
    uint8_t last_write[8];
    uint16_t last_write_length;
    bool fail_reads;
} fake_device;

typedef struct {
    fake_device device;
    unsigned int i2c_init_calls;
    unsigned int int_pin_init_calls;
    unsigned int reset_pin_init_calls;
    int last_reset_level;
    unsigned int reset_ctrl_calls;
    uint32_t delay_us_total;
    unsigned int delay_calls;
    unsigned int log_calls;
    char last_log[128];
    unsigned int rawdata_calls;
    uint32_t last_rawdata_count;
    unsigned int wear_calls;
    bool last_worn;
    r1_gh3x2x_gsensor_sample gsensor[4];
    uint16_t gsensor_count;
} fake_hal_state;

static fake_hal_state fake;

static void *reconstructed_allocate(void *context, size_t bytes) {
    (void)context;
    return malloc(bytes);
}

static void reconstructed_release(void *context, void *allocation) {
    (void)context;
    free(allocation);
}

static float reconstructed_square_root(float value) {
    if (value <= 0.0f) {
        return 0.0f;
    }
    float estimate = value > 1.0f ? value : 1.0f;
    for (size_t index = 0u; index < 12u; ++index) {
        estimate = 0.5f * (estimate + value / estimate);
    }
    return estimate;
}

static int32_t reconstructed_identity_i32(int32_t value) {
    return value;
}

typedef union {
    max_align_t alignment;
    size_t bytes;
} reconstructed_allocation_header;

typedef struct {
    size_t live_bytes;
    size_t peak_bytes;
    size_t allocations;
    size_t releases;
} reconstructed_allocation_trace;

static void *reconstructed_traced_allocate(void *context, size_t bytes) {
    reconstructed_allocation_trace *const trace = context;
    reconstructed_allocation_header *const header =
        malloc(sizeof(*header) + bytes);
    if (trace == NULL || header == NULL) {
        free(header);
        return NULL;
    }
    header->bytes = bytes;
    trace->live_bytes += bytes;
    if (trace->live_bytes > trace->peak_bytes) {
        trace->peak_bytes = trace->live_bytes;
    }
    ++trace->allocations;
    return header + 1;
}

static void reconstructed_traced_release(void *context, void *allocation) {
    reconstructed_allocation_trace *const trace = context;
    reconstructed_allocation_header *const header =
        (reconstructed_allocation_header *)allocation - 1;
    assert(trace != NULL && allocation != NULL &&
           header->bytes <= trace->live_bytes);
    trace->live_bytes -= header->bytes;
    ++trace->releases;
    free(header);
}

static void fake_reset(void) {
    memset(&fake, 0, sizeof(fake));
    fake.last_reset_level = -1;
    /* magic values the driver polls during init */
    fake.device.regs[FAKE_REG_COMM_CONFIRM] = FAKE_REG_COMM_CONFIRM_MAGIC;
    fake.device.regs[FAKE_REG_SCAN_DONE] = 0x0001u;
}

static void fake_i2c_init(void *context) {
    (void)context;
    ++fake.i2c_init_calls;
}

static void fake_i2c_write(void *context, uint8_t device_id,
                           const uint8_t *data, uint16_t length) {
    fake_device *device = context;
    device->last_device_id = device_id;
    device->last_write_length = length;
    const uint16_t kept = length < sizeof(device->last_write)
        ? length : (uint16_t)sizeof(device->last_write);
    memcpy(device->last_write, data, kept);
    if (length < 3u) {
        return;
    }
    const uint16_t address = (uint16_t)(((uint16_t)data[0] << 8u) | data[1]);
    if (address == FAKE_I2C_CMD_ADDR) {
        device->last_command = data[2];
        ++device->command_calls;
        return;
    }
    ++device->write_calls;
    for (uint16_t offset = 2u; offset + 1u < length; offset += 2u) {
        device->regs[address + ((offset - 2u) / 2u)] =
            (uint16_t)(((uint16_t)data[offset] << 8u) | data[offset + 1u]);
    }
}

static void fake_i2c_read(void *context, uint8_t device_id,
                          const uint8_t *command, uint16_t command_length,
                          uint8_t *data, uint16_t data_length) {
    fake_device *device = context;
    device->last_device_id = device_id;
    ++device->read_calls;
    memset(data, 0, data_length);
    if (device->fail_reads || command_length < 2u) {
        return;
    }
    const uint16_t address =
        (uint16_t)(((uint16_t)command[0] << 8u) | command[1]);
    if (address == FAKE_FIFO_REG_ADDR) {
        return; /* empty FIFO: zeros */
    }
    for (uint16_t index = 0u; index + 1u < data_length; index += 2u) {
        const uint16_t value = device->regs[address + (index / 2u)];
        data[index] = (uint8_t)(value >> 8u);
        data[index + 1u] = (uint8_t)(value & 0xFFu);
    }
}

static void fake_int_pin_init(void *context) {
    (void)context;
    ++fake.int_pin_init_calls;
}

static void fake_reset_pin_init(void *context) {
    (void)context;
    ++fake.reset_pin_init_calls;
}

static void fake_reset_pin_ctrl(void *context, uint8_t level) {
    (void)context;
    fake.last_reset_level = level;
    ++fake.reset_ctrl_calls;
}

static void fake_gsensor_get(void *context, r1_gh3x2x_gsensor_sample *samples,
                             uint16_t *count) {
    (void)context;
    uint16_t index = 0u;
    for (; index < fake.gsensor_count; ++index) {
        samples[index] = fake.gsensor[index];
    }
    *count = fake.gsensor_count;
}

static void fake_delay_us(void *context, uint32_t microseconds) {
    (void)context;
    fake.delay_us_total += microseconds;
    ++fake.delay_calls;
}

static void fake_log(void *context, const char *text) {
    (void)context;
    ++fake.log_calls;
    snprintf(fake.last_log, sizeof(fake.last_log), "%s", text);
}

static void fake_rawdata_notify(void *context, const uint32_t *rawdata,
                                uint32_t count) {
    (void)context;
    (void)rawdata;
    ++fake.rawdata_calls;
    fake.last_rawdata_count = count;
}

static void fake_wear_notify(void *context, bool worn) {
    (void)context;
    ++fake.wear_calls;
    fake.last_worn = worn;
}

static const r1_gh3x2x_hal fake_hal = {
    .context = &fake.device,
    .i2c_init = fake_i2c_init,
    .i2c_write = fake_i2c_write,
    .i2c_read = fake_i2c_read,
    .int_pin_init = fake_int_pin_init,
    .reset_pin_init = fake_reset_pin_init,
    .reset_pin_ctrl = fake_reset_pin_ctrl,
    .gsensor_get = fake_gsensor_get,
    .delay_us = fake_delay_us,
    .log = fake_log,
    .rawdata_notify = fake_rawdata_notify,
    .wear_notify = fake_wear_notify,
};

/* --- port trampoline coverage --- */

static void test_port_unbound_fail_closed(void) {
    r1_gh3x2x_port_unbind_hal();
    assert(!r1_gh3x2x_port_hal_bound());

    uint8_t buffer[4] = {0xDEu, 0xADu, 0xBEu, 0xEFu};
    gh3026_i2c_read(0x28u, NULL, 0u, buffer, sizeof(buffer));
    assert(buffer[0] == 0u && buffer[1] == 0u && buffer[2] == 0u &&
           buffer[3] == 0u);

    /* every other trampoline is a silent no-op while unbound */
    gh3026_i2c_init();
    gh3026_i2c_write(0x28u, buffer, sizeof(buffer));
    gh3026_int_pin_init();
    gh3026_reset_pin_init();
    gh3026_reset_pin_ctrl(1u);
    r1_gh3x2x_gsensor_sample samples[2];
    uint16_t count = 7u;
    gh3026_gsensor_data_get(samples, &count);
    assert(count == 0u);
    delay_us(100u);
    gh3x2x_print_fmt("unbound %d", 1);
    uint32_t rawdata[2] = {1u, 2u};
    gh3x2x_rawdata_notify(rawdata, 2u);
    gh3x2x_wear_evt_notify(true);
    Gh3x2xPoolIsNotEnough(); /* no pool ops bound: must return */
}

static void test_port_hal_forwarding(void) {
    fake_reset();
    r1_gh3x2x_port_bind_hal(&fake_hal);
    assert(r1_gh3x2x_port_hal_bound());

    gh3026_i2c_init();
    assert(fake.i2c_init_calls == 1u);

    const uint8_t write_bytes[4] = {0x12u, 0x34u, 0xABu, 0xCDu};
    gh3026_i2c_write(0x28u, write_bytes, sizeof(write_bytes));
    assert(fake.device.last_device_id == 0x28u);
    assert(fake.device.last_write_length == 4u);
    assert(memcmp(fake.device.last_write, write_bytes, 4u) == 0);
    assert(fake.device.regs[0x1234u] == 0xABCDu);

    uint8_t read_back[2] = {0u, 0u};
    const uint8_t read_cmd[2] = {0x12u, 0x34u};
    gh3026_i2c_read(0x28u, read_cmd, sizeof(read_cmd), read_back,
                    sizeof(read_back));
    assert(read_back[0] == 0xABu && read_back[1] == 0xCDu);

    gh3026_int_pin_init();
    gh3026_reset_pin_init();
    gh3026_reset_pin_ctrl(1u);
    gh3026_reset_pin_ctrl(0u);
    assert(fake.int_pin_init_calls == 1u);
    assert(fake.reset_pin_init_calls == 1u);
    assert(fake.reset_ctrl_calls == 2u);
    assert(fake.last_reset_level == 0);

    fake.gsensor_count = 2u;
    fake.gsensor[0] = (r1_gh3x2x_gsensor_sample){.x = 1, .y = -2, .z = 3};
    fake.gsensor[1] = (r1_gh3x2x_gsensor_sample){.x = 4, .y = 5, .z = -6};
    r1_gh3x2x_gsensor_sample samples[4];
    uint16_t count = 0u;
    gh3026_gsensor_data_get(samples, &count);
    assert(count == 2u);
    assert(samples[0].x == 1 && samples[0].y == -2 && samples[0].z == 3);
    assert(samples[1].z == -6);

    delay_us(250u);
    assert(fake.delay_calls == 1u && fake.delay_us_total == 250u);

    gh3x2x_print_fmt("driver log %s", "text");
    assert(fake.log_calls == 1u);
    assert(strcmp(fake.last_log, "driver log %s") == 0);

    uint32_t rawdata[3] = {10u, 20u, 30u};
    gh3x2x_rawdata_notify(rawdata, 3u);
    assert(fake.rawdata_calls == 1u && fake.last_rawdata_count == 3u);

    gh3x2x_wear_evt_notify(true);
    assert(fake.wear_calls == 1u && fake.last_worn);

    /* NULL bind returns to the fail-closed state */
    r1_gh3x2x_port_bind_hal(NULL);
    assert(!r1_gh3x2x_port_hal_bound());
    read_back[0] = 0xFFu;
    gh3026_i2c_read(0x28u, read_cmd, sizeof(read_cmd), read_back, 1u);
    assert(read_back[0] == 0u);
}

/* --- goodix_mem integrator surface --- */

typedef struct {
    unsigned int record_calls;
    uint32_t last_info1;
    unsigned int halt_calls;
} fake_pool_state;

static fake_pool_state fake_pool;

static void fake_pool_record(void *context, uint32_t info1) {
    (void)context;
    ++fake_pool.record_calls;
    fake_pool.last_info1 = info1;
}

static void fake_pool_halt(void *context) {
    (void)context;
    ++fake_pool.halt_calls;
}

static void test_pool_glue(void) {
    memset(&fake_pool, 0, sizeof(fake_pool));
    const r1_goodix_pool_fatal_ops ops = {
        .record = fake_pool_record,
        .halt = fake_pool_halt,
        .context = NULL,
    };
    r1_gh3x2x_pool_bind(&ops);
    Gh3x2xPoolIsNotEnough();
    assert(fake_pool.record_calls == 1u);
    assert(fake_pool.last_info1 == 0u); /* void(void) seam carries no info1 */
    assert(fake_pool.halt_calls == 1u);
    r1_gh3x2x_pool_bind(NULL);
}

/* --- HAL translation through the compiled driver source --- */

static void test_driver_register_translation(void) {
    fake_reset();
    r1_gh3x2x_port_bind_hal(&fake_hal);

    /* the kernel template registers the hal_* wrappers from gh_demo_user.c */
    assert(GH3X2X_RegisterI2cOperationFunc(GH3X2X_I2C_ID_SEL_1L0L,
                                           hal_gh3x2x_i2c_write,
                                           hal_gh3x2x_i2c_read) ==
           GH3X2X_RET_OK);

    GH3X2X_WriteReg(0x0200u, 0x1020u);
    assert(fake.device.regs[0x0200u] == 0x1020u);
    assert(GH3X2X_ReadReg(0x0200u) == 0x1020u);

    /* read-modify-write bit field: set bits [4:2] of 0x0200 to 0b101 */
    GH3X2X_WriteRegBitField(0x0200u, 2u, 4u, 0x5u);
    assert(GH3X2X_ReadReg(0x0200u) == (uint16_t)(0x1020u | (0x5u << 2u)));
    assert(GH3X2X_ReadRegBitField(0x0200u, 2u, 4u) == 0x5u);

    /* command path: SendCmd issues a 3-byte write to 0xDDDD (the driver
     * may have sent a wakeup command first if the sleep flag was set) */
    const unsigned int commands_before = fake.device.command_calls;
    GH3X2X_SendCmd(GH3X2X_CMD_RESET);
    assert(fake.device.command_calls == commands_before + 1u);
    assert(fake.device.last_command == GH3X2X_CMD_RESET);

    /* communicate confirm: magic at 0x0036 plus invert/verify on 0x01EC */
    fake.device.regs[0x01ECu] = 0x1234u;
    assert(GH3X2X_CommunicateConfirm() == GH3X2X_RET_OK);
    assert(fake.device.regs[0x01ECu] == 0x1234u); /* restored */

    fake.device.regs[FAKE_REG_COMM_CONFIRM] = 0u;
    assert(GH3X2X_CommunicateConfirm() == GH3X2X_RET_COMM_ERROR);
    fake.device.regs[FAKE_REG_COMM_CONFIRM] = FAKE_REG_COMM_CONFIRM_MAGIC;

    /* bad registration parameters fail with the democode's own code */
    assert(GH3X2X_RegisterI2cOperationFunc(GH3X2X_I2C_ID_SEL_1L0L, NULL,
                                           hal_gh3x2x_i2c_read) ==
           GH3X2X_RET_PARAMETER_ERROR);
}

static void test_driver_comm_error_mapping(void) {
    fake_reset();
    r1_gh3x2x_port_bind_hal(&fake_hal);
    assert(GH3X2X_RegisterI2cOperationFunc(GH3X2X_I2C_ID_SEL_1L0L,
                                           hal_gh3x2x_i2c_write,
                                           hal_gh3x2x_i2c_read) ==
           GH3X2X_RET_OK);
    /* every read returns zeros: the magic check fails closed */
    fake.device.fail_reads = true;
    assert(GH3X2X_CommunicateConfirm() == GH3X2X_RET_COMM_ERROR);
    assert(GH3X2X_Init(&g_stGh3x2xCfgListArr[0]) == GH3X2X_RET_COMM_ERROR);
}

/* --- checked algorithm bridge and excluded protocol layer --- */

typedef struct {
    unsigned int initialize_calls;
    unsigned int process_calls;
    unsigned int deinitialize_calls;
    unsigned int sensor_calls;
    unsigned int register_calls;
    bool invalid_result;
    r1_gh3x2x_algo_frame last_frame;
} fake_algo_state;

typedef struct {
    unsigned int calls;
    uint8_t function_offset;
    uint32_t frame_count;
    r1_gh3x2x_algo_result result;
} fake_result_observer_state;

typedef struct {
    unsigned int calls;
    uint8_t function_offset;
    uint32_t frame_count;
    uint32_t first_raw_value;
} fake_frame_observer_state;

static void fake_result_observer(
    void *context, const r1_gh3x2x_algo_frame *frame,
    const r1_gh3x2x_algo_result *result) {
    fake_result_observer_state *state = context;
    ++state->calls;
    state->function_offset = frame->function_offset;
    state->frame_count = frame->frame_count;
    state->result = *result;
}

static void fake_frame_observer(
    void *context, const r1_gh3x2x_algo_frame *frame) {
    fake_frame_observer_state *state = context;
    ++state->calls;
    state->function_offset = frame->function_offset;
    state->frame_count = frame->frame_count;
    state->first_raw_value = frame->raw_values[0];
}

static bool fake_algo_initialize(void *context,
                                 const r1_gh3x2x_algo_frame *frame) {
    fake_algo_state *state = context;
    ++state->initialize_calls;
    state->last_frame = *frame;
    return true;
}

static bool fake_algo_process(void *context,
                              const r1_gh3x2x_algo_frame *frame,
                              r1_gh3x2x_algo_result *result) {
    fake_algo_state *state = context;
    ++state->process_calls;
    state->last_frame = *frame;
    result->updated = true;
    result->value_mask = 0x0005u;
    result->value_count = state->invalid_result ? 1u : 2u;
    result->values[0] = 72;
    result->values[1] = 98;
    return true;
}

static bool fake_algo_deinitialize(void *context, uint32_t function_mask,
                                   uint8_t function_offset) {
    fake_algo_state *state = context;
    assert(function_mask == GH3X2X_FUNCTION_HR);
    assert(function_offset == GH3X2X_FUNC_OFFSET_HR);
    ++state->deinitialize_calls;
    return true;
}

static bool fake_algo_version(void *context, uint8_t function_offset,
                              char *destination, size_t destination_size) {
    fake_algo_state *state = context;
    assert(function_offset == GH3X2X_FUNC_OFFSET_HR);
    assert(destination_size >= sizeof("openr1-hr"));
    ++state->register_calls;
    memcpy(destination, "openr1-hr", sizeof("openr1-hr"));
    return true;
}

static void fake_algo_sensor_enable(void *context, bool accelerometer,
                                    bool capacitive, bool temperature) {
    fake_algo_state *state = context;
    assert(accelerometer);
    assert(!capacitive);
    assert(temperature);
    ++state->sensor_calls;
}

static bool fake_algo_register(void *context, uint16_t address,
                               uint16_t value) {
    fake_algo_state *state = context;
    assert(address == 0x30C0u);
    assert(value == 0x0001u);
    ++state->register_calls;
    return true;
}

static void test_algorithm_bridge(void) {
    assert(R1_GH3X2X_ALGO_FUNCTION_HR == GH3X2X_FUNC_OFFSET_HR);
    assert(R1_GH3X2X_ALGO_FUNCTION_HRV == GH3X2X_FUNC_OFFSET_HRV);
    assert(R1_GH3X2X_ALGO_FUNCTION_HSM == GH3X2X_FUNC_OFFSET_HSM);
    assert(R1_GH3X2X_ALGO_FUNCTION_SPO2 == GH3X2X_FUNC_OFFSET_SPO2);
    r1_gh3x2x_algo_unbind_provider();
    r1_gh3x2x_algo_unbind_result_observer();
    r1_gh3x2x_algo_unbind_frame_observer();
    assert(!r1_gh3x2x_algo_provider_bound());
    assert(!r1_gh3x2x_algo_result_observer_bound());
    assert(!r1_gh3x2x_algo_frame_observer_bound());
    assert(GH3X2X_AlgoInit(GH3X2X_FUNCTION_HR) == GH3X2X_RET_RESOURCE_ERROR);
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_SPO2) ==
           GH3X2X_RET_RESOURCE_ERROR);
    assert(GH3X2X_AlgoDeinit(0xFFFFFFFFu) == GH3X2X_RET_PARAMETER_ERROR);

    GCHAR version[150];
    memset(version, 0x5A, sizeof(version));
    GH3X2X_AlgoVersion(0u, version);
    assert(strcmp(version, "no_ver") == 0);
    memset(version, 0x5A, sizeof(version));
    GH3X2X_GetVersion(0u, version);
    assert(strcmp(version, "no_ver") == 0);

    GU8 channel_map[2] = {0x10u, 0x21u};
    GU32 raw_values[2] = {100001u, 200002u};
    GU32 agc_values[2] = {0x010203u, 0x040506u};
    GU32 frame_flags[8] = {0u};
    GS16 acceleration[3] = {-11, 22, -33};
    GU8 last_gain[2] = {0u};
    GU32 frame_count = 42u;
    STGh3x2xFunctionInfo function_info = {
        .usSampleRate = 25u,
        .uchChnlNum = 2u,
    };
    STGh3x2xAlgoResult vendor_result;
    memset(&vendor_result, 0x5A, sizeof(vendor_result));
    STGh3x2xFrameInfo vendor_frame = {
        .unFunctionID = GH3X2X_FUNCTION_HR,
        .pstFunctionInfo = &function_info,
        .uchFuntionChnlLimit = 2u,
        .pchChnlMap = channel_map,
        .punFrameRawdata = raw_values,
        .pusFrameGsensordata = acceleration,
        .punFrameAgcInfo = agc_values,
        .punFrameFlag = frame_flags,
        .puchFrameLastGain = last_gain,
        .punFrameCnt = &frame_count,
        .pstAlgoResult = &vendor_result,
    };
    STGh3x2xFrameInfo hsm_frame = vendor_frame;
    hsm_frame.unFunctionID = GH3X2X_FUNCTION_HSM;
    hsm_frame.pstAlgoResult = NULL;
    const STGh3x2xFrameInfo *frames[GH3X2X_FUNC_OFFSET_MAX] = {0};
    frames[GH3X2X_FUNC_OFFSET_HR] = &vendor_frame;
    frames[GH3X2X_FUNC_OFFSET_HSM] = &hsm_frame;
    GH3X2X_AlgoCallConfigInit(frames, 0u);

    fake_algo_state state;
    memset(&state, 0, sizeof(state));
    const r1_gh3x2x_algo_provider provider = {
        .context = &state,
        .supported_functions = GH3X2X_FUNCTION_HR,
        .initialize = fake_algo_initialize,
        .process = fake_algo_process,
        .deinitialize = fake_algo_deinitialize,
        .version = fake_algo_version,
        .sensor_enable = fake_algo_sensor_enable,
        .write_virtual_register = fake_algo_register,
    };
    r1_gh3x2x_algo_bind_provider(&provider);
    fake_result_observer_state observer_state;
    memset(&observer_state, 0, sizeof(observer_state));
    r1_gh3x2x_algo_bind_result_observer(
        fake_result_observer, &observer_state);
    fake_frame_observer_state frame_observer_state;
    memset(&frame_observer_state, 0, sizeof(frame_observer_state));
    r1_gh3x2x_algo_bind_frame_observer(
        fake_frame_observer, &frame_observer_state);
    assert(r1_gh3x2x_algo_result_observer_bound());
    assert(r1_gh3x2x_algo_frame_observer_bound());
    assert(r1_gh3x2x_algo_provider_bound());
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HR) ==
           GH3X2X_RET_RESOURCE_ERROR);

    /* A later malformed frame must roll back every provider root initialized
     * by the same mixed-mask request. HSM itself has no provider deinit. */
    hsm_frame.punFrameRawdata = NULL;
    assert(GH3X2X_AlgoInit(GH3X2X_FUNCTION_HR |
                           GH3X2X_FUNCTION_HSM) ==
           GH3X2X_RET_GENERIC_ERROR);
    assert(state.initialize_calls == 1u);
    assert(state.deinitialize_calls == 1u);
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HR) ==
           GH3X2X_RET_RESOURCE_ERROR);
    hsm_frame.punFrameRawdata = raw_values;

    assert(GH3X2X_AlgoInit(GH3X2X_FUNCTION_HR) == GH3X2X_RET_OK);
    assert(state.initialize_calls == 2u);
    assert(state.last_frame.function_offset == GH3X2X_FUNC_OFFSET_HR);
    assert(state.last_frame.channel_count == 2u);
    assert(state.last_frame.sample_rate_hz == 25u);
    assert(state.last_frame.frame_count == 42u);
    assert(state.last_frame.raw_values[1] == 200002u);
    assert(state.last_frame.acceleration[2] == -33);

    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HR) == GH3X2X_RET_OK);
    assert(state.process_calls == 1u);
    assert(vendor_result.uchUpdateFlag == 1u);
    assert(vendor_result.uchResultNum == 2u);
    assert(vendor_result.usResultBit == 0x0005u);
    assert(vendor_result.snResult[0] == 72);
    assert(vendor_result.snResult[1] == 98);
    assert(observer_state.calls == 1u);
    assert(observer_state.function_offset == GH3X2X_FUNC_OFFSET_HR);
    assert(observer_state.frame_count == 42u);
    assert(observer_state.result.updated);
    assert(observer_state.result.value_count == 2u);
    assert(observer_state.result.values[0] == 72);

    /* R1's HSM row has no algorithm executor: mask 0x08 is a checked raw
     * frame source and must not call the biometric provider or fabricate an
     * algorithm result. */
    assert(GH3X2X_AlgoInit(GH3X2X_FUNCTION_HSM) == GH3X2X_RET_OK);
    assert(state.initialize_calls == 2u);
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HSM) == GH3X2X_RET_OK);
    assert(state.process_calls == 1u);
    assert(frame_observer_state.calls == 1u);
    assert(frame_observer_state.function_offset == GH3X2X_FUNC_OFFSET_HSM);
    assert(frame_observer_state.frame_count == 42u);
    assert(frame_observer_state.first_raw_value == 100001u);
    hsm_frame.punFrameRawdata = NULL;
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HSM) ==
           GH3X2X_RET_GENERIC_ERROR);
    assert(frame_observer_state.calls == 1u);
    hsm_frame.punFrameRawdata = raw_values;
    assert(GH3X2X_AlgoDeinit(GH3X2X_FUNCTION_HSM) == GH3X2X_RET_OK);
    assert(state.deinitialize_calls == 1u);
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HSM) ==
           GH3X2X_RET_RESOURCE_ERROR);

    state.invalid_result = true;
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HR) ==
           GH3X2X_RET_PARAMETER_ERROR);
    assert(vendor_result.snResult[0] == 72); /* invalid output was not copied */
    assert(observer_state.calls == 1u); /* invalid output was not observed */
    state.invalid_result = false;

    GH3X2X_AlgoSensorEnable(1u, 0u, 1u);
    assert(state.sensor_calls == 1u);
    GH3X2X_WriteAlgConfigWithVirtualReg(0x30C0u, 0x0001u);
    assert(state.register_calls == 1u);
    memset(version, 0x5A, sizeof(version));
    GH3X2X_AlgoVersion(GH3X2X_FUNC_OFFSET_HR, version);
    assert(strcmp(version, "openr1-hr") == 0);
    assert(state.register_calls == 2u);

    assert(GH3X2X_AlgoDeinit(GH3X2X_FUNCTION_HR) == GH3X2X_RET_OK);
    assert(state.deinitialize_calls == 2u);
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_HR) ==
           GH3X2X_RET_RESOURCE_ERROR);
    r1_gh3x2x_algo_unbind_provider();
    r1_gh3x2x_algo_unbind_result_observer();
    r1_gh3x2x_algo_unbind_frame_observer();
    assert(!r1_gh3x2x_algo_result_observer_bound());
    assert(!r1_gh3x2x_algo_frame_observer_bound());
    GH3X2X_AlgoCallConfigInit(NULL, 0u);

    GH3X2X_TimestampSyncAccInit();
    GH3X2X_TimestampSyncPpgInit(GH3X2X_FUNCTION_HR);
    GH3X2X_TimestampSyncSetPpgIntFlag(1u);
    GH3X2X_TimestampSyncFillAccSyncBuffer(0u, 1, 2, 3);
    GH3X2X_TimestampSyncFillPpgSyncBuffer(0u, &vendor_frame);
    assert(GH3X2X_TimestampSyncGetFrameDataFlag() == 1u);

    GU8 packet[16];
    GU8 payload[4] = {1u, 2u, 3u, 4u};
    assert(GH3X2X_UprotocolPacketFormat(0x01u, packet, payload, 4u) == 0u);
    Gh3x2xDemoSendProtocolData(packet, 0u);
}

static void test_recovered_algorithm_inputs(void) {
    const goodix_hba_config *hr_configuration =
        (const goodix_hba_config *)goodix_hba_config_get_arr();
    assert(hr_configuration != NULL &&
           goodix_hba_config_get_size() ==
               (int32_t)sizeof(*hr_configuration));
    assert(hr_configuration->mode == 0 && hr_configuration->fs == 25u &&
           hr_configuration->valid_ch_num == 4 &&
           hr_configuration->hba_earliest_output_time == 9 &&
           hr_configuration->hba_latest_output_time == 20 &&
           hr_configuration->raw_ppg_scale == 202 &&
           hr_configuration->delay_time == 5 &&
           hr_configuration->valid_score_scale == 1);
    const goodix_hrv_config *hrv_configuration =
        (const goodix_hrv_config *)goodix_hrv_config_get_arr();
    assert(hrv_configuration != NULL &&
           goodix_hrv_config_get_size() ==
               (int32_t)sizeof(*hrv_configuration));
    assert(hrv_configuration->need_ipl == 1 &&
           hrv_configuration->fs == 100u &&
           hrv_configuration->acc_thr[0] == 200000 &&
           hrv_configuration->acc_thr[1] == 100000 &&
           hrv_configuration->acc_thr[2] == 30000 &&
           hrv_configuration->acc_thr[3] == 30000);

    const uint32_t raw_values[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        UINT32_MAX, 2u, 3u, 4u, 5u, 6u,
        7u, 8u, 9u, 10u, 11u, 12u,
    };
    const uint32_t agc_values[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        UINT32_C(0x00010203), UINT32_C(0x00040506),
        UINT32_C(0x00070809), UINT32_C(0x000a0b0c),
        UINT32_C(0x000d0e0f), UINT32_C(0x00101112),
        UINT32_C(0x00131415), UINT32_C(0x00161718),
        UINT32_C(0x00191a1b), UINT32_C(0x001c1d1e),
        UINT32_C(0x001f2021), UINT32_C(0x00222324),
    };
    r1_gh3x2x_algo_frame frame = {
        .function_mask = GH3X2X_FUNCTION_HR,
        .function_offset = GH3X2X_FUNC_OFFSET_HR,
        .channel_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .raw_values = raw_values,
        .agc_values = agc_values,
        .acceleration = {-101, 202, -303},
        .frame_count = UINT32_C(0x12345678),
    };
    r1_gh3x2x_algo_input input;
    memset(&input, 0x5a, sizeof(input));
    assert(r1_gh3x2x_algo_prepare_hr_input(&frame, 3u, &input));
    assert(input.frame_id == 0x78u && input.total_channel_count == 4u);
    assert(input.sleep_flag == 3u && input.bit_count == 24u &&
           input.chip_type == 1u && input.data_type == 0u);
    assert(input.enable_flags[0] == 0xf0u &&
           input.enable_flags[1] == 0u);
    assert(input.channel_values[0] == -1 && input.channel_values[3] == 4 &&
           input.channel_values[4] == 0);
    assert(input.acceleration[0] == -101 &&
           input.acceleration[2] == -303);
    const uint8_t filter_code[1] = {5u};
    goodix_primitives_hba_process_input hr_primitive;
    assert(r1_gh3x2x_algo_bind_hr_primitive_input(
        &input, filter_code, sizeof(filter_code), &hr_primitive));
    assert(hr_primitive.channel_values == input.channel_values &&
           hr_primitive.channel_value_count == 12u &&
           hr_primitive.enable_flags == input.enable_flags &&
           hr_primitive.enable_flag_count == 2u &&
           hr_primitive.channel_count == 4u &&
           hr_primitive.accelerometer[1] == 202 &&
           hr_primitive.filter_code == filter_code);

    uint8_t default_hr_map[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {0u};
    assert(r1_gh3x2x_algo_hr_default_channel_map(default_hr_map));
    const uint8_t expected_default_hr_map[
        R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        0u, 1u, 2u, 3u, UINT8_MAX, UINT8_MAX,
        UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX,
        UINT8_MAX, UINT8_MAX,
    };
    assert(memcmp(default_hr_map, expected_default_hr_map,
                  sizeof(default_hr_map)) == 0);
    assert(!r1_gh3x2x_algo_hr_default_channel_map(NULL));

    frame.function_mask = GH3X2X_FUNCTION_HRV;
    frame.function_offset = GH3X2X_FUNC_OFFSET_HRV;
    assert(r1_gh3x2x_algo_prepare_hrv_input(&frame, 73u, 4u, &input));
    assert(input.enable_flags[0] == 0xf0u && input.last_hr == 73u);
    assert(input.gain_codes[0] == 3u && input.gain_codes[3] == 12u);
    assert(input.drive_currents[0] == 3u &&
           input.drive_currents[3] == 21u);
    goodix_primitives_hrv_process_input hrv_primitive;
    assert(r1_gh3x2x_algo_bind_hrv_primitive_input(
        &input, &hrv_primitive));
    assert(hrv_primitive.channel_value_count == 4u &&
           hrv_primitive.presence_bytes == input.enable_flags &&
           hrv_primitive.gain_codes == input.gain_codes &&
           hrv_primitive.drive_currents == input.drive_currents &&
           hrv_primitive.last_hr == 73u && hrv_primitive.axis_y == 202);

    const uint8_t spo2_map[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        3u, 2u, 1u, 0u, 4u, UINT8_MAX,
        6u, 7u, 11u, 10u, 9u, 8u,
    };
    frame.function_mask = GH3X2X_FUNCTION_SPO2;
    frame.function_offset = GH3X2X_FUNC_OFFSET_SPO2;
    assert(r1_gh3x2x_algo_prepare_spo2_input(
        &frame, spo2_map, 7u, &input));
    assert(input.enable_flags[0] == 0xfbu &&
           input.enable_flags[1] == 0xf0u);
    assert(input.channel_values[0] == 4 && input.channel_values[3] == -1 &&
           input.channel_values[4] == 5 && input.channel_values[5] == 0 &&
           input.channel_values[8] == 12 && input.channel_values[11] == 9);
    assert(input.sleep_flag == 7u);
    assert(input.gain_codes[0] == 12u && input.drive_currents[0] == 21u &&
           input.gain_codes[8] == 4u && input.drive_currents[8] == 69u);
    goodix_primitives_spo2_calc_input spo2_primitive;
    assert(r1_gh3x2x_algo_bind_spo2_primitive_input(
        &input, &spo2_primitive));
    assert(spo2_primitive.channel_values == input.channel_values &&
           spo2_primitive.channel_value_count == 12u &&
           spo2_primitive.enable_flags == input.enable_flags &&
           spo2_primitive.enable_flag_count == 2u &&
           spo2_primitive.total_channel_count == 4u &&
           spo2_primitive.acceleration[2] == -303 &&
           spo2_primitive.sleep_flag == 7u &&
           spo2_primitive.gain_codes == input.gain_codes &&
           spo2_primitive.drive_currents == input.drive_currents);

    uint8_t default_spo2_map[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {0u};
    assert(r1_gh3x2x_algo_spo2_default_channel_map(default_spo2_map));
    const uint8_t expected_default_spo2_map[
        R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX,
        1u, UINT8_MAX, UINT8_MAX, UINT8_MAX,
        0u, UINT8_MAX, UINT8_MAX, UINT8_MAX,
    };
    assert(memcmp(default_spo2_map, expected_default_spo2_map,
                  sizeof(default_spo2_map)) == 0);
    assert(!r1_gh3x2x_algo_spo2_default_channel_map(NULL));

    r1_gh3x2x_algo_input unchanged;
    memset(&unchanged, 0xa5, sizeof(unchanged));
    input = unchanged;
    uint8_t invalid_map[R1_GH3X2X_ALGO_INPUT_CHANNELS];
    memcpy(invalid_map, spo2_map, sizeof(invalid_map));
    invalid_map[0] = R1_GH3X2X_ALGO_INPUT_CHANNELS;
    assert(!r1_gh3x2x_algo_prepare_spo2_input(
        &frame, invalid_map, 0u, &input));
    assert(memcmp(&input, &unchanged, sizeof(input)) == 0);
    frame.function_offset = GH3X2X_FUNC_OFFSET_HR;
    assert(!r1_gh3x2x_algo_prepare_spo2_input(
        &frame, spo2_map, 0u, &input));
    assert(memcmp(&input, &unchanged, sizeof(input)) == 0);
}

/* --- exact recovered HR/HRV/SpO2 wrapper composition --- */

typedef struct {
    unsigned int initialize_calls;
    unsigned int process_calls;
    unsigned int deinitialize_calls;
    unsigned int version_calls;
    bool initialize_ok;
    bool deinitialize_ok;
    r1_gh3x2x_root_status status;
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS];
    r1_gh3x2x_algo_frame last_frame;
    r1_gh3x2x_algo_input last_input;
    const char *version_text;
} fake_composer_root;

typedef struct {
    unsigned int sensor_calls;
    bool accelerometer;
    bool capacitive;
    bool temperature;
    unsigned int register_calls;
    uint16_t address;
    uint16_t value;
    bool register_ok;
} fake_composer_control;

static bool fake_composer_initialize(
    void *context, const r1_gh3x2x_algo_frame *frame) {
    fake_composer_root *root = context;
    ++root->initialize_calls;
    root->last_frame = *frame;
    return root->initialize_ok;
}

static r1_gh3x2x_root_status fake_composer_process(
    void *context, const r1_gh3x2x_algo_input *input,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]) {
    fake_composer_root *root = context;
    ++root->process_calls;
    root->last_input = *input;
    for (size_t index = 0u; index < R1_GH3X2X_PUBLIC_RESULT_WORDS;
         ++index) {
        output[index] = root->output[index];
    }
    return root->status;
}

static bool fake_composer_deinitialize(void *context) {
    fake_composer_root *root = context;
    ++root->deinitialize_calls;
    return root->deinitialize_ok;
}

static bool fake_composer_version(void *context, char *destination,
                                  size_t destination_size) {
    fake_composer_root *root = context;
    ++root->version_calls;
    const size_t length = strlen(root->version_text);
    if (length + 1u > destination_size) {
        return false;
    }
    memcpy(destination, root->version_text, length + 1u);
    return true;
}

static void fake_composer_sensor_enable(void *context, bool accelerometer,
                                        bool capacitive, bool temperature) {
    fake_composer_control *control = context;
    ++control->sensor_calls;
    control->accelerometer = accelerometer;
    control->capacitive = capacitive;
    control->temperature = temperature;
}

static bool fake_composer_write_register(void *context, uint16_t address,
                                         uint16_t value) {
    fake_composer_control *control = context;
    ++control->register_calls;
    control->address = address;
    control->value = value;
    return control->register_ok;
}

static r1_gh3x2x_root_binding fake_composer_binding(
    fake_composer_root *root) {
    const r1_gh3x2x_root_binding binding = {
        .context = root,
        .initialize = fake_composer_initialize,
        .process = fake_composer_process,
        .deinitialize = fake_composer_deinitialize,
        .version = fake_composer_version,
    };
    return binding;
}

static r1_gh3x2x_algo_frame fake_composer_frame(
    uint8_t offset, const uint32_t *raw_values,
    const uint32_t *agc_values) {
    const r1_gh3x2x_algo_frame frame = {
        .function_mask = (uint32_t)1u << offset,
        .function_offset = offset,
        .channel_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .sample_rate_hz = 25u,
        .raw_values = raw_values,
        .agc_values = agc_values,
        .acceleration = {-7, 8, -9},
        .frame_count = UINT32_C(0x12345678),
    };
    return frame;
}

static void test_provider_composer(void) {
    const uint32_t hr_mask = (uint32_t)1u << R1_GH3X2X_ALGO_FUNCTION_HR;
    const uint32_t hrv_mask = (uint32_t)1u << R1_GH3X2X_ALGO_FUNCTION_HRV;
    const uint32_t spo2_mask =
        (uint32_t)1u << R1_GH3X2X_ALGO_FUNCTION_SPO2;
    const uint32_t all_masks = hr_mask | hrv_mask | spo2_mask;
    const uint32_t raw_values[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        101u, 202u, 303u, 404u, 505u, 606u,
        707u, 808u, 909u, 1001u, 1101u, 1201u,
    };
    const uint32_t agc_values[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        UINT32_C(0x00010203), UINT32_C(0x00040506),
        UINT32_C(0x00070809), UINT32_C(0x000a0b0c),
        UINT32_C(0x000d0e0f), UINT32_C(0x00101112),
        UINT32_C(0x00131415), UINT32_C(0x00161718),
        UINT32_C(0x00191a1b), UINT32_C(0x001c1d1e),
        UINT32_C(0x001f2021), UINT32_C(0x00222324),
    };
    fake_composer_root hr = {
        .initialize_ok = true,
        .deinitialize_ok = true,
        .status = R1_GH3X2X_ROOT_UPDATE,
        .output = {73, 91, 22, 3, 4, 5},
        .version_text = "openr1-hba",
    };
    fake_composer_root hrv = {
        .initialize_ok = true,
        .deinitialize_ok = true,
        .status = R1_GH3X2X_ROOT_UPDATE,
        .output = {800, 810, 820, 830, 88, 4},
        .version_text = "openr1-hrv",
    };
    fake_composer_root spo2 = {
        .initialize_ok = true,
        .deinitialize_ok = true,
        .status = R1_GH3X2X_ROOT_UPDATE,
        .output = {98, 1234, 90, 2, 71, 0},
        .version_text = "openr1-spo2",
    };
    r1_gh3x2x_root_binding hr_binding = fake_composer_binding(&hr);
    r1_gh3x2x_root_binding hrv_binding = fake_composer_binding(&hrv);
    r1_gh3x2x_root_binding spo2_binding = fake_composer_binding(&spo2);
    r1_gh3x2x_provider_composer composer;
    r1_gh3x2x_provider_composer_initialize(&composer);
    r1_gh3x2x_algo_provider provider;

    assert(!r1_gh3x2x_provider_composer_build(&composer, &provider));
    r1_gh3x2x_root_binding incomplete = hr_binding;
    incomplete.process = NULL;
    assert(!r1_gh3x2x_provider_composer_bind_root(
        &composer, R1_GH3X2X_ALGO_FUNCTION_HR, &incomplete));
    assert(!r1_gh3x2x_provider_composer_bind_root(
        &composer, 19u, &hr_binding));
    assert(r1_gh3x2x_provider_composer_bind_root(
        &composer, R1_GH3X2X_ALGO_FUNCTION_HR, &hr_binding));
    assert(r1_gh3x2x_provider_composer_bind_root(
        &composer, R1_GH3X2X_ALGO_FUNCTION_HRV, &hrv_binding));
    assert(r1_gh3x2x_provider_composer_bind_root(
        &composer, R1_GH3X2X_ALGO_FUNCTION_SPO2, &spo2_binding));
    assert(composer.supported_functions == all_masks);
    composer.supported_functions ^= hr_mask;
    assert(!r1_gh3x2x_provider_composer_build(&composer, &provider));
    composer.supported_functions ^= hr_mask;
    assert(r1_gh3x2x_provider_composer_build(&composer, &provider));
    assert(provider.supported_functions == all_masks);

    fake_composer_control control = {.register_ok = true};
    const r1_gh3x2x_provider_control control_binding = {
        .context = &control,
        .sensor_enable = fake_composer_sensor_enable,
        .write_virtual_register = fake_composer_write_register,
    };
    r1_gh3x2x_provider_composer_bind_control(&composer, &control_binding);
    provider.sensor_enable(provider.context, true, false, true);
    assert(control.sensor_calls == 1u && control.accelerometer &&
           !control.capacitive && control.temperature);
    assert(provider.write_virtual_register(
        provider.context, 0x30c0u, 0x0001u));
    assert(control.register_calls == 1u && control.address == 0x30c0u &&
           control.value == 0x0001u);

    r1_gh3x2x_provider_composer_set_mode(&composer, 6u, 2u);
    r1_gh3x2x_algo_frame hr_frame = fake_composer_frame(
        R1_GH3X2X_ALGO_FUNCTION_HR, raw_values, agc_values);
    r1_gh3x2x_algo_frame hrv_frame = fake_composer_frame(
        R1_GH3X2X_ALGO_FUNCTION_HRV, raw_values, agc_values);
    r1_gh3x2x_algo_frame spo2_frame = fake_composer_frame(
        R1_GH3X2X_ALGO_FUNCTION_SPO2, raw_values, agc_values);
    r1_gh3x2x_algo_result result;
    memset(&result, 0x5a, sizeof(result));
    assert(!provider.process(provider.context, &hr_frame, &result));
    assert(provider.initialize(provider.context, &hrv_frame));
    assert(composer.last_hr == 0u);
    assert(provider.initialize(provider.context, &hr_frame));
    assert(!r1_gh3x2x_provider_composer_build(&composer, &provider));
    assert(!provider.initialize(provider.context, &hr_frame));
    assert(hr.initialize_calls == 1u);
    assert(provider.process(provider.context, &hr_frame, &result));
    assert(result.updated && result.value_mask == R1_GH3X2X_HR_RESULT_MASK &&
           result.value_count == 6u && result.values[0] == 73 &&
           result.values[5] == 5 && result.values[6] == 0);
    assert(hr.last_input.scene == 6u && hr.last_input.sleep_flag == 2u &&
           hr.last_input.enable_flags[0] == 0xf0u &&
           hr.last_input.channel_values[0] == 101 &&
           hr.last_input.channel_values[3] == 404 &&
           hr.last_input.channel_values[4] == 0);
    assert(composer.last_hr == 73u);

    assert(provider.process(provider.context, &hrv_frame, &result));
    assert(hrv.last_input.last_hr == 73u &&
           hrv.last_input.channel_values[3] == 404 &&
           hrv.last_input.gain_codes[0] == 3u &&
           hrv.last_input.drive_currents[0] == 3u);
    assert(result.updated && result.value_mask == R1_GH3X2X_HRV_RESULT_MASK &&
           result.value_count == 7u && result.values[0] == 800 &&
           result.values[5] == 4 && result.values[6] == 0);

    assert(provider.initialize(provider.context, &spo2_frame));
    assert(provider.process(provider.context, &spo2_frame, &result));
    assert(spo2.last_input.enable_flags[0] == 0x08u &&
           spo2.last_input.enable_flags[1] == 0x80u &&
           spo2.last_input.channel_values[4] == 202 &&
           spo2.last_input.channel_values[8] == 101 &&
           spo2.last_input.gain_codes[4] == 6u &&
           spo2.last_input.drive_currents[8] == 3u);
    assert(result.updated &&
           result.value_mask == R1_GH3X2X_SPO2_RESULT_MASK &&
           result.value_count == 8u && result.values[0] == 98 &&
           result.values[5] == 0 && result.values[6] == 98 &&
           result.values[7] == 0);

    hrv.status = R1_GH3X2X_ROOT_NO_UPDATE;
    memset(&result, 0x5a, sizeof(result));
    assert(provider.process(provider.context, &hrv_frame, &result));
    assert(!result.updated && result.value_count == 0u &&
           result.value_mask == 0u && result.values[0] == 0);
    hrv.status = R1_GH3X2X_ROOT_UPDATE;

    char version[32];
    assert(provider.version(provider.context,
                            R1_GH3X2X_ALGO_FUNCTION_SPO2,
                            version, sizeof(version)));
    assert(strcmp(version, "openr1-spo2") == 0 && spo2.version_calls == 1u);
    assert(!provider.version(provider.context, 19u,
                             version, sizeof(version)));
    assert(!provider.deinitialize(provider.context, UINT32_MAX, 255u));
    assert(!r1_gh3x2x_provider_composer_bind_root(
        &composer, R1_GH3X2X_ALGO_FUNCTION_HR, &hr_binding));
    assert(provider.deinitialize(provider.context, hr_mask,
                                 R1_GH3X2X_ALGO_FUNCTION_HR));
    assert(composer.last_hr == 73u);
    assert(provider.deinitialize(provider.context, hrv_mask,
                                 R1_GH3X2X_ALGO_FUNCTION_HRV));
    assert(provider.deinitialize(provider.context, spo2_mask,
                                 R1_GH3X2X_ALGO_FUNCTION_SPO2));
    assert(composer.initialized_functions == 0u);
}

/* --- recovered primitive root executors and retail result transforms --- */

typedef struct {
    unsigned int initialize_calls;
    unsigned int deinitialize_calls;
    uint16_t sample_rate_hz;
    bool initialize_ok;
    bool deinitialize_ok;
} fake_reconstructed_lifecycle;

static bool fake_reconstructed_initialize(void *opaque,
                                           uint16_t sample_rate_hz) {
    fake_reconstructed_lifecycle *lifecycle = opaque;
    ++lifecycle->initialize_calls;
    lifecycle->sample_rate_hz = sample_rate_hz;
    return lifecycle->initialize_ok;
}

static bool fake_reconstructed_deinitialize(void *opaque) {
    fake_reconstructed_lifecycle *lifecycle = opaque;
    ++lifecycle->deinitialize_calls;
    return lifecycle->deinitialize_ok;
}

static r1_gh3x2x_root_state_lifecycle fake_reconstructed_binding(
    fake_reconstructed_lifecycle *lifecycle) {
    const r1_gh3x2x_root_state_lifecycle binding = {
        .context = lifecycle,
        .initialize = fake_reconstructed_initialize,
        .deinitialize = fake_reconstructed_deinitialize,
    };
    return binding;
}

static void test_reconstructed_root_executors(void) {
    int32_t public_output[R1_GH3X2X_PUBLIC_RESULT_WORDS] = {0};
    const goodix_primitives_hba_process_output hba_output = {
        .valid = 1u,
        .selected = 77u,
        .reserved = UINT32_C(0xfffffffe),
        .score_at_least_70 = 1u,
        .scaled_score = 555u,
    };
    assert(r1_gh3x2x_format_hba_root_output(
               0u, &hba_output, public_output) ==
           R1_GH3X2X_ROOT_UPDATE);
    assert(public_output[0] == 77 && public_output[1] == 555 &&
           public_output[2] == -200 && public_output[3] == 1 &&
           public_output[4] == 0 && public_output[5] == 0);
    goodix_primitives_hba_process_output hba_no_update = hba_output;
    hba_no_update.valid = 0u;
    assert(r1_gh3x2x_format_hba_root_output(
               0u, &hba_no_update, public_output) ==
           R1_GH3X2X_ROOT_NO_UPDATE);
    assert(r1_gh3x2x_format_hba_root_output(
               1u, &hba_output, public_output) ==
           R1_GH3X2X_ROOT_ERROR);

    uint32_t spo2_words[R1_GH3X2X_ALGO_RESULT_COUNT] = {0u};
    spo2_words[0] = 985000u;
    spo2_words[1] = 3u;
    spo2_words[2] = 2u;
    spo2_words[4] = 4u;
    spo2_words[6] = 6u;
    spo2_words[11] = UINT32_C(0xfffffffc);
    spo2_words[12] = 1u;
    assert(r1_gh3x2x_format_spo2_root_output(
               0, spo2_words, public_output) ==
           R1_GH3X2X_ROOT_UPDATE);
    assert(public_output[0] == 99 && public_output[1] == -4 &&
           public_output[2] == 2 && public_output[3] == 3 &&
           public_output[4] == 4 && public_output[5] == 6);
    spo2_words[0] = UINT32_C(0xfff0f858);
    assert(r1_gh3x2x_format_spo2_root_output(
               4, spo2_words, public_output) ==
           R1_GH3X2X_ROOT_UPDATE);
    assert(public_output[0] == -99);
    spo2_words[12] = 0u;
    assert(r1_gh3x2x_format_spo2_root_output(
               3, spo2_words, public_output) ==
           R1_GH3X2X_ROOT_NO_UPDATE);
    assert(r1_gh3x2x_format_spo2_root_output(
               5, spo2_words, public_output) ==
           R1_GH3X2X_ROOT_ERROR);

    static goodix_primitives_hba_process_configuration hba_configuration;
    static goodix_primitives_hba_process_plan hba_plan;
    static goodix_primitives_hba_process_state hba_state;
    static goodix_primitives_hba_stream_workspace hba_stream_workspace;
    static goodix_primitives_hba_process_workspace hba_workspace;
    static goodix_primitives_hrv_process_plan hrv_plan;
    static goodix_primitives_hrv_process_state hrv_state;
    static goodix_primitives_hrv_process_workspace hrv_workspace;
    static goodix_primitives_nadt_preprocess_plan spo2_plan;
    static goodix_primitives_nadt_preprocess_state spo2_state;
    static goodix_primitives_nadt_preprocess_workspace spo2_workspace;
    static const uint8_t filter_code[1] = {0u};
    fake_reconstructed_lifecycle hba_lifecycle = {
        .initialize_ok = true,
        .deinitialize_ok = true,
    };
    fake_reconstructed_lifecycle hrv_lifecycle = hba_lifecycle;
    fake_reconstructed_lifecycle spo2_lifecycle = hba_lifecycle;
    r1_gh3x2x_hba_root_context hba = {
        .configuration = &hba_configuration,
        .plan = &hba_plan,
        .state = &hba_state,
        .stream_workspace = &hba_stream_workspace,
        .workspace = &hba_workspace,
        .filter_code = filter_code,
        .filter_code_count = 1u,
        .lifecycle = fake_reconstructed_binding(&hba_lifecycle),
    };
    r1_gh3x2x_hrv_root_context hrv = {
        .plan = &hrv_plan,
        .state = &hrv_state,
        .workspace = &hrv_workspace,
        .lifecycle = fake_reconstructed_binding(&hrv_lifecycle),
    };
    r1_gh3x2x_spo2_root_context spo2 = {
        .plan = &spo2_plan,
        .state = &spo2_state,
        .workspace = &spo2_workspace,
        .weights_version = "gh3x2x-v2.23_7ecd2a",
        .lifecycle = fake_reconstructed_binding(&spo2_lifecycle),
    };
    r1_gh3x2x_root_binding hba_binding;
    r1_gh3x2x_root_binding hrv_binding;
    r1_gh3x2x_root_binding spo2_binding;
    assert(r1_gh3x2x_make_hba_root_binding(&hba, &hba_binding));
    assert(r1_gh3x2x_make_hrv_root_binding(&hrv, &hrv_binding));
    assert(r1_gh3x2x_make_spo2_root_binding(&spo2, &spo2_binding));
    assert(hba_binding.process(hba_binding.context, NULL, public_output) ==
           R1_GH3X2X_ROOT_ERROR);

    const uint32_t raw_values[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {0u};
    const uint32_t agc_values[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {0u};
    r1_gh3x2x_algo_frame hba_frame = fake_composer_frame(
        R1_GH3X2X_ALGO_FUNCTION_HR, raw_values, agc_values);
    r1_gh3x2x_algo_frame hrv_frame = fake_composer_frame(
        R1_GH3X2X_ALGO_FUNCTION_HRV, raw_values, agc_values);
    r1_gh3x2x_algo_frame spo2_frame = fake_composer_frame(
        R1_GH3X2X_ALGO_FUNCTION_SPO2, raw_values, agc_values);
    assert(!hba_binding.initialize(hba_binding.context, &hrv_frame));
    assert(hba_lifecycle.initialize_calls == 0u);
    assert(hba_binding.initialize(hba_binding.context, &hba_frame));
    assert(hrv_binding.initialize(hrv_binding.context, &hrv_frame));
    assert(spo2_binding.initialize(spo2_binding.context, &spo2_frame));
    assert(hba_lifecycle.sample_rate_hz == 25u &&
           hrv_lifecycle.sample_rate_hz == 25u &&
           spo2_lifecycle.sample_rate_hz == 25u);
    assert(!r1_gh3x2x_make_hba_root_binding(&hba, &hba_binding));

    char version[128];
    assert(hba_binding.version(
        hba_binding.context, version, sizeof(version)));
    assert(strncmp(version, "GH_HR_exc_pv_v2.0.3.0",
                   strlen("GH_HR_exc_pv_v2.0.3.0")) == 0);
    assert(hrv_binding.version(
        hrv_binding.context, version, sizeof(version)));
    assert(strcmp(version, "GH_HRV_pre_pv_v1.0.1.0_ed953ff3") == 0);
    assert(spo2_binding.version(
        spo2_binding.context, version, sizeof(version)));
    assert(strncmp(version, "GH_SPO2_pre_pv_v2.1.10.0",
                   strlen("GH_SPO2_pre_pv_v2.1.10.0")) == 0);
    assert(hba_binding.deinitialize(hba_binding.context));
    assert(hrv_binding.deinitialize(hrv_binding.context));
    assert(spo2_binding.deinitialize(spo2_binding.context));
    assert(hba_lifecycle.deinitialize_calls == 1u &&
           hrv_lifecycle.deinitialize_calls == 1u &&
           spo2_lifecycle.deinitialize_calls == 1u);

    const goodix_primitives_hrv_configuration reconstructed_configuration = {
        .identity = 0u,
        .sample_count = 0u,
        .calibration = {100000, 10000, 0, 10000},
    };
    r1_gh3x2x_hrv_reconstructed_state reconstructed_state = {
        .configuration = &reconstructed_configuration,
        .allocate = reconstructed_allocate,
        .release = reconstructed_release,
        .square_root = reconstructed_square_root,
    };
    r1_gh3x2x_hrv_root_context reconstructed_root = {0};
    r1_gh3x2x_root_binding reconstructed_binding;
    assert(r1_gh3x2x_make_reconstructed_hrv_root_binding(
        &reconstructed_root, &reconstructed_state,
        &reconstructed_binding));
    assert(reconstructed_binding.initialize(
        reconstructed_binding.context, &hrv_frame));
    assert(reconstructed_state.context != NULL &&
           reconstructed_state.runtime.bound &&
           reconstructed_state.runtime.state.sample_rate == 25u);
    r1_gh3x2x_algo_input reconstructed_input;
    assert(r1_gh3x2x_algo_prepare_hrv_input(
        &hrv_frame, 0u, 0u, &reconstructed_input));
    assert(reconstructed_binding.process(
               reconstructed_binding.context, &reconstructed_input,
               public_output) == R1_GH3X2X_ROOT_UPDATE);
    assert(reconstructed_state.context->process_count == 1u);
    for (size_t index = 0u; index < R1_GH3X2X_PUBLIC_RESULT_WORDS;
            ++index) {
        assert(public_output[index] == 0);
    }
    assert(reconstructed_binding.deinitialize(
        reconstructed_binding.context));
    assert(reconstructed_state.context == NULL &&
           !reconstructed_state.runtime.bound);

    const goodix_primitives_hr_configuration reconstructed_hba_configuration = {
        .algorithm_mode =
            (uint8_t)r1_goodix_hba_configuration_words[0],
        .sample_rate = r1_goodix_hba_configuration_words[1],
        .minimum_batch =
            (int32_t)r1_goodix_hba_configuration_words[2],
        .secondary_window_override =
            r1_goodix_hba_configuration_words[3],
        .primary_window_override =
            r1_goodix_hba_configuration_words[4],
        .feature_stride =
            (int32_t)r1_goodix_hba_configuration_words[5],
        .terminal_default =
            (int32_t)r1_goodix_hba_configuration_words[6],
        .candidate_limit = r1_goodix_hba_configuration_words[7],
        .owner_word = r1_goodix_hba_configuration_words[8],
    };
    const quantized_runtime_providers reconstructed_hba_providers = {
        .fminf_fn = fminf,
        .fmaxf_fn = fmaxf,
        .floorf_fn = floorf,
        .expf_fn = expf,
        .qsort_fn = qsort,
        .vector_95b20 =
            (uintptr_t)&quantized_runtime_float_multiply_execute,
        .vector_36dcc =
            (uintptr_t)&quantized_runtime_float_concatenate_two_execute,
        .vector_30534 =
            (uintptr_t)&quantized_runtime_int8_to_float_execute,
        .vector_35d12 =
            (uintptr_t)&quantized_runtime_float_strided_copy_2d_execute,
        .vector_7ca94 =
            (uintptr_t)&quantized_runtime_float_pool_1d_execute,
    };
    quantized_runtime reconstructed_hba_quantized;
    quantized_runtime_initialize(
        &reconstructed_hba_quantized, &reconstructed_hba_providers);
    uint32_t reconstructed_hba_timestamps[1] = {1u};
    goodix_primitives_elapsed_state reconstructed_hba_elapsed = {
        .slot_timestamps = reconstructed_hba_timestamps,
        .slot_count = 1u,
    };
    goodix_primitives_float_span reconstructed_hba_mode_buffers[3] = {{0}};
    const goodix_primitives_hba_runtime_bindings
        reconstructed_hba_runtime_bindings = {
        .integrity_transform = reconstructed_identity_i32,
        .quantized = &reconstructed_hba_quantized,
        .elapsed_state = &reconstructed_hba_elapsed,
        .mode_buffers = reconstructed_hba_mode_buffers,
        .exponential = expf,
        .logarithm_base_10 = log10f,
        .square_root = sqrtf,
    };
    reconstructed_allocation_trace reconstructed_hba_allocations = {0};
    r1_gh3x2x_hba_reconstructed_state reconstructed_hba_state = {
        .configuration = &reconstructed_hba_configuration,
        .runtime_bindings = &reconstructed_hba_runtime_bindings,
        .allocate = reconstructed_traced_allocate,
        .release = reconstructed_traced_release,
        .provider_context = &reconstructed_hba_allocations,
    };
    static const uint8_t reconstructed_hba_filter_code[1] = {0u};
    r1_gh3x2x_hba_root_context reconstructed_hba_root = {
        .filter_code = reconstructed_hba_filter_code,
        .filter_code_count = sizeof(reconstructed_hba_filter_code),
    };
    r1_gh3x2x_root_binding reconstructed_hba_binding;
    assert(r1_gh3x2x_make_reconstructed_hba_root_binding(
        &reconstructed_hba_root, &reconstructed_hba_state,
        &reconstructed_hba_binding));
    assert(reconstructed_hba_binding.initialize(
        reconstructed_hba_binding.context, &hba_frame));
    assert(reconstructed_hba_state.runtime.bound &&
           reconstructed_hba_state.graph_selector_0_built &&
           reconstructed_hba_state.graph_selector_1_built &&
           reconstructed_hba_state.graph_selector_6_built &&
           reconstructed_hba_allocations.allocations == 37u &&
           reconstructed_hba_allocations.peak_bytes <= 16384u);
    r1_gh3x2x_algo_input reconstructed_hba_input;
    assert(r1_gh3x2x_algo_prepare_hr_input(
        &hba_frame, 0u, &reconstructed_hba_input));
    assert(reconstructed_hba_binding.process(
               reconstructed_hba_binding.context,
               &reconstructed_hba_input, public_output) ==
           R1_GH3X2X_ROOT_NO_UPDATE);
    assert(reconstructed_hba_binding.deinitialize(
        reconstructed_hba_binding.context));
    assert(!reconstructed_hba_state.runtime.bound &&
           reconstructed_hba_allocations.live_bytes == 0u &&
           reconstructed_hba_allocations.releases ==
               reconstructed_hba_allocations.allocations);
}

/* --- bind layer error mapping --- */

static void test_bind_error_mapping(void) {
    const r1_goodix_provider_ops *ops = r1_gh3x2x_bind_provider_ops();
    assert(ops != NULL);
    assert(ops->initialize == r1_gh3x2x_bind_initialize);
    assert(ops->switch_configuration ==
           r1_gh3x2x_bind_switch_configuration);
    assert(ops->start_sampling == r1_gh3x2x_bind_start_sampling);
    assert(ops->stop_sampling == r1_gh3x2x_bind_stop_sampling);

    /* invalid config array index propagates the democode error */
    assert(r1_gh3x2x_bind_switch_configuration(NULL, 0xFFu) != 0);
}

/* --- end-to-end: demo init + start/stop sampling against the fake --- */

static void test_demo_init_and_sampling(void) {
    fake_reset();
    r1_gh3x2x_port_bind_hal(&fake_hal);
    assert(r1_gh3x2x_bind_initialize(NULL) == 0);
    assert(fake.i2c_init_calls == 1u);
    assert(fake.reset_pin_init_calls == 1u);
    assert(fake.reset_ctrl_calls >= 2u); /* hard reset pulse */
    assert(fake.delay_calls > 0u);
    assert(fake.device.regs[FAKE_REG_SCAN_DONE] == 0x0001u);
    /* the stock config array applies real register writes below 0x3000 */
    assert(fake.device.write_calls > 100u);

    /* R1 stock profile masks start the raw-streaming TEST functions */
    assert(r1_gh3x2x_bind_start_sampling(NULL, R1_GOODIX_MASK_STOCK_2000) ==
           0);
    assert(r1_gh3x2x_bind_stop_sampling(NULL, R1_GOODIX_MASK_STOCK_2000) ==
           0);
    assert(r1_gh3x2x_bind_start_sampling(NULL, R1_GOODIX_MASK_STOCK_4000) ==
           0);
    assert(r1_gh3x2x_bind_stop_sampling(NULL, 0xFFFFFFFFu) == 0);

    /* config switch through the bound ops table */
    const r1_goodix_provider_ops *ops = r1_gh3x2x_bind_provider_ops();
    assert(ops->switch_configuration(NULL, 0u) == 0);
    assert(ops->stop_sampling(NULL, 0xFFFFFFFFu) == 0);
}

int main(void) {
    test_port_unbound_fail_closed();
    test_port_hal_forwarding();
    test_pool_glue();
    test_driver_register_translation();
    test_driver_comm_error_mapping();
    test_algorithm_bridge();
    test_recovered_algorithm_inputs();
    test_provider_composer();
    test_reconstructed_root_executors();
    test_bind_error_mapping();
    test_demo_init_and_sampling();
    puts("test_vendor_goodix: all tests passed");
    return 0;
}
