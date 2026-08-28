/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_DISPLAY_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_DISPLAY_H

#include <stdint.h>
#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_display_get_u8_fn)(uint8_t *value, void *context);
typedef int (*open_cfw_pt_display_screen_fn)(
    uint16_t screen_id, int enabled, void *context);
typedef int (*open_cfw_pt_display_parameters_fn)(
    uint8_t first, uint8_t second, int persist, void *context);
typedef int (*open_cfw_pt_display_bool_fn)(int enabled, void *context);

struct open_cfw_pt_display_providers {
    open_cfw_pt_display_get_u8_fn get_product_mode;
    open_cfw_pt_display_screen_fn set_test_screen;
    open_cfw_pt_display_parameters_fn set_display_parameters;
    open_cfw_pt_display_bool_fn set_runtime_flag;
    open_cfw_pt_display_get_u8_fn get_aging_mode;
    open_cfw_pt_display_bool_fn set_aging_mode;
    void *context;
};

int open_cfw_pt_bind_display_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_display_providers *providers
);
#endif
