#include "openr1_optical_zephyr.h"

#include <errno.h>
#include <stddef.h>
#include <string.h>

#include <hal/nrf_gpio.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "openr1_motion_zephyr.h"
#include "openr1_yhm2710_zephyr.h"
#include "r1_gh3x2x_bind.h"
#include "r1_gh3x2x_port.h"
#include "software_twi/software_twi.h"

/* Public, source-built Goodix democode entry points. The binary algorithm
 * archives are deliberately not linked; r1_gh3x2x_stubs.c keeps their global
 * ABI fail-closed until the recovered typed algorithms have a checked frame
 * adapter. */
void Gh3x2xDemoInterruptProcess(void);
void hal_gh3x2x_int_handler_call_back(void);
const void *goodix_spo2_config_get_instance(void);

#define OPENR1_OPTICAL_NODE DT_NODELABEL(openr1_optical)
#define OPENR1_OPTICAL_SCL_PIN NRF_GPIO_PIN_MAP(1, 9)
#define OPENR1_OPTICAL_SDA_PIN NRF_GPIO_PIN_MAP(0, 31)
#define OPENR1_GOODIX_DEVICE_ID UINT8_C(0x28)
#define OPENR1_GOODIX_COMMAND_BYTES 2u
#define OPENR1_GOODIX_GSENSOR_LIMIT 31u

typedef struct {
    int (*initialize)(void);
    int (*start)(r1_goodix_stock_profile);
    int (*switch_profile)(r1_goodix_switch_selection);
    int (*stop)(void);
    bool (*provider_available)(void);
    bool (*prepared)(void);
    uint32_t (*interrupt_count)(void);
    uint32_t (*raw_frame_count)(void);
    int (*last_error)(void);
    const void *(*spo2_configuration)(void);
} openr1_optical_zephyr_api;

static const struct gpio_dt_spec optical_interrupt =
    GPIO_DT_SPEC_GET(OPENR1_OPTICAL_NODE, optical_interrupt_gpios);
static const struct gpio_dt_spec optical_emitter =
    GPIO_DT_SPEC_GET(OPENR1_OPTICAL_NODE, optical_emitter_gpios);
static const struct gpio_dt_spec optical_reset =
    GPIO_DT_SPEC_GET(OPENR1_OPTICAL_NODE, optical_reset_gpios);

K_MUTEX_DEFINE(optical_bus_mutex);
K_MUTEX_DEFINE(optical_provider_mutex);

static struct gpio_callback optical_interrupt_callback;
static struct k_work optical_interrupt_work;
static r1_goodix_adapter optical_adapter;
static atomic_t optical_interrupts;
static atomic_t raw_frames;
static atomic_t last_error;
static atomic_t worn_state;
static atomic_t interrupt_armed;
static atomic_t board_prepared;
static bool interrupt_callback_installed;
static bool module_initialized;

static bool optical_bus_pin(uint32_t pin) {
    return pin == OPENR1_OPTICAL_SCL_PIN || pin == OPENR1_OPTICAL_SDA_PIN;
}

static void record_error(int error) {
    if (error != 0) {
        atomic_set(&last_error, (atomic_val_t)error);
    }
}

static void zero_bytes(uint8_t *bytes, uint16_t length) {
    if (bytes != NULL) {
        memset(bytes, 0, length);
    }
}

static void twi_drive_low(uint32_t pin) {
    if (optical_bus_pin(pin)) {
        nrf_gpio_pin_clear(pin);
    }
}

static void twi_release_high(uint32_t pin) {
    if (optical_bus_pin(pin)) {
        nrf_gpio_pin_set(pin);
    }
}

static void twi_set_output(uint32_t pin) {
    if (optical_bus_pin(pin)) {
        nrf_gpio_cfg_output(pin);
    }
}

static void twi_set_input(uint32_t pin, uint32_t pull) {
    if (optical_bus_pin(pin) && pull <= NRF_GPIO_PIN_PULLUP) {
        nrf_gpio_cfg_input(pin, (nrf_gpio_pin_pull_t)pull);
    }
}

static void twi_delay(uint32_t microseconds) {
    k_busy_wait(microseconds);
}

static uint32_t twi_read_pin(uint32_t pin) {
    return optical_bus_pin(pin) ? nrf_gpio_pin_read(pin) : 0u;
}

static void twi_gpio_configure(uint32_t pin, uint32_t direction,
                               uint32_t input, uint32_t pull,
                               uint32_t drive, uint32_t sense) {
    if (!optical_bus_pin(pin)) {
        return;
    }
    nrf_gpio_cfg(pin, (nrf_gpio_pin_dir_t)direction,
                 (nrf_gpio_pin_input_t)input,
                 (nrf_gpio_pin_pull_t)pull,
                 (nrf_gpio_pin_drive_t)drive,
                 (nrf_gpio_pin_sense_t)sense);
}

static uint32_t optical_bus_open(void) {
    uint32_t status = SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    if (k_mutex_lock(&optical_bus_mutex, K_FOREVER) == 0) {
        status = software_twi_i2c_4_open();
        (void)k_mutex_unlock(&optical_bus_mutex);
    }
    if (status != SOFTWARE_TWI_STATUS_OK) {
        record_error(-EIO);
    }
    return status;
}

static void optical_i2c_init(void *context) {
    (void)context;
    (void)optical_bus_open();
}

static void optical_i2c_write(void *context, uint8_t device_id,
                              const uint8_t *data, uint16_t length) {
    (void)context;
    if (device_id != OPENR1_GOODIX_DEVICE_ID ||
        (length != 0u && data == NULL)) {
        record_error(-EINVAL);
        return;
    }
    const software_twi_write_request request = {
        .address = device_id,
        .buffer = data,
        .length = length,
    };
    uint32_t status = SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    if (k_mutex_lock(&optical_bus_mutex, K_FOREVER) == 0) {
        status = software_twi_i2c_4_write(0u, 0u, &request);
        (void)k_mutex_unlock(&optical_bus_mutex);
    }
    if (status != SOFTWARE_TWI_STATUS_OK) {
        record_error(-EIO);
    }
}

static void optical_i2c_read(void *context, uint8_t device_id,
                             const uint8_t *command,
                             uint16_t command_length, uint8_t *data,
                             uint16_t data_length) {
    (void)context;
    zero_bytes(data, data_length);
    if (device_id != OPENR1_GOODIX_DEVICE_ID || data == NULL ||
        command == NULL || command_length != OPENR1_GOODIX_COMMAND_BYTES ||
        data_length == 0u) {
        record_error(-EINVAL);
        return;
    }
    const software_twi_read_request request = {
        .address = device_id,
        .register_address =
            (uint16_t)(((uint16_t)command[0] << 8u) | command[1]),
        .buffer = data,
        .length = data_length,
    };
    uint32_t status = SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    if (k_mutex_lock(&optical_bus_mutex, K_FOREVER) == 0) {
        status = software_twi_i2c_4_read(0u, 0u, &request);
        (void)k_mutex_unlock(&optical_bus_mutex);
    }
    if (status != SOFTWARE_TWI_STATUS_OK) {
        zero_bytes(data, data_length);
        record_error(-EIO);
    }
}

static void optical_interrupt_handler(const struct device *port,
                                      struct gpio_callback *callback,
                                      gpio_port_pins_t pins) {
    (void)port;
    (void)callback;
    (void)pins;
    if (atomic_get(&interrupt_armed) == 0) {
        return;
    }
    (void)atomic_inc(&optical_interrupts);
    hal_gh3x2x_int_handler_call_back();
    (void)k_work_submit(&optical_interrupt_work);
}

static void optical_interrupt_process(struct k_work *work) {
    (void)work;
    if (atomic_get(&interrupt_armed) == 0 ||
        atomic_get(&board_prepared) == 0 ||
        k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return;
    }
    if (atomic_get(&interrupt_armed) != 0 &&
        atomic_get(&board_prepared) != 0) {
        Gh3x2xDemoInterruptProcess();
    }
    (void)k_mutex_unlock(&optical_provider_mutex);
}

static void optical_int_pin_init(void *context) {
    (void)context;
    int error = gpio_pin_configure_dt(&optical_interrupt, GPIO_INPUT);
    if (error == 0 && !interrupt_callback_installed) {
        gpio_init_callback(&optical_interrupt_callback,
                           optical_interrupt_handler,
                           BIT(optical_interrupt.pin));
        error = gpio_add_callback(optical_interrupt.port,
                                  &optical_interrupt_callback);
        if (error == 0) {
            interrupt_callback_installed = true;
        }
    }
    if (error == 0) {
        error = gpio_pin_interrupt_configure_dt(
            &optical_interrupt, GPIO_INT_EDGE_TO_ACTIVE);
    }
    if (error == 0) {
        atomic_set(&interrupt_armed, 1);
    } else {
        record_error(error);
    }
}

static void optical_reset_pin_init(void *context) {
    (void)context;
    const int error = gpio_pin_configure_dt(&optical_reset,
                                            GPIO_OUTPUT_INACTIVE);
    record_error(error);
}

static void optical_reset_pin_ctrl(void *context, uint8_t level) {
    (void)context;
    record_error(gpio_pin_set_dt(&optical_reset, level != 0u));
}

static void optical_gsensor_get(void *context,
                                r1_gh3x2x_gsensor_sample *samples,
                                uint16_t *count) {
    (void)context;
    if (samples == NULL || count == NULL ||
        !openr1_motion_zephyr_is_enabled()) {
        return;
    }
    r1_motion_sample motion_samples[OPENR1_GOODIX_GSENSOR_LIMIT];
    size_t sample_count = 0u;
    const int error = openr1_motion_zephyr_read_fifo(
        motion_samples, OPENR1_GOODIX_GSENSOR_LIMIT, &sample_count);
    if (error == 0) {
        for (size_t index = 0u; index < sample_count; ++index) {
            samples[index].x = motion_samples[index].x;
            samples[index].y = motion_samples[index].y;
            samples[index].z = motion_samples[index].z;
        }
        *count = (uint16_t)sample_count;
    } else {
        record_error(error);
    }
}

static void optical_delay_us(void *context, uint32_t microseconds) {
    (void)context;
    k_busy_wait(microseconds);
}

static void optical_rawdata_notify(void *context, const uint32_t *rawdata,
                                   uint32_t count) {
    (void)context;
    if (rawdata != NULL && count != 0u) {
        (void)atomic_inc(&raw_frames);
    }
}

static void optical_wear_notify(void *context, bool worn) {
    (void)context;
    atomic_set(&worn_state, worn ? 1 : 0);
}

static bool optical_board_prepare(void *context) {
    (void)context;
    if (atomic_get(&board_prepared) != 0) {
        return true;
    }
    if (!openr1_yhm2710_zephyr_optical_acquire()) {
        record_error(-EACCES);
        return false;
    }
    int error = gpio_pin_set_dt(&optical_reset, 0);
    if (error == 0) {
        error = gpio_pin_set_dt(&optical_emitter, 1);
    }
    if (error != 0) {
        (void)openr1_yhm2710_zephyr_optical_release();
        record_error(error);
        return false;
    }
    atomic_set(&board_prepared, 1);
    return true;
}

static void optical_board_shutdown(void *context) {
    (void)context;
    atomic_clear(&interrupt_armed);
    if (interrupt_callback_installed) {
        record_error(gpio_pin_interrupt_configure_dt(
            &optical_interrupt, GPIO_INT_DISABLE));
    }
    record_error(gpio_pin_set_dt(&optical_reset, 0));
    record_error(gpio_pin_set_dt(&optical_emitter, 0));
    if (k_mutex_lock(&optical_bus_mutex, K_FOREVER) == 0) {
        software_twi_record *record =
            software_twi_bus_record(SOFTWARE_TWI_BUS_I2C_4);
        if (record != NULL) {
            record->opened = 0u;
        }
        nrf_gpio_cfg_input(OPENR1_OPTICAL_SCL_PIN, NRF_GPIO_PIN_NOPULL);
        nrf_gpio_cfg_input(OPENR1_OPTICAL_SDA_PIN, NRF_GPIO_PIN_NOPULL);
        (void)k_mutex_unlock(&optical_bus_mutex);
    }
    if (atomic_get(&board_prepared) != 0 &&
        !openr1_yhm2710_zephyr_optical_release()) {
        record_error(-EIO);
    }
    atomic_clear(&board_prepared);
}

static void optical_board_delay_ms(void *context, uint32_t milliseconds) {
    (void)context;
    k_msleep(milliseconds);
}

static int map_error(r1_error error) {
    if (error == R1_OK) {
        return 0;
    }
    if (error == R1_ERROR_ARGUMENT) {
        return -EINVAL;
    }
    if (error == R1_ERROR_UNSUPPORTED) {
        return -ENOTSUP;
    }
    return -EIO;
}

int openr1_optical_zephyr_initialize(void) {
    static const software_twi_providers twi_providers = {
        .drive_low = twi_drive_low,
        .release_high = twi_release_high,
        .set_output = twi_set_output,
        .set_input = twi_set_input,
        .udelay = twi_delay,
        .read_pin = twi_read_pin,
        .gpio_configure = twi_gpio_configure,
        /* The recovered i2c_4 open explicitly configures no internal pull;
         * the R1 board supplies the bus pull-up. */
        .input_pull = NRF_GPIO_PIN_NOPULL,
    };
    static const r1_gh3x2x_hal goodix_hal = {
        .context = NULL,
        .i2c_init = optical_i2c_init,
        .i2c_write = optical_i2c_write,
        .i2c_read = optical_i2c_read,
        .int_pin_init = optical_int_pin_init,
        .reset_pin_init = optical_reset_pin_init,
        .reset_pin_ctrl = optical_reset_pin_ctrl,
        .gsensor_get = optical_gsensor_get,
        .delay_us = optical_delay_us,
        .log = NULL,
        .rawdata_notify = optical_rawdata_notify,
        .wear_notify = optical_wear_notify,
    };
    static const r1_goodix_board_ops board_ops = {
        .prepare = optical_board_prepare,
        .shutdown = optical_board_shutdown,
        .delay_ms = optical_board_delay_ms,
    };
    if (module_initialized) {
        return -EALREADY;
    }
    if (!gpio_is_ready_dt(&optical_interrupt) ||
        !gpio_is_ready_dt(&optical_emitter) ||
        !gpio_is_ready_dt(&optical_reset)) {
        return -ENODEV;
    }
    int error = gpio_pin_configure_dt(&optical_emitter,
                                      GPIO_OUTPUT_INACTIVE);
    if (error == 0) {
        error = gpio_pin_configure_dt(&optical_reset,
                                      GPIO_OUTPUT_INACTIVE);
    }
    if (error != 0) {
        return error;
    }
    interrupt_callback_installed = false;
    atomic_clear(&interrupt_armed);
    atomic_clear(&board_prepared);
    atomic_clear(&optical_interrupts);
    atomic_clear(&raw_frames);
    atomic_clear(&last_error);
    atomic_clear(&worn_state);
    k_work_init(&optical_interrupt_work, optical_interrupt_process);
    software_twi_initialize(&twi_providers);
    r1_gh3x2x_port_bind_hal(&goodix_hal);
    r1_goodix_adapter_initialize(&optical_adapter);
    error = map_error(r1_goodix_adapter_bind(
        &optical_adapter, r1_gh3x2x_bind_provider_ops(), NULL,
        &board_ops, NULL));
    if (error != 0) {
        r1_gh3x2x_port_unbind_hal();
        record_error(error);
    } else {
        module_initialized = true;
    }
    return error;
}

int openr1_optical_zephyr_start(r1_goodix_stock_profile profile) {
    if (!module_initialized ||
        !openr1_yhm2710_zephyr_provider_available()) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_start_stock_profile(
        &optical_adapter, profile));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

int openr1_optical_zephyr_switch(r1_goodix_switch_selection profile) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_switch_profile(
        &optical_adapter, profile));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

int openr1_optical_zephyr_stop(void) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_stop_stock_profiles(
        &optical_adapter));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

bool openr1_optical_zephyr_provider_available(void) {
    return module_initialized &&
        openr1_yhm2710_zephyr_provider_available() &&
        r1_goodix_provider_available(&optical_adapter);
}

bool openr1_optical_zephyr_prepared(void) {
    return atomic_get(&board_prepared) != 0;
}

uint32_t openr1_optical_zephyr_interrupt_count(void) {
    return (uint32_t)atomic_get(&optical_interrupts);
}

uint32_t openr1_optical_zephyr_raw_frame_count(void) {
    return (uint32_t)atomic_get(&raw_frames);
}

int openr1_optical_zephyr_last_error(void) {
    return (int)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_optical_zephyr_api optical_zephyr_api = {
    openr1_optical_zephyr_initialize,
    openr1_optical_zephyr_start,
    openr1_optical_zephyr_switch,
    openr1_optical_zephyr_stop,
    openr1_optical_zephyr_provider_available,
    openr1_optical_zephyr_prepared,
    openr1_optical_zephyr_interrupt_count,
    openr1_optical_zephyr_raw_frame_count,
    openr1_optical_zephyr_last_error,
    goodix_spo2_config_get_instance,
};
