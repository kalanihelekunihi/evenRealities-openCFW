/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_DATA_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_DATA_H

#include <stddef.h>
#include <stdint.h>

#include "pt_protocol_procsr.h"

struct open_cfw_pt_session_status {
    uint8_t state;
    struct open_cfw_pt_time reference;
    struct open_cfw_pt_time first;
    struct open_cfw_pt_time second;
    uint8_t flag_a;
    uint8_t flag_b;
    uint8_t flag_c;
};

typedef int (*open_cfw_pt_data_read_fixed_fn)(
    uint8_t *destination, size_t length, void *context);
typedef int (*open_cfw_pt_data_read_text_fn)(
    unsigned int index, const char **text, void *context);
typedef int (*open_cfw_pt_data_set_bool_fn)(int value, void *context);
typedef int (*open_cfw_pt_data_read_u8_fn)(uint8_t *value, void *context);
typedef int (*open_cfw_pt_data_read_pair_fn)(
    uint8_t *first, uint8_t *second, void *context);
typedef int (*open_cfw_pt_data_session_fn)(
    struct open_cfw_pt_session_status *status, void *context);

struct open_cfw_pt_data_providers {
    open_cfw_pt_data_read_fixed_fn read_identifier_6;
    open_cfw_pt_data_read_text_fn read_system_text;
    open_cfw_pt_data_set_bool_fn set_sync_ready;
    open_cfw_pt_data_read_u8_fn read_boolean_flag;
    open_cfw_pt_data_read_pair_fn read_pair_state;
    open_cfw_pt_data_session_fn read_session_status;
    open_cfw_pt_data_read_fixed_fn read_diagnostic_blob_36;
    open_cfw_pt_data_read_text_fn read_font_version;
    open_cfw_pt_data_read_u8_fn read_display_value;
    void *context;
};

int open_cfw_pt_bind_data_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_data_providers *providers
);

#endif
