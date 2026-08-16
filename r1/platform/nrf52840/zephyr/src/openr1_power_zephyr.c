#include "openr1_power_zephyr.h"

#include <errno.h>

#include <hal/nrf_power.h>

typedef struct {
    int (*initialize)(void);
    int (*set_reg1)(bool);
    int (*get_reg1)(bool *);
} openr1_power_zephyr_api;

static bool power_ready;

static int write_reg1(bool enabled) {
    nrf_power_dcdcen_set(NRF_POWER, enabled);
    return nrf_power_dcdcen_get(NRF_POWER) == enabled ? 0 : -EIO;
}

int openr1_power_zephyr_initialize(void) {
    if (power_ready) {
        return -EALREADY;
    }

    /* Stock BLE initialization enables REG1 unconditionally. Zephyr's SoC
     * initialization performs the same source-HAL write when
     * CONFIG_SOC_DCDC_NRF52X is selected; repeat it here so the product-owned
     * lifecycle has an explicit, verified boundary before Bluetooth starts. */
    const int error = write_reg1(true);
    if (error == 0) {
        power_ready = true;
    }
    return error;
}

int openr1_power_zephyr_set_reg1(bool enabled) {
    if (!power_ready) {
        return -EACCES;
    }
    return write_reg1(enabled);
}

int openr1_power_zephyr_get_reg1(bool *enabled) {
    if (enabled == NULL) {
        return -EINVAL;
    }
    if (!power_ready) {
        return -EACCES;
    }
    *enabled = nrf_power_dcdcen_get(NRF_POWER);
    return 0;
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_power_zephyr_api power_zephyr_api = {
    openr1_power_zephyr_initialize,
    openr1_power_zephyr_set_reg1,
    openr1_power_zephyr_get_reg1,
};
