#include "openr1_nfc_resources_zephyr.h"

#include <errno.h>
#include <stdint.h>

#include <hal/nrf_gpio.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

#include "openr1_nfc_zephyr.h"

#define OPENR1_POWER_NODE DT_NODELABEL(openr1_power)
#define OPENR1_NFC_BOARD_ENABLE_PIN NRF_GPIO_PIN_MAP(1, 10)
#define OPENR1_NFC_BOARD_SETTLE_TICKS UINT32_C(10)

typedef struct {
    int (*initialize)(void);
    bool (*board_enabled)(void);
} openr1_nfc_resources_zephyr_api;

static const struct gpio_dt_spec board_enable_gpio =
    GPIO_DT_SPEC_GET(OPENR1_POWER_NODE, nfc_enable_gpios);

K_MUTEX_DEFINE(nfc_dock_bus_mutex);

static bool board_enabled;
static bool dock_bus_active;
static bool module_initialized;

static void configure_board_enable(void) {
    nrf_gpio_cfg(OPENR1_NFC_BOARD_ENABLE_PIN,
                 NRF_GPIO_PIN_DIR_OUTPUT,
                 NRF_GPIO_PIN_INPUT_DISCONNECT,
                 NRF_GPIO_PIN_PULLUP,
                 NRF_GPIO_PIN_H0H1,
                 NRF_GPIO_PIN_NOSENSE);
    nrf_gpio_pin_clear(OPENR1_NFC_BOARD_ENABLE_PIN);
    board_enabled = false;
}

static bool acquire_board_enable(void *context) {
    (void)context;
    if (!module_initialized || board_enabled || k_is_in_isr()) {
        return false;
    }
    nrf_gpio_pin_clear(OPENR1_NFC_BOARD_ENABLE_PIN);
    k_sleep(K_TICKS(OPENR1_NFC_BOARD_SETTLE_TICKS));
    nrf_gpio_pin_set(OPENR1_NFC_BOARD_ENABLE_PIN);
    k_sleep(K_TICKS(OPENR1_NFC_BOARD_SETTLE_TICKS));
    board_enabled = true;
    return true;
}

static void release_board_enable(void *context) {
    (void)context;
    nrf_gpio_pin_clear(OPENR1_NFC_BOARD_ENABLE_PIN);
    board_enabled = false;
}

static bool acquire_dock_bus(void *context) {
    (void)context;
    if (!module_initialized || dock_bus_active || k_is_in_isr() ||
        k_mutex_lock(&nfc_dock_bus_mutex, K_NO_WAIT) != 0) {
        return false;
    }
    dock_bus_active = true;
    return true;
}

static void release_dock_bus(void *context) {
    (void)context;
    if (dock_bus_active) {
        dock_bus_active = false;
        (void)k_mutex_unlock(&nfc_dock_bus_mutex);
    }
}

int openr1_nfc_resources_zephyr_initialize(void) {
    static const openr1_nfc_zephyr_resource_ops resources = {
        acquire_board_enable,
        release_board_enable,
        acquire_dock_bus,
        release_dock_bus,
    };
    if (module_initialized) {
        return -EALREADY;
    }
    if (!gpio_is_ready_dt(&board_enable_gpio)) {
        return -ENODEV;
    }
    configure_board_enable();
    module_initialized = true;
    const int error = openr1_nfc_zephyr_bind_resources(&resources, NULL);
    if (error != 0) {
        module_initialized = false;
        configure_board_enable();
    }
    return error;
}

bool openr1_nfc_resources_zephyr_board_enabled(void) {
    return board_enabled;
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_nfc_resources_zephyr_api nfc_resources_zephyr_api = {
    openr1_nfc_resources_zephyr_initialize,
    openr1_nfc_resources_zephyr_board_enabled,
};
