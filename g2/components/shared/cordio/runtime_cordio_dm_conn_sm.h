/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_CONN_SM_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_CONN_SM_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_DM_CONN_SM_STATES = 5U,
    OPEN_CFW_DM_CONN_SM_EVENTS = 8U,
    OPEN_CFW_DM_CONN_SM_ACTION_SETS = 3U,
    OPEN_CFW_DM_CONN_SM_STATE_OFFSET = 0x15U,
    OPEN_CFW_DM_CONN_SM_EVENT_OFFSET = 2U
};

struct open_cfw_cordio_dm_connection_control_block {
    uint8_t prefix[OPEN_CFW_DM_CONN_SM_STATE_OFFSET];
    uint8_t state;
};

struct open_cfw_cordio_dm_connection_message {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

typedef void (*open_cfw_cordio_dm_connection_action_t)(
    struct open_cfw_cordio_dm_connection_control_block *control,
    struct open_cfw_cordio_dm_connection_message *message
);

#ifndef OPEN_CFW_DM_CONN_SM_PRODUCTION
extern uintptr_t open_cfw_cordio_dm_connection_action_sets[
    OPEN_CFW_DM_CONN_SM_ACTION_SETS
];
#endif

void open_cfw_cordio_dm_connection_action_none(
    struct open_cfw_cordio_dm_connection_control_block *control,
    struct open_cfw_cordio_dm_connection_message *message
);

void open_cfw_cordio_dm_connection_state_machine_execute(
    struct open_cfw_cordio_dm_connection_control_block *control,
    struct open_cfw_cordio_dm_connection_message *message
);

_Static_assert(offsetof(struct open_cfw_cordio_dm_connection_control_block,
    state) == OPEN_CFW_DM_CONN_SM_STATE_OFFSET,
    "G2 DM connection CCB state ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_connection_message,
    event) == OPEN_CFW_DM_CONN_SM_EVENT_OFFSET,
    "G2 DM connection message event ABI");

#endif
