#include "openr1_twim1_zephyr.h"

#include <errno.h>

#include <hal/nrf_gpio.h>
#include <hal/nrf_twim.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/kernel.h>

#define OPENR1_TWIM1_NODE DT_NODELABEL(i2c1)
#define OPENR1_MOTION_SCL_PIN NRF_GPIO_PIN_MAP(0, 11)
#define OPENR1_MOTION_SDA_PIN NRF_GPIO_PIN_MAP(0, 14)
#define OPENR1_NFC_SCL_PIN NRF_GPIO_PIN_MAP(1, 11)
#define OPENR1_NFC_SDA_PIN NRF_GPIO_PIN_MAP(1, 14)

typedef struct {
    int (*initialize)(void);
    int (*acquire)(openr1_twim1_zephyr_owner);
    int (*release)(openr1_twim1_zephyr_owner);
    openr1_twim1_zephyr_owner (*current_owner)(void);
} openr1_twim1_zephyr_api;

static const struct device *const twim1_bus =
    DEVICE_DT_GET(OPENR1_TWIM1_NODE);

K_MUTEX_DEFINE(twim1_mutex);

static openr1_twim1_zephyr_owner bus_owner;
static bool module_initialized;

static bool valid_owner(openr1_twim1_zephyr_owner owner) {
    return owner == OPENR1_TWIM1_ZEPHYR_OWNER_MOTION ||
           owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC;
}

static void configure_pin(uint32_t pin) {
    nrf_gpio_cfg(pin, NRF_GPIO_PIN_DIR_INPUT, NRF_GPIO_PIN_INPUT_CONNECT,
                 NRF_GPIO_PIN_NOPULL, NRF_GPIO_PIN_S0D1,
                 NRF_GPIO_PIN_NOSENSE);
}

static void select_pins(openr1_twim1_zephyr_owner owner) {
    const uint32_t old_scl =
        owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC
            ? OPENR1_MOTION_SCL_PIN : OPENR1_NFC_SCL_PIN;
    const uint32_t old_sda =
        owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC
            ? OPENR1_MOTION_SDA_PIN : OPENR1_NFC_SDA_PIN;
    const uint32_t scl =
        owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC
            ? OPENR1_NFC_SCL_PIN : OPENR1_MOTION_SCL_PIN;
    const uint32_t sda =
        owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC
            ? OPENR1_NFC_SDA_PIN : OPENR1_MOTION_SDA_PIN;

    nrf_twim_disable(NRF_TWIM1);
    nrf_gpio_cfg_default(old_scl);
    nrf_gpio_cfg_default(old_sda);
    configure_pin(scl);
    configure_pin(sda);
    nrf_twim_pins_set(NRF_TWIM1, scl, sda);
    nrf_twim_enable(NRF_TWIM1);
}

static int lock_owner(openr1_twim1_zephyr_owner owner) {
    if (!module_initialized || !valid_owner(owner)) {
        return -EACCES;
    }
    if (k_mutex_lock(&twim1_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    if (bus_owner != owner) {
        (void)k_mutex_unlock(&twim1_mutex);
        return -EBUSY;
    }
    return 0;
}

static int finish_transfer(openr1_twim1_zephyr_owner owner, int error) {
    /* The Zephyr driver may restore its devicetree default after bus recovery.
     * Reassert the dock pins before the next NFC transfer if recovery ran. */
    if (error != 0 && owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC) {
        select_pins(owner);
    }
    (void)k_mutex_unlock(&twim1_mutex);
    return error;
}

int openr1_twim1_zephyr_initialize(void) {
    if (module_initialized) {
        return -EALREADY;
    }
    if (!device_is_ready(twim1_bus)) {
        return -ENODEV;
    }
    bus_owner = OPENR1_TWIM1_ZEPHYR_OWNER_MOTION;
    module_initialized = true;
    return 0;
}

int openr1_twim1_zephyr_acquire(openr1_twim1_zephyr_owner owner) {
    if (!module_initialized || !valid_owner(owner)) {
        return -EACCES;
    }
    if (k_mutex_lock(&twim1_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    int error = 0;
    if (bus_owner == owner) {
        /* Idempotent acquisition by the current owner. */
    } else if (owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC ||
               bus_owner == OPENR1_TWIM1_ZEPHYR_OWNER_NONE) {
        select_pins(owner);
        bus_owner = owner;
    } else {
        error = -EBUSY;
    }
    (void)k_mutex_unlock(&twim1_mutex);
    return error;
}

int openr1_twim1_zephyr_release(openr1_twim1_zephyr_owner owner) {
    if (!module_initialized || !valid_owner(owner)) {
        return -EACCES;
    }
    if (k_mutex_lock(&twim1_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    int error = 0;
    if (bus_owner != owner) {
        error = -EINVAL;
    } else if (owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC) {
        select_pins(OPENR1_TWIM1_ZEPHYR_OWNER_MOTION);
        bus_owner = OPENR1_TWIM1_ZEPHYR_OWNER_MOTION;
    } else {
        bus_owner = OPENR1_TWIM1_ZEPHYR_OWNER_NONE;
    }
    (void)k_mutex_unlock(&twim1_mutex);
    return error;
}

int openr1_twim1_zephyr_write(openr1_twim1_zephyr_owner owner,
                              uint16_t address, const uint8_t *bytes,
                              size_t length) {
    if (length != 0u && bytes == NULL) {
        return -EINVAL;
    }
    const int lock_error = lock_owner(owner);
    if (lock_error != 0) {
        return lock_error;
    }
    return finish_transfer(owner, i2c_write(twim1_bus, bytes, length, address));
}

int openr1_twim1_zephyr_read(openr1_twim1_zephyr_owner owner,
                             uint16_t address, uint8_t *bytes,
                             size_t length) {
    if (bytes == NULL || length == 0u) {
        return -EINVAL;
    }
    const int lock_error = lock_owner(owner);
    if (lock_error != 0) {
        return lock_error;
    }
    return finish_transfer(owner, i2c_read(twim1_bus, bytes, length, address));
}

int openr1_twim1_zephyr_write_read(openr1_twim1_zephyr_owner owner,
                                   uint16_t address,
                                   const uint8_t *write_bytes,
                                   size_t write_length, uint8_t *read_bytes,
                                   size_t read_length) {
    if ((write_length != 0u && write_bytes == NULL) || read_bytes == NULL ||
        read_length == 0u) {
        return -EINVAL;
    }
    const int lock_error = lock_owner(owner);
    if (lock_error != 0) {
        return lock_error;
    }
    return finish_transfer(owner, i2c_write_read(
        twim1_bus, address, write_bytes, write_length, read_bytes,
        read_length));
}

openr1_twim1_zephyr_owner openr1_twim1_zephyr_current_owner(void) {
    return bus_owner;
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_twim1_zephyr_api twim1_zephyr_api = {
    openr1_twim1_zephyr_initialize,
    openr1_twim1_zephyr_acquire,
    openr1_twim1_zephyr_release,
    openr1_twim1_zephyr_current_owner,
};
