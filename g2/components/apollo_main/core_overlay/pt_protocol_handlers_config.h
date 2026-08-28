/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_CONFIG_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_CONFIG_H

#include <stddef.h>
#include <stdint.h>

#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_config_get_mode_fn)(uint8_t *mode, void *context);
typedef int (*open_cfw_pt_config_set_mode_fn)(uint8_t mode, void *context);
typedef int (*open_cfw_pt_config_action_fn)(void *context);
typedef int (*open_cfw_pt_config_touch_fn)(
    uint8_t *proximity, int16_t *difference, void *context);
typedef int (*open_cfw_pt_config_write_bytes_fn)(
    const uint8_t *data, size_t length, void *context);
typedef int (*open_cfw_pt_config_buzzer_test_fn)(
    int enabled, uint32_t frequency, uint8_t duty, void *context);
typedef int (*open_cfw_pt_config_buzzer_read_fn)(
    uint32_t *frequency, uint8_t *duty, void *context);
typedef int (*open_cfw_pt_config_buzzer_write_fn)(
    uint32_t frequency, uint8_t duty, void *context);
typedef int (*open_cfw_pt_config_bool_fn)(int enabled, void *context);

struct open_cfw_pt_config_providers {
    open_cfw_pt_config_get_mode_fn get_product_mode;
    open_cfw_pt_config_set_mode_fn set_product_mode;
    open_cfw_pt_config_action_fn production_reset_action;
    open_cfw_pt_config_touch_fn read_touch_diagnostic;
    open_cfw_pt_config_write_bytes_fn write_and_verify_psn_14;
    open_cfw_pt_config_write_bytes_fn write_sensor_calibration_36;
    open_cfw_pt_config_buzzer_test_fn buzzer_test;
    open_cfw_pt_config_buzzer_read_fn buzzer_read;
    open_cfw_pt_config_buzzer_write_fn buzzer_write;
    open_cfw_pt_config_bool_fn update_onboarding;
    open_cfw_pt_config_bool_fn set_charger_test;
    void *context;
};

int open_cfw_pt_bind_config_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_config_providers *providers
);

#endif
