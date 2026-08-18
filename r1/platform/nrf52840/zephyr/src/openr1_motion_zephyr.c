#include "openr1_motion_zephyr.h"

#include <errno.h>
#include <limits.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "bma4.h"
#include "bma456w.h"
#include "lis2dw12_reg.h"
#include "openr1_twim1_zephyr.h"
#include "qma6100/qma6100.h"

#define OPENR1_MOTION_NODE DT_NODELABEL(openr1_motion)
#define OPENR1_MOTION_BUS_NODE \
    DT_PHANDLE(OPENR1_MOTION_NODE, motion_bus)
#define OPENR1_MOTION_I2C_ADDRESS UINT8_C(0x18)
#define OPENR1_MOTION_BMA_TRANSFER_BYTES UINT16_C(0x40)
#define OPENR1_MOTION_BMA_FIFO_SETTLE_US UINT32_C(450)
#define OPENR1_MOTION_LIS_RESET_POLL_MS UINT32_C(2)
#define OPENR1_MOTION_LIS_RESET_READS 12u
#define OPENR1_MOTION_LIS_POST_CONFIG_MS UINT32_C(100)
#define OPENR1_MOTION_INITIAL_RATE_HZ UINT16_C(25)
#define OPENR1_MOTION_CORE_CYCLES_PER_US UINT32_C(64)

typedef struct {
    int (*initialize)(void);
    int (*read_fifo)(r1_motion_sample *, size_t, size_t *);
    int (*disable_double_tap)(void);
    r1_motion_variant (*variant)(void);
    bool (*is_enabled)(void);
    uint32_t (*interrupt_count)(void);
} openr1_motion_zephyr_api;

static const struct gpio_dt_spec motion_interrupt =
    GPIO_DT_SPEC_GET(OPENR1_MOTION_NODE, motion_interrupt_gpios);

static struct gpio_callback motion_interrupt_callback;
static atomic_t motion_interrupts;
static r1_motion_adapter motion_adapter;
static struct bma4_dev bma_device;
static qma6100_device qma_device;
static uint8_t bma_address = OPENR1_MOTION_I2C_ADDRESS;
static bool bus_ready;
static bool motion_ready;

K_MUTEX_DEFINE(qma_provider_mutex);

static bool valid_transfer(const uint8_t *bytes, size_t length) {
    return bus_ready && length <= UINT16_MAX &&
           (length == 0u || bytes != NULL);
}

static int32_t motion_bus_read(uint8_t device_address,
                               uint8_t register_address,
                               uint8_t *bytes, size_t length) {
    if (!valid_transfer(bytes, length) || length == 0u) {
        return -1;
    }
    const int error = openr1_twim1_zephyr_write_read(
        OPENR1_TWIM1_ZEPHYR_OWNER_MOTION, device_address,
        &register_address, 1u, bytes, length);
    return error == 0 ? 0 : -1;
}

static int32_t motion_bus_write(uint8_t device_address,
                                uint8_t register_address,
                                const uint8_t *bytes, size_t length) {
    if (!valid_transfer(bytes, length) ||
        length > OPENR1_MOTION_BMA_TRANSFER_BYTES) {
        return -1;
    }
    uint8_t frame[1u + OPENR1_MOTION_BMA_TRANSFER_BYTES];
    frame[0] = register_address;
    if (length != 0u) {
        memcpy(frame + 1u, bytes, length);
    }
    const int error = openr1_twim1_zephyr_write(
        OPENR1_TWIM1_ZEPHYR_OWNER_MOTION, device_address, frame,
        length + 1u);
    return error == 0 ? 0 : -1;
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
    k_busy_wait(period);
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
    k_msleep(milliseconds);
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

static bool qma_bus_read(void *context, uint8_t device_address,
                         uint8_t register_address, uint8_t *bytes,
                         size_t length) {
    (void)context;
    return motion_bus_read(device_address, register_address, bytes, length) == 0;
}

static bool qma_bus_write(void *context, uint8_t device_address,
                          uint8_t register_address, const uint8_t *bytes,
                          size_t length) {
    (void)context;
    return motion_bus_write(device_address, register_address, bytes, length) == 0;
}

static void qma_delay_cycles(void *context, uint32_t cycles) {
    (void)context;
    const uint32_t microseconds =
        cycles / OPENR1_MOTION_CORE_CYCLES_PER_US +
        (cycles % OPENR1_MOTION_CORE_CYCLES_PER_US != 0u ? 1u : 0u);
    k_busy_wait(microseconds);
}

static void qma_lock(void *context) {
    (void)context;
    (void)k_mutex_lock(&qma_provider_mutex, K_FOREVER);
}

static void qma_unlock(void *context) {
    (void)context;
    (void)k_mutex_unlock(&qma_provider_mutex);
}

static r1_error qma_probe(void *context, uint8_t *chip_id) {
    qma6100_device *device = context;
    if (device == NULL || chip_id == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    static const uint8_t addresses[] = {
        QMA6100_ADDRESS_1, QMA6100_ADDRESS_2,
    };
    qma_lock(NULL);
    *chip_id = 0u;
    for (size_t index = 0u; index < sizeof addresses; ++index) {
        device->address = addresses[index];
        *chip_id = qma6100_chip_id(device);
        if (qma6100_identity_accepted(*chip_id)) {
            break;
        }
    }
    qma_unlock(NULL);
    return R1_OK;
}

static r1_error qma_configure(void *context, uint16_t requested_rate_hz) {
    qma6100_device *device = context;
    if (device == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    return qma6100_configure_wrapper(device, requested_rate_hz) != 0u
        ? R1_OK : R1_ERROR_STATE;
}

static r1_error qma_read_fifo(void *context, uint8_t *raw_samples,
                              size_t maximum_samples,
                              size_t *sample_count) {
    qma6100_device *device = context;
    if (device == NULL || raw_samples == NULL || maximum_samples == 0u ||
        sample_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    qma_lock(NULL);
    const uint32_t count = qma6100_read_fifo(
        device, raw_samples, maximum_samples);
    qma_unlock(NULL);
    if (count == QMA6100_FIFO_ERROR) {
        *sample_count = 0u;
        return R1_ERROR_STATE;
    }
    *sample_count = (size_t)count;
    return R1_OK;
}

static r1_error qma_disable_double_tap(void *context) {
    qma6100_device *device = context;
    if (device == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    qma_lock(NULL);
    const uint32_t status = qma6100_tap_configure(
        device, UINT8_C(0x31), UINT8_C(0), false);
    qma_unlock(NULL);
    return status != 0u ? R1_OK : R1_ERROR_STATE;
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

static const r1_motion_provider_ops qma_provider = {
    qma_probe,
    qma_configure,
    qma_read_fifo,
    qma_disable_double_tap,
};

static void qma_interrupt_worker(struct k_work *work) {
    (void)work;
    if (motion_ready &&
        r1_motion_adapter_selected(&motion_adapter) ==
            R1_MOTION_VARIANT_QMA6100) {
        qma6100_interrupt_wrapper(&qma_device);
    }
}

K_WORK_DEFINE(qma_interrupt_work, qma_interrupt_worker);

static int map_error(r1_error error) {
    if (error == R1_OK) {
        return 0;
    }
    if (error == R1_ERROR_ARGUMENT) {
        return -EINVAL;
    }
    if (error == R1_ERROR_CAPACITY || error == R1_ERROR_LENGTH) {
        return -ENOSPC;
    }
    if (error == R1_ERROR_UNSUPPORTED) {
        return -ENOTSUP;
    }
    return -EIO;
}

static void motion_interrupt_handler(const struct device *port,
                                     struct gpio_callback *callback,
                                     gpio_port_pins_t pins) {
    (void)port;
    (void)callback;
    (void)pins;
    (void)atomic_inc(&motion_interrupts);
    (void)k_work_submit(&qma_interrupt_work);
}

static int initialize_interrupt(void) {
    if (!gpio_is_ready_dt(&motion_interrupt)) {
        return -ENODEV;
    }
    int error = gpio_pin_configure_dt(&motion_interrupt, GPIO_INPUT);
    if (error != 0) {
        return error;
    }
    gpio_init_callback(&motion_interrupt_callback, motion_interrupt_handler,
                       BIT(motion_interrupt.pin));
    error = gpio_add_callback(
        motion_interrupt.port, &motion_interrupt_callback);
    if (error != 0) {
        return error;
    }
    return gpio_pin_interrupt_configure_dt(
        &motion_interrupt, GPIO_INT_EDGE_TO_ACTIVE);
}

int openr1_motion_zephyr_initialize(void) {
    if (motion_ready) {
        return -EALREADY;
    }
    int error = openr1_twim1_zephyr_initialize();
    if (error != 0 && error != -EALREADY) {
        return error;
    }
    bus_ready = true;
    error = initialize_interrupt();
    if (error != 0) {
        bus_ready = false;
        return error;
    }
    atomic_clear(&motion_interrupts);
    static const qma6100_bindings qma_bindings = {
        qma_bus_read,
        qma_bus_write,
        qma_delay_cycles,
        NULL,
        qma_lock,
        qma_unlock,
        NULL,
    };
    qma6100_initialize(&qma_device, &qma_bindings);
    r1_motion_adapter_initialize(&motion_adapter);
    r1_error motion_error = r1_motion_adapter_bind(
        &motion_adapter, R1_MOTION_VARIANT_LIS2DW12, &lis_provider, NULL);
    if (motion_error == R1_OK) {
        motion_error = r1_motion_adapter_bind(
            &motion_adapter, R1_MOTION_VARIANT_BMA456W, &bma_provider, NULL);
    }
    if (motion_error == R1_OK) {
        motion_error = r1_motion_adapter_bind(
            &motion_adapter, R1_MOTION_VARIANT_QMA6100,
            &qma_provider, &qma_device);
    }
    if (motion_error == R1_OK) {
        motion_error = r1_motion_adapter_configure(
            &motion_adapter, R1_MOTION_POLICY_AUTO_LICENSED,
            OPENR1_MOTION_INITIAL_RATE_HZ);
    }
    error = map_error(motion_error);
    if (error != 0) {
        bus_ready = false;
        return error;
    }
    motion_ready = true;
    return 0;
}

int openr1_motion_zephyr_read_fifo(r1_motion_sample *samples,
                                   size_t capacity,
                                   size_t *sample_count) {
    if (!motion_ready) {
        return -EACCES;
    }
    return map_error(r1_motion_adapter_read_fifo(
        &motion_adapter, samples, capacity, sample_count));
}

int openr1_motion_zephyr_disable_double_tap(void) {
    if (!motion_ready) {
        return -EACCES;
    }
    return map_error(r1_motion_adapter_disable_double_tap(&motion_adapter));
}

r1_motion_variant openr1_motion_zephyr_variant(void) {
    return r1_motion_adapter_selected(&motion_adapter);
}

bool openr1_motion_zephyr_is_enabled(void) {
    return motion_ready && motion_adapter.configured;
}

uint32_t openr1_motion_zephyr_interrupt_count(void) {
    return (uint32_t)atomic_get(&motion_interrupts);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_motion_zephyr_api motion_zephyr_api = {
    openr1_motion_zephyr_initialize,
    openr1_motion_zephyr_read_fifo,
    openr1_motion_zephyr_disable_double_tap,
    openr1_motion_zephyr_variant,
    openr1_motion_zephyr_is_enabled,
    openr1_motion_zephyr_interrupt_count,
};
