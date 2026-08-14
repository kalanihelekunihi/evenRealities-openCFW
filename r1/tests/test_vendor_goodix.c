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
 *   - fail-closed algorithm/protocol stubs (absent Armv8-M libraries)
 *   - goodix_mem integrator surface (Gh3x2xPoolIsNotEnough glue)
 *   - end-to-end Gh3x2xDemoInit + start/stop sampling against the fake
 */

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "openr1/r1_goodix.h"
#include "r1_gh3x2x_bind.h"
#include "r1_gh3x2x_port.h"

#include "gh_demo.h"
#include "gh_demo_inner.h"
#include "gh3x2x_demo_algo_call.h"
#include "gh_drv_control.h"
#include "gh_drv_interface.h"
#include "gh_uprotocol.h"

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

/* --- fail-closed stubs for the absent algorithm/protocol layer --- */

static void test_algorithm_stubs_fail_closed(void) {
    assert(GH3X2X_AlgoInit(GH3X2X_FUNCTION_HR) == GH3X2X_RET_RESOURCE_ERROR);
    assert(GH3X2X_AlgoCalculate(GH3X2X_FUNCTION_SPO2) ==
           GH3X2X_RET_RESOURCE_ERROR);
    assert(GH3X2X_AlgoDeinit(0xFFFFFFFFu) == GH3X2X_RET_RESOURCE_ERROR);

    GCHAR version[150];
    memset(version, 0x5A, sizeof(version));
    GH3X2X_AlgoVersion(0u, version);
    assert(strcmp(version, "no_ver") == 0);
    memset(version, 0x5A, sizeof(version));
    GH3X2X_GetVersion(0u, version);
    assert(strcmp(version, "no_ver") == 0);

    GH3X2X_AlgoSensorEnable(1u, 0u, 0u);
    GH3X2X_AlgoCallConfigInit(g_pstGh3x2xFrameInfo, 0u);
    GH3X2X_WriteAlgConfigWithVirtualReg(0x30C0u, 0x0001u);

    GH3X2X_TimestampSyncAccInit();
    GH3X2X_TimestampSyncPpgInit(GH3X2X_FUNCTION_HR);
    GH3X2X_TimestampSyncSetPpgIntFlag(1u);
    GH3X2X_TimestampSyncFillAccSyncBuffer(0u, 1, 2, 3);
    GH3X2X_TimestampSyncFillPpgSyncBuffer(0u, g_pstGh3x2xFrameInfo[0]);
    assert(GH3X2X_TimestampSyncGetFrameDataFlag() == 0u);

    GU8 packet[16];
    GU8 payload[4] = {1u, 2u, 3u, 4u};
    assert(GH3X2X_UprotocolPacketFormat(0x01u, packet, payload, 4u) == 0u);
    Gh3x2xDemoSendProtocolData(packet, 0u);
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
    test_algorithm_stubs_fail_closed();
    test_bind_error_mapping();
    test_demo_init_and_sampling();
    puts("test_vendor_goodix: all tests passed");
    return 0;
}
