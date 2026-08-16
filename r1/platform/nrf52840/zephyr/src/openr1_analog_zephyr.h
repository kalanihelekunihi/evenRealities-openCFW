#ifndef OPENR1_ANALOG_ZEPHYR_H
#define OPENR1_ANALOG_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_state.h"

typedef struct r1_runtime r1_runtime;

typedef struct {
    bool (*acquire_battery_power)(void *context);
    void (*release_battery_power)(void *context);
} openr1_analog_zephyr_power_ops;

typedef struct {
    int (*initialize)(void);
    int (*bind_power)(const openr1_analog_zephyr_power_ops *, void *);
    int (*battery_millivolts)(int16_t, r1_charge_state, uint16_t *);
    int (*update_runtime_battery)(
        r1_runtime *, int16_t, r1_charge_state, uint32_t);
    int (*pmic_current_millivolts)(uint16_t *);
    int (*nfc_rectifier_millivolts)(uint16_t *);
} openr1_analog_zephyr_api;

int openr1_analog_zephyr_initialize(void);
int openr1_analog_zephyr_bind_power(
    const openr1_analog_zephyr_power_ops *operations, void *context);
int openr1_analog_zephyr_battery_millivolts(
    int16_t nv_compensation_millivolts, r1_charge_state charge,
    uint16_t *millivolts);
int openr1_analog_zephyr_update_runtime_battery(
    r1_runtime *runtime, int16_t nv_compensation_millivolts,
    r1_charge_state charge, uint32_t elapsed_seconds);
int openr1_analog_zephyr_pmic_current_millivolts(uint16_t *millivolts);
int openr1_analog_zephyr_nfc_rectifier_millivolts(uint16_t *millivolts);

extern const openr1_analog_zephyr_api openr1_analog_zephyr_api_table;

#endif
