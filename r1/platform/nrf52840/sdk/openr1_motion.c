#include "openr1_motion.h"

#include "openr1_twim1_arbiter.h"

#include <limits.h>
#include <string.h>

#include "FreeRTOS.h"
#include "bma4.h"
#include "bma456w.h"
#include "cmsis_os2.h"
#include "lis2dw12_reg.h"
#include "nrf_delay.h"
#include "nrf_gpio.h"
#include "nrfx_gpiote.h"
#include "nrfx_twim.h"
#include "task.h"

#define OPENR1_MOTION_SCL_PIN NRF_GPIO_PIN_MAP(0, 11)
#define OPENR1_MOTION_SDA_PIN NRF_GPIO_PIN_MAP(0, 14)
#define OPENR1_MOTION_INTERRUPT_PIN NRF_GPIO_PIN_MAP(0, 15)
#define OPENR1_MOTION_I2C_ADDRESS UINT8_C(0x18)
#define OPENR1_MOTION_TWIM_PRIORITY 2u
#define OPENR1_MOTION_BMA_TRANSFER_BYTES UINT16_C(0x40)
#define OPENR1_MOTION_BMA_FIFO_SETTLE_US UINT32_C(450)
#define OPENR1_MOTION_LIS_RESET_POLL_MS UINT32_C(2)
#define OPENR1_MOTION_LIS_RESET_READS 12u
#define OPENR1_MOTION_LIS_POST_CONFIG_MS UINT32_C(100)
#define OPENR1_MOTION_INITIAL_RATE_HZ UINT16_C(25)
#define OPENR1_MOTION_FLAG_INTERRUPT UINT32_C(0x01)

#if OPENR1_MOTION_POLICY < OPENR1_MOTION_POLICY_DISABLED || \
    OPENR1_MOTION_POLICY > OPENR1_MOTION_POLICY_FORCE_BMA456W
#error "OPENR1_MOTION_POLICY is outside the supported motion policy range"
#endif

/*
 * The TWIM1 hardware instance is owned by openr1_twim1_arbiter; this client
 * only keeps its recovered pin/frequency/priority configuration and passes it
 * to the arbiter on acquisition. See the arbiter header for the dock/worn
 * handoff contract.
 */
static const nrfx_twim_config_t motion_bus_configuration = {
    .scl = OPENR1_MOTION_SCL_PIN,
    .sda = OPENR1_MOTION_SDA_PIN,
    .frequency = NRF_TWIM_FREQ_400K,
    .interrupt_priority = OPENR1_MOTION_TWIM_PRIORITY,
    .hold_bus_uninit = false,
};
static osMutexId_t motion_mutex;
static StaticSemaphore_t motion_mutex_control_block;
static osThreadId_t motion_thread;
static StaticTask_t motion_control_block;
static StackType_t motion_stack[configMINIMAL_STACK_SIZE];
static r1_motion_adapter motion_adapter;
static struct bma4_dev bma_device;
static uint8_t bma_address = OPENR1_MOTION_I2C_ADDRESS;
static bool bus_initialized;
static bool module_initialized;

static bool lock_bus(void) {
    return motion_mutex != NULL &&
           osMutexAcquire(motion_mutex, osWaitForever) == osOK;
}

static void unlock_bus(void) {
    if (motion_mutex != NULL) {
        (void)osMutexRelease(motion_mutex);
    }
}

static bool valid_transfer(const uint8_t *bytes, size_t length) {
    return bus_initialized && length <= UINT16_MAX &&
           (length == 0u || bytes != NULL);
}

static int32_t motion_bus_read(uint8_t device_address,
                               uint8_t register_address,
                               uint8_t *bytes, size_t length) {
    if (!valid_transfer(bytes, length) || length == 0u || !lock_bus()) {
        return -1;
    }
    nrfx_err_t error = openr1_twim1_acquire(
        OPENR1_TWIM1_CLIENT_MOTION, &motion_bus_configuration);
    if (error == NRFX_SUCCESS) {
        error = openr1_twim1_tx(OPENR1_TWIM1_CLIENT_MOTION, device_address,
                                &register_address, 1u, true);
    }
    if (error == NRFX_SUCCESS) {
        error = openr1_twim1_rx(OPENR1_TWIM1_CLIENT_MOTION, device_address,
                                bytes, length);
    }
    unlock_bus();
    return error == NRFX_SUCCESS ? 0 : -1;
}

static int32_t motion_bus_write(uint8_t device_address,
                                uint8_t register_address,
                                const uint8_t *bytes, size_t length) {
    if (!valid_transfer(bytes, length) ||
        length > OPENR1_MOTION_BMA_TRANSFER_BYTES || !lock_bus()) {
        return -1;
    }
    uint8_t frame[1u + OPENR1_MOTION_BMA_TRANSFER_BYTES];
    frame[0] = register_address;
    if (length != 0u) {
        memcpy(frame + 1u, bytes, length);
    }
    nrfx_err_t error = openr1_twim1_acquire(
        OPENR1_TWIM1_CLIENT_MOTION, &motion_bus_configuration);
    if (error == NRFX_SUCCESS) {
        error = openr1_twim1_tx(OPENR1_TWIM1_CLIENT_MOTION, device_address,
                                frame, length + 1u, false);
    }
    unlock_bus();
    return error == NRFX_SUCCESS ? 0 : -1;
}

static BMA4_INTF_RET_TYPE bma_bus_read(uint8_t register_address,
                                       uint8_t *bytes, uint32_t length,
                                       void *interface_pointer) {
    if (interface_pointer == NULL) {
        return (BMA4_INTF_RET_TYPE)-2;
    }
    const uint8_t address = *(const uint8_t *)interface_pointer;
    return motion_bus_read(address, register_address, bytes, (size_t)length) == 0
        ? BMA4_INTF_RET_SUCCESS : (BMA4_INTF_RET_TYPE)-2;
}

static BMA4_INTF_RET_TYPE bma_bus_write(uint8_t register_address,
                                        const uint8_t *bytes,
                                        uint32_t length,
                                        void *interface_pointer) {
    if (interface_pointer == NULL) {
        return (BMA4_INTF_RET_TYPE)-2;
    }
    const uint8_t address = *(const uint8_t *)interface_pointer;
    return motion_bus_write(address, register_address, bytes, (size_t)length) == 0
        ? BMA4_INTF_RET_SUCCESS : (BMA4_INTF_RET_TYPE)-2;
}

static void bma_delay_us(uint32_t period, void *interface_pointer) {
    (void)interface_pointer;
    nrf_delay_us(period);
}

static void bma_context_initialize(void) {
    memset(&bma_device, 0, sizeof bma_device);
    bma_address = OPENR1_MOTION_I2C_ADDRESS;
    bma_device.intf_ptr = &bma_address;
    bma_device.intf = BMA4_I2C_INTF;
    bma_device.variant = BMA45X_VARIANT;
    bma_device.read_write_len = OPENR1_MOTION_BMA_TRANSFER_BYTES;
    bma_device.bus_read = bma_bus_read;
    bma_device.bus_write = bma_bus_write;
    bma_device.delay_us = bma_delay_us;
    bma_device.perf_mode_status = 0u;
}

static r1_error bma_probe(void *context, uint8_t *chip_id) {
    (void)context;
    if (chip_id == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    bma_context_initialize();
    *chip_id = 0u;
    return bma4_read_regs(BMA4_CHIP_ID_ADDR, chip_id, 1u, &bma_device) == BMA4_OK
        ? R1_OK : R1_ERROR_STATE;
}

static uint8_t bma_rate(uint16_t requested_rate_hz) {
    if (requested_rate_hz == 50u) {
        return BMA4_OUTPUT_DATA_RATE_50HZ;
    }
    if (requested_rate_hz == 100u) {
        return BMA4_OUTPUT_DATA_RATE_100HZ;
    }
    if (requested_rate_hz == 200u) {
        return BMA4_OUTPUT_DATA_RATE_200HZ;
    }
    return BMA4_OUTPUT_DATA_RATE_25HZ;
}

static r1_error bma_configure(void *context, uint16_t requested_rate_hz) {
    (void)context;
    struct bma4_accel_config configuration = {
        .odr = bma_rate(requested_rate_hz),
        .bandwidth = 0u,
        .perf_mode = 0u,
        .range = BMA4_ACCEL_RANGE_8G,
    };
    int8_t status = bma456w_init(&bma_device);
    if (status == BMA4_OK) {
        status = bma4_set_accel_config(&configuration, &bma_device);
    }
    if (status == BMA4_OK) {
        status = bma4_set_accel_enable(BMA4_ENABLE, &bma_device);
    }
    if (status == BMA4_OK) {
        status = bma4_set_advance_power_save(BMA4_DISABLE, &bma_device);
    }
    if (status == BMA4_OK) {
        status = bma4_set_fifo_config(BMA4_FIFO_ALL, BMA4_DISABLE,
                                      &bma_device);
    }
    if (status == BMA4_OK) {
        status = bma4_set_fifo_config(BMA4_FIFO_ACCEL, BMA4_ENABLE,
                                      &bma_device);
    }
    if (status == BMA4_OK) {
        status = bma4_set_fifo_config(BMA4_FIFO_HEADER, BMA4_DISABLE,
                                      &bma_device);
    }
    if (status == BMA4_OK) {
        status = bma4_set_advance_power_save(BMA4_ENABLE, &bma_device);
    }
    return status == BMA4_OK ? R1_OK : R1_ERROR_STATE;
}

static r1_error bma_read_fifo(void *context, uint8_t *raw_samples,
                              size_t maximum_samples,
                              size_t *sample_count) {
    (void)context;
    if (raw_samples == NULL || maximum_samples == 0u || sample_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *sample_count = 0u;
    int8_t status = bma4_set_advance_power_save(BMA4_DISABLE, &bma_device);
    if (status != BMA4_OK) {
        return R1_ERROR_STATE;
    }
    bma_delay_us(OPENR1_MOTION_BMA_FIFO_SETTLE_US, bma_device.intf_ptr);
    uint16_t fifo_bytes = 0u;
    status = bma4_get_fifo_length(&fifo_bytes, &bma_device);
    size_t bounded_bytes = fifo_bytes;
    const size_t capacity_bytes = maximum_samples * R1_MOTION_SAMPLE_BYTES;
    if (bounded_bytes > capacity_bytes) {
        bounded_bytes = capacity_bytes;
    }
    bounded_bytes -= bounded_bytes % R1_MOTION_SAMPLE_BYTES;
    if (status == BMA4_OK && bounded_bytes != 0u) {
        status = bma_device.bus_read(BMA4_FIFO_DATA_ADDR, raw_samples,
                                     (uint32_t)bounded_bytes,
                                     bma_device.intf_ptr);
    }
    const int8_t power_status =
        bma4_set_advance_power_save(BMA4_ENABLE, &bma_device);
    if (status != BMA4_OK || power_status != BMA4_OK) {
        return R1_ERROR_STATE;
    }
    *sample_count = bounded_bytes / R1_MOTION_SAMPLE_BYTES;
    return R1_OK;
}

static int32_t lis_bus_read(void *handle, uint8_t register_address,
                            uint8_t *bytes, uint16_t length) {
    (void)handle;
    return motion_bus_read(OPENR1_MOTION_I2C_ADDRESS, register_address,
                           bytes, length);
}

static int32_t lis_bus_write(void *handle, uint8_t register_address,
                             const uint8_t *bytes, uint16_t length) {
    (void)handle;
    return motion_bus_write(OPENR1_MOTION_I2C_ADDRESS, register_address,
                            bytes, length);
}

static void lis_delay_ms(uint32_t milliseconds) {
    nrf_delay_ms(milliseconds);
}

static stmdev_ctx_t lis_context = {
    .write_reg = lis_bus_write,
    .read_reg = lis_bus_read,
    .mdelay = lis_delay_ms,
    .handle = NULL,
    .priv_data = NULL,
};

static r1_error lis_probe(void *context, uint8_t *chip_id) {
    (void)context;
    if (chip_id == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *chip_id = 0u;
    return lis2dw12_device_id_get(&lis_context, chip_id) == 0
        ? R1_OK : R1_ERROR_STATE;
}

static lis2dw12_odr_t lis_rate(uint16_t requested_rate_hz) {
    if (requested_rate_hz == 50u) {
        return LIS2DW12_XL_ODR_50Hz;
    }
    if (requested_rate_hz == 100u) {
        return LIS2DW12_XL_ODR_100Hz;
    }
    if (requested_rate_hz == 150u || requested_rate_hz == 200u) {
        return LIS2DW12_XL_ODR_200Hz;
    }
    return LIS2DW12_XL_ODR_25Hz;
}

static r1_error lis_read_fifo(void *context, uint8_t *raw_samples,
                              size_t maximum_samples,
                              size_t *sample_count) {
    (void)context;
    if (raw_samples == NULL || maximum_samples == 0u || sample_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *sample_count = 0u;
    uint8_t fifo_samples = 0u;
    if (lis2dw12_fifo_data_level_get(&lis_context, &fifo_samples) != 0) {
        return R1_ERROR_STATE;
    }
    size_t count = fifo_samples;
    if (count > maximum_samples) {
        count = maximum_samples;
    }
    if (count != 0u &&
        lis2dw12_read_reg(&lis_context, LIS2DW12_OUT_X_L, raw_samples,
                          (uint16_t)(count * R1_MOTION_SAMPLE_BYTES)) != 0) {
        return R1_ERROR_STATE;
    }
    *sample_count = count;
    return R1_OK;
}

static r1_error lis_configure(void *context, uint16_t requested_rate_hz) {
    (void)context;
    uint8_t chip_id = 0u;
    if (lis2dw12_device_id_get(&lis_context, &chip_id) != 0 ||
        chip_id != LIS2DW12_ID || lis2dw12_reset_set(&lis_context, 1u) != 0) {
        return R1_ERROR_STATE;
    }
    uint8_t resetting = 1u;
    size_t reads = 0u;
    while (resetting != 0u && reads < OPENR1_MOTION_LIS_RESET_READS) {
        if (lis2dw12_reset_get(&lis_context, &resetting) != 0) {
            return R1_ERROR_STATE;
        }
        lis_delay_ms(OPENR1_MOTION_LIS_RESET_POLL_MS);
        ++reads;
    }
    if (resetting != 0u ||
        lis2dw12_auto_increment_set(&lis_context, 1u) != 0 ||
        lis2dw12_block_data_update_set(&lis_context, 1u) != 0 ||
        lis2dw12_filter_bandwidth_set(&lis_context,
                                      LIS2DW12_ODR_DIV_10) != 0 ||
        lis2dw12_filter_path_set(&lis_context, LIS2DW12_LPF_ON_OUT) != 0 ||
        lis2dw12_full_scale_set(&lis_context, LIS2DW12_4g) != 0 ||
        lis2dw12_fifo_watermark_set(&lis_context, 31u) != 0 ||
        lis2dw12_fifo_mode_set(&lis_context, LIS2DW12_STREAM_MODE) != 0 ||
        lis2dw12_power_mode_set(&lis_context,
                                LIS2DW12_SINGLE_LOW_PWR_3) != 0 ||
        lis2dw12_data_rate_set(&lis_context,
                               lis_rate(requested_rate_hz)) != 0) {
        return R1_ERROR_STATE;
    }
    lis_delay_ms(OPENR1_MOTION_LIS_POST_CONFIG_MS);
    uint8_t discarded[R1_MOTION_SAMPLE_BYTES * 5u];
    size_t discarded_count = 0u;
    return lis_read_fifo(NULL, discarded, 5u, &discarded_count);
}

static r1_error lis_disable_double_tap(void *context) {
    (void)context;
    lis2dw12_ctrl4_int1_pad_ctrl_t route;
    memset(&route, 0, sizeof route);
    if (lis2dw12_pin_int1_route_get(&lis_context, &route) != 0) {
        return R1_ERROR_STATE;
    }
    route.int1_tap = 0u;
    if (lis2dw12_pin_int1_route_set(&lis_context, &route) != 0 ||
        lis2dw12_tap_detection_on_x_set(&lis_context, 0u) != 0 ||
        lis2dw12_tap_detection_on_y_set(&lis_context, 0u) != 0 ||
        lis2dw12_tap_detection_on_z_set(&lis_context, 0u) != 0 ||
        lis2dw12_tap_mode_set(&lis_context, LIS2DW12_ONLY_SINGLE) != 0 ||
        lis2dw12_filter_bandwidth_set(&lis_context,
                                      LIS2DW12_ODR_DIV_10) != 0 ||
        lis2dw12_data_rate_set(&lis_context, LIS2DW12_XL_ODR_25Hz) != 0) {
        return R1_ERROR_STATE;
    }
    return R1_OK;
}

static const r1_motion_provider_ops bma_provider = {
    bma_probe,
    bma_configure,
    bma_read_fifo,
    NULL,
};

static const r1_motion_provider_ops lis_provider = {
    lis_probe,
    lis_configure,
    lis_read_fifo,
    lis_disable_double_tap,
};

static ret_code_t map_error(r1_error error) {
    if (error == R1_OK) {
        return NRF_SUCCESS;
    }
    if (error == R1_ERROR_ARGUMENT) {
        return NRF_ERROR_INVALID_PARAM;
    }
    if (error == R1_ERROR_CAPACITY || error == R1_ERROR_LENGTH) {
        return NRF_ERROR_DATA_SIZE;
    }
    if (error == R1_ERROR_UNSUPPORTED) {
        return NRF_ERROR_NOT_SUPPORTED;
    }
    return NRF_ERROR_INVALID_STATE;
}

/*
 * Interrupt context does the minimum: record the event for the deferred
 * worker.  Recovered r1_motion_interrupt_input_lookup (0x00050128) resolves
 * the P0.15 rising-edge record; nothing else belongs in the handler.
 */
static void motion_interrupt(nrfx_gpiote_pin_t pin,
                             nrf_gpiote_polarity_t action) {
    (void)pin;
    (void)action;
    if (motion_thread != NULL) {
        (void)osThreadFlagsSet(motion_thread, OPENR1_MOTION_FLAG_INTERRUPT);
    }
}

/*
 * Recovered r1_motion_selected_interrupt_dispatch (0x00050294) routes the
 * deferred interrupt to the selected provider's hook.  Both admitted hooks
 * are recovered two-byte no-ops and only the withheld QMA6100 variant has
 * real interrupt behavior, so every admitted dispatch performs no work.
 */
static void selected_interrupt_dispatch(void) {
    switch (r1_motion_adapter_selected(&motion_adapter)) {
    case R1_MOTION_VARIANT_LIS2DW12:
        /* Recovered LIS2DW12 hook at 0x0006F3B2: two-byte no-op. */
        break;
    case R1_MOTION_VARIANT_BMA456W:
        /* Recovered BMA456W hook at 0x0006F1DA: two-byte no-op. */
        break;
    default:
        /* No provider selected: nothing to route to. */
        break;
    }
}

static void motion_worker(void *context) {
    (void)context;
    for (;;) {
        const uint32_t flags = osThreadFlagsWait(
            OPENR1_MOTION_FLAG_INTERRUPT, osFlagsWaitAny, osWaitForever);
        if ((flags & osFlagsError) != 0u) {
            continue;
        }
        if ((flags & OPENR1_MOTION_FLAG_INTERRUPT) != 0u) {
            selected_interrupt_dispatch();
        }
    }
}

static ret_code_t initialize_interrupt(void) {
    if (!nrfx_gpiote_is_init() && nrfx_gpiote_init() != NRFX_SUCCESS) {
        return NRF_ERROR_INTERNAL;
    }
    const nrfx_gpiote_in_config_t configuration =
        NRFX_GPIOTE_CONFIG_IN_SENSE_LOTOHI(false);
    const nrfx_err_t error = nrfx_gpiote_in_init(
        OPENR1_MOTION_INTERRUPT_PIN, &configuration, motion_interrupt);
    if (error != NRFX_SUCCESS) {
        return (ret_code_t)error;
    }
    nrfx_gpiote_in_event_enable(OPENR1_MOTION_INTERRUPT_PIN, true);
    return NRF_SUCCESS;
}

static ret_code_t initialize_bus(void) {
    static const osMutexAttr_t attributes = {
        .name = "openr1_motion",
        .cb_mem = &motion_mutex_control_block,
        .cb_size = sizeof motion_mutex_control_block,
    };
    motion_mutex = osMutexNew(&attributes);
    if (motion_mutex == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    const nrfx_err_t error = openr1_twim1_acquire(
        OPENR1_TWIM1_CLIENT_MOTION, &motion_bus_configuration);
    if (error != NRFX_SUCCESS) {
        return (ret_code_t)error;
    }
    bus_initialized = true;
    return initialize_interrupt();
}

ret_code_t openr1_motion_initialize(void) {
    if (module_initialized) {
        return NRF_ERROR_INVALID_STATE;
    }
    r1_motion_adapter_initialize(&motion_adapter);
#if OPENR1_MOTION_POLICY == OPENR1_MOTION_POLICY_DISABLED
    module_initialized = true;
    return NRF_SUCCESS;
#else
    static const osThreadAttr_t thread_attributes = {
        .name = "motion",
        .cb_mem = &motion_control_block,
        .cb_size = sizeof motion_control_block,
        .stack_mem = motion_stack,
        .stack_size = sizeof motion_stack,
    };
    motion_thread = osThreadNew(motion_worker, NULL, &thread_attributes);
    if (motion_thread == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    ret_code_t error = initialize_bus();
    if (error != NRF_SUCCESS) {
        return error;
    }
    r1_error motion_error = r1_motion_adapter_bind(
        &motion_adapter, R1_MOTION_VARIANT_LIS2DW12, &lis_provider, NULL);
    if (motion_error == R1_OK) {
        motion_error = r1_motion_adapter_bind(
            &motion_adapter, R1_MOTION_VARIANT_BMA456W, &bma_provider, NULL);
    }
    if (motion_error == R1_OK) {
        motion_error = r1_motion_adapter_configure(
            &motion_adapter, (r1_motion_policy)OPENR1_MOTION_POLICY,
            OPENR1_MOTION_INITIAL_RATE_HZ);
    }
    error = map_error(motion_error);
    if (error != NRF_SUCCESS) {
        (void)openr1_twim1_release(OPENR1_TWIM1_CLIENT_MOTION);
        bus_initialized = false;
        return error;
    }
    module_initialized = true;
    return NRF_SUCCESS;
#endif
}

ret_code_t openr1_motion_read_fifo(r1_motion_sample *samples,
                                   size_t capacity,
                                   size_t *sample_count) {
    if (!module_initialized) {
        return NRF_ERROR_INVALID_STATE;
    }
    return map_error(r1_motion_adapter_read_fifo(
        &motion_adapter, samples, capacity, sample_count));
}

ret_code_t openr1_motion_disable_double_tap(void) {
    if (!module_initialized) {
        return NRF_ERROR_INVALID_STATE;
    }
    return map_error(r1_motion_adapter_disable_double_tap(&motion_adapter));
}

r1_motion_variant openr1_motion_variant(void) {
    return r1_motion_adapter_selected(&motion_adapter);
}

bool openr1_motion_is_enabled(void) {
    return module_initialized && motion_adapter.configured;
}

const openr1_motion_api openr1_motion
    __attribute__((used, section(".openr1_motion_api"))) = {
        openr1_motion_initialize,
        openr1_motion_read_fifo,
        openr1_motion_disable_double_tap,
        openr1_motion_variant,
        openr1_motion_is_enabled,
    };
