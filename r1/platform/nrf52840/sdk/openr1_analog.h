#ifndef OPENR1_NRF52840_SDK_ANALOG_H
#define OPENR1_NRF52840_SDK_ANALOG_H

#include <stdbool.h>
#include <stdint.h>

#include "sdk_errors.h"

#include "openr1/r1_state.h"

typedef struct r1_runtime r1_runtime;

typedef struct {
    bool (*acquire_battery_power)(void *context);
    void (*release_battery_power)(void *context);
} openr1_analog_power_ops;

ret_code_t openr1_analog_initialize(void);
ret_code_t openr1_analog_bind_power(
    const openr1_analog_power_ops *operations, void *context);
ret_code_t openr1_analog_battery_millivolts(
    int16_t nv_compensation_millivolts, r1_charge_state charge,
    uint16_t *millivolts);
ret_code_t openr1_analog_update_runtime_battery(
    r1_runtime *runtime, int16_t nv_compensation_millivolts,
    r1_charge_state charge, uint32_t elapsed_seconds);
ret_code_t openr1_analog_pmic_current_millivolts(uint16_t *millivolts);
ret_code_t openr1_analog_nfc_rectifier_millivolts(uint16_t *millivolts);

#endif
