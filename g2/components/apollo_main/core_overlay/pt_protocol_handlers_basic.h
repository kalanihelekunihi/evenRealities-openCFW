/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_BASIC_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_BASIC_H

#include <stdint.h>

#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_basic_set_bool_fn)(int enabled, void *context);
typedef int (*open_cfw_pt_basic_action_fn)(void *context);
typedef int (*open_cfw_pt_basic_store_u8_fn)(uint8_t value, void *context);
typedef int (*open_cfw_pt_basic_load_u8_fn)(uint8_t *value, void *context);

struct open_cfw_pt_basic_providers {
    open_cfw_pt_basic_set_bool_fn set_box_detected;
    open_cfw_pt_basic_action_fn codec_delay;
    open_cfw_pt_basic_store_u8_fn store_terminal_mode;
    open_cfw_pt_basic_load_u8_fn load_terminal_mode;
    open_cfw_pt_basic_action_fn post_input_message;
    void *context;
};

int open_cfw_pt_bind_basic_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_basic_providers *providers
);

#endif
