/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_CCC_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_CCC_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_ATTS_CCC_CONNECTIONS = 3U,
    OPEN_CFW_ATTS_CCC_STATE_EVENT = 0x14U,
    OPEN_CFW_ATTS_CCC_METHOD_READ = 5U,
    OPEN_CFW_ATTS_CCC_ATT_SUCCESS = 0x00U,
    OPEN_CFW_ATTS_CCC_ATT_ERR_NOT_FOUND = 0x0AU,
    OPEN_CFW_ATTS_CCC_ATT_ERR_RESOURCES = 0x11U,
    OPEN_CFW_ATTS_CCC_ATT_ERR_VALUE_RANGE = 0x80U,
    OPEN_CFW_ATTS_CCC_NOTIFY = 0x0001U,
    OPEN_CFW_ATTS_CCC_INDICATE = 0x0002U,
    OPEN_CFW_ATTS_CCC_HANDLE_NONE = 0x0000U
};

struct open_cfw_cordio_atts_ccc_setting {
    uint16_t handle;
    uint16_t value_range;
    uint8_t security_level;
    uint8_t reserved;
};

struct open_cfw_cordio_atts_ccc_message_header {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_cordio_atts_ccc_event {
    struct open_cfw_cordio_atts_ccc_message_header header;
    uint16_t handle;
    uint16_t value;
    uint8_t index;
    uint8_t reserved;
};

typedef void (*open_cfw_cordio_atts_ccc_callback_t)(
    struct open_cfw_cordio_atts_ccc_event *event
);
typedef uint8_t (*open_cfw_cordio_atts_ccc_main_callback_t)(
    uint8_t connection_id,
    uint8_t method,
    uint16_t handle,
    uint8_t *value
);

struct open_cfw_cordio_atts_ccc_control_block {
    uint16_t *tables[OPEN_CFW_ATTS_CCC_CONNECTIONS];
    struct open_cfw_cordio_atts_ccc_setting *settings;
    open_cfw_cordio_atts_ccc_callback_t callback;
    uint8_t settings_length;
    uint8_t reserved[3];
};

extern struct open_cfw_cordio_atts_ccc_control_block
    open_cfw_cordio_atts_ccc_control_block;
extern open_cfw_cordio_atts_ccc_main_callback_t
    open_cfw_cordio_atts_ccc_atts_main_callback;

void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_buffer_free_candidate(void *buffer);
uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t connection_id);

void open_cfw_cordio_atts_ccc_callback(
    uint8_t connection_id, uint8_t index, uint16_t handle, uint16_t value
);
uint16_t *open_cfw_cordio_atts_ccc_allocate_table(uint8_t connection_id);
uint16_t *open_cfw_cordio_atts_ccc_get_table(uint8_t connection_id);
void open_cfw_cordio_atts_ccc_free_table(uint8_t connection_id);
uint8_t open_cfw_cordio_atts_ccc_read_value(
    uint8_t connection_id, uint16_t handle, uint8_t *value
);
uint8_t open_cfw_cordio_atts_ccc_write_value(
    uint8_t connection_id, uint16_t handle, uint8_t *value
);
uint8_t open_cfw_cordio_atts_ccc_main_callback(
    uint8_t connection_id, uint8_t method, uint16_t handle, uint8_t *value
);
void open_cfw_cordio_atts_ccc_register(
    uint8_t settings_length,
    struct open_cfw_cordio_atts_ccc_setting *settings,
    open_cfw_cordio_atts_ccc_callback_t callback
);
void open_cfw_cordio_atts_ccc_initialize_table(
    uint8_t connection_id, uint16_t *initial_values
);
void open_cfw_cordio_atts_ccc_clear_table(uint8_t connection_id);
uint16_t open_cfw_cordio_atts_ccc_get(uint8_t connection_id, uint8_t index);
void open_cfw_cordio_atts_ccc_set(
    uint8_t connection_id, uint8_t index, uint16_t value
);
uint16_t open_cfw_cordio_atts_ccc_enabled(
    uint8_t connection_id, uint8_t index
);
uint8_t open_cfw_cordio_atts_ccc_table_length(void);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_atts_ccc_setting) == 6U,
    "G2 ATT CCC setting ABI");
_Static_assert(sizeof(struct open_cfw_cordio_atts_ccc_event) == 10U,
    "G2 ATT CCC event ABI");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ccc_event, index) == 8U,
    "G2 ATT CCC event index offset");
_Static_assert(sizeof(struct open_cfw_cordio_atts_ccc_control_block) == 24U,
    "G2 ATT CCC control block ABI");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ccc_control_block, settings)
    == 12U, "G2 ATT CCC settings offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ccc_control_block, callback)
    == 16U, "G2 ATT CCC callback offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ccc_control_block,
    settings_length) == 20U, "G2 ATT CCC length offset");
#endif

#endif
