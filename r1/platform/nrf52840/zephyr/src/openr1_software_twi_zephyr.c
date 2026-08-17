#include "openr1_software_twi_zephyr.h"

#include <errno.h>
#include <stdbool.h>
#include <stdint.h>

#include <hal/nrf_gpio.h>
#include <zephyr/kernel.h>

K_MUTEX_DEFINE(software_twi_mutex);

static bool module_initialized;

static bool supported_pin(uint32_t pin) {
    switch (pin) {
    case NRF_GPIO_PIN_MAP(1, 13): /* i2c_2 / GXT310 SCL */
    case NRF_GPIO_PIN_MAP(0, 28): /* i2c_2 / GXT310 SDA */
    case NRF_GPIO_PIN_MAP(0, 11): /* i2c_3 SCL */
    case NRF_GPIO_PIN_MAP(0, 12): /* i2c_3 SDA */
    case NRF_GPIO_PIN_MAP(1, 9):  /* i2c_4 / Goodix SCL */
    case NRF_GPIO_PIN_MAP(0, 31): /* i2c_4 / Goodix SDA */
    case NRF_GPIO_PIN_MAP(1, 14): /* i2c_5 SCL */
    case NRF_GPIO_PIN_MAP(1, 11): /* i2c_5 SDA */
        return true;
    default:
        return false;
    }
}

static void twi_drive_low(uint32_t pin) {
    if (supported_pin(pin)) {
        nrf_gpio_pin_clear(pin);
    }
}

static void twi_release_high(uint32_t pin) {
    if (supported_pin(pin)) {
        nrf_gpio_pin_set(pin);
    }
}

static void twi_set_output(uint32_t pin) {
    if (supported_pin(pin)) {
        nrf_gpio_cfg_output(pin);
    }
}

static void twi_set_input(uint32_t pin, uint32_t pull) {
    if (supported_pin(pin) && pull <= NRF_GPIO_PIN_PULLUP) {
        nrf_gpio_cfg_input(pin, (nrf_gpio_pin_pull_t)pull);
    }
}

static void twi_delay(uint32_t microseconds) {
    k_busy_wait(microseconds);
}

static uint32_t twi_read_pin(uint32_t pin) {
    return supported_pin(pin) ? nrf_gpio_pin_read(pin) : 0u;
}

static void twi_gpio_configure(uint32_t pin, uint32_t direction,
                               uint32_t input, uint32_t pull,
                               uint32_t drive, uint32_t sense) {
    if (supported_pin(pin)) {
        nrf_gpio_cfg(pin, (nrf_gpio_pin_dir_t)direction,
                     (nrf_gpio_pin_input_t)input,
                     (nrf_gpio_pin_pull_t)pull,
                     (nrf_gpio_pin_drive_t)drive,
                     (nrf_gpio_pin_sense_t)sense);
    }
}

static int map_status(uint32_t status) {
    if (status == SOFTWARE_TWI_STATUS_OK) {
        return 0;
    }
    if (status == SOFTWARE_TWI_STATUS_BAD_ARGUMENT) {
        return -EINVAL;
    }
    if (status == SOFTWARE_TWI_STATUS_READ_NOT_OPEN ||
        status == SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN) {
        return -EACCES;
    }
    return -EIO;
}

static uint32_t bus_open(software_twi_bus_id bus) {
    switch (bus) {
    case SOFTWARE_TWI_BUS_I2C_2:
        return software_twi_i2c_2_open();
    case SOFTWARE_TWI_BUS_I2C_3:
        return software_twi_i2c_3_open();
    case SOFTWARE_TWI_BUS_I2C_4:
        return software_twi_i2c_4_open();
    case SOFTWARE_TWI_BUS_I2C_5:
        return software_twi_i2c_5_open();
    default:
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
}

static uint32_t bus_read(software_twi_bus_id bus,
                         const software_twi_read_request *request) {
    switch (bus) {
    case SOFTWARE_TWI_BUS_I2C_2:
        return software_twi_i2c_2_read(0u, 0u, request);
    case SOFTWARE_TWI_BUS_I2C_3:
        return software_twi_i2c_3_read(0u, 0u, request);
    case SOFTWARE_TWI_BUS_I2C_4:
        return software_twi_i2c_4_read(0u, 0u, request);
    case SOFTWARE_TWI_BUS_I2C_5:
        return software_twi_i2c_5_read(0u, 0u, request);
    default:
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
}

static uint32_t bus_write(software_twi_bus_id bus,
                          const software_twi_write_request *request) {
    switch (bus) {
    case SOFTWARE_TWI_BUS_I2C_2:
        return software_twi_i2c_2_write(0u, 0u, request);
    case SOFTWARE_TWI_BUS_I2C_3:
        return software_twi_i2c_3_write(0u, 0u, request);
    case SOFTWARE_TWI_BUS_I2C_4:
        return software_twi_i2c_4_write(0u, 0u, request);
    case SOFTWARE_TWI_BUS_I2C_5:
        return software_twi_i2c_5_write(0u, 0u, request);
    default:
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
}

int openr1_software_twi_zephyr_initialize(void) {
    static const software_twi_providers providers = {
        .drive_low = twi_drive_low,
        .release_high = twi_release_high,
        .set_output = twi_set_output,
        .set_input = twi_set_input,
        .udelay = twi_delay,
        .read_pin = twi_read_pin,
        .gpio_configure = twi_gpio_configure,
        /* The recovered board supplies external pull-ups. i2c_4 separately
         * applies its exact fixed no-pull configuration during open. */
        .input_pull = NRF_GPIO_PIN_NOPULL,
    };
    if (module_initialized) {
        return -EALREADY;
    }
    software_twi_initialize(&providers);
    module_initialized = true;
    return 0;
}

int openr1_software_twi_zephyr_open(software_twi_bus_id bus) {
    if (!module_initialized || k_is_in_isr()) {
        return -EACCES;
    }
    if (k_mutex_lock(&software_twi_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_status(bus_open(bus));
    (void)k_mutex_unlock(&software_twi_mutex);
    return error;
}

int openr1_software_twi_zephyr_read(
    software_twi_bus_id bus, const software_twi_read_request *request) {
    if (!module_initialized || k_is_in_isr()) {
        return -EACCES;
    }
    if (k_mutex_lock(&software_twi_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_status(bus_read(bus, request));
    (void)k_mutex_unlock(&software_twi_mutex);
    return error;
}

int openr1_software_twi_zephyr_write(
    software_twi_bus_id bus, const software_twi_write_request *request) {
    if (!module_initialized || k_is_in_isr()) {
        return -EACCES;
    }
    if (k_mutex_lock(&software_twi_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_status(bus_write(bus, request));
    (void)k_mutex_unlock(&software_twi_mutex);
    return error;
}

void openr1_software_twi_zephyr_close(software_twi_bus_id bus) {
    if (!module_initialized || k_is_in_isr() ||
        k_mutex_lock(&software_twi_mutex, K_FOREVER) != 0) {
        return;
    }
    software_twi_record *record = software_twi_bus_record(bus);
    if (record != NULL && record->opened != 0u) {
        nrf_gpio_cfg_input(record->engine.scl_pin, NRF_GPIO_PIN_NOPULL);
        nrf_gpio_cfg_input(record->engine.sda_pin, NRF_GPIO_PIN_NOPULL);
        record->opened = 0u;
    }
    (void)k_mutex_unlock(&software_twi_mutex);
}
