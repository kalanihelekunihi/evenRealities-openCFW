/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_dm_conn_sm.h"

#if !defined(OPEN_CFW_DM_CONN_SM_EXECUTE_ONLY)
#define OPEN_CFW_DM_CONN_SM_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_DM_CONN_SM_PRODUCTION
#define OPEN_CFW_DM_CONN_SM_ACTION_SET_TABLE \
    ((const uintptr_t *)0x20073FE4U)
#else
#define OPEN_CFW_DM_CONN_SM_ACTION_SET_TABLE \
    open_cfw_cordio_dm_connection_action_sets
#endif

struct open_cfw_dm_conn_sm_transition {
    uint8_t next_state;
    uint8_t action;
};

/* Packetcraft r20.05--r20.05c five-state/eight-event table.  Production uses
 * the separately authenticated retained G2 constant object at 0x006ECC58;
 * the host build owns the same bytes so behavior remains independently
 * executable and testable. */
#ifdef OPEN_CFW_DM_CONN_SM_PRODUCTION
#define OPEN_CFW_DM_CONN_SM_TABLE \
    ((const struct open_cfw_dm_conn_sm_transition (*) \
        [OPEN_CFW_DM_CONN_SM_EVENTS])0x006ECC58U)
#else
static const struct open_cfw_dm_conn_sm_transition
    open_cfw_dm_conn_sm_host_table[OPEN_CFW_DM_CONN_SM_STATES]
        [OPEN_CFW_DM_CONN_SM_EVENTS] = {
    {{1U, 0x10U}, {0U, 0x00U}, {2U, 0x20U}, {0U, 0x00U},
     {3U, 0x22U}, {0U, 0x00U}, {0U, 0x00U}, {0U, 0x00U}},
    {{1U, 0x00U}, {4U, 0x11U}, {1U, 0x00U}, {0U, 0x03U},
     {3U, 0x02U}, {0U, 0x03U}, {1U, 0x00U}, {1U, 0x00U}},
    {{2U, 0x00U}, {0U, 0x21U}, {2U, 0x00U}, {0U, 0x23U},
     {3U, 0x22U}, {0U, 0x23U}, {2U, 0x00U}, {2U, 0x00U}},
    {{3U, 0x00U}, {4U, 0x01U}, {3U, 0x00U}, {3U, 0x00U},
     {3U, 0x00U}, {0U, 0x04U}, {3U, 0x05U}, {3U, 0x00U}},
    {{4U, 0x00U}, {4U, 0x00U}, {4U, 0x00U}, {0U, 0x04U},
     {4U, 0x01U}, {0U, 0x04U}, {4U, 0x00U}, {4U, 0x00U}}
};
#define OPEN_CFW_DM_CONN_SM_TABLE open_cfw_dm_conn_sm_host_table
#endif

static void open_cfw_dm_conn_sm_none(
    struct open_cfw_cordio_dm_connection_control_block *control,
    struct open_cfw_cordio_dm_connection_message *message
)
{
    open_cfw_cordio_dm_connection_action_none(control, message);
}

#if defined(OPEN_CFW_DM_CONN_SM_BUILD_ALL) || \
    defined(OPEN_CFW_DM_CONN_SM_EXECUTE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_connection_state_machine_execute(
    struct open_cfw_cordio_dm_connection_control_block *control,
    struct open_cfw_cordio_dm_connection_message *message
)
{
    const struct open_cfw_dm_conn_sm_transition *transition;
    const uintptr_t *action_set;
    open_cfw_cordio_dm_connection_action_t action_function;
    uintptr_t action_set_address;
    uintptr_t action_address;
    uint8_t action;
    uint8_t action_id;
    uint8_t action_set_id;
    uint8_t event;
    uint8_t state;

    if (control == NULL || message == NULL) {
        return;
    }

    state = control->state;
    if (state >= OPEN_CFW_DM_CONN_SM_STATES) {
        open_cfw_dm_conn_sm_none(control, message);
        return;
    }

    event = (uint8_t)(message->event & 0x07U);
    transition = &OPEN_CFW_DM_CONN_SM_TABLE[state][event];
    action = transition->action;
    control->state = transition->next_state;

    action_set_id = (uint8_t)(action >> 4U);
    action_id = (uint8_t)(action & 0x0FU);
    if (action_set_id >= OPEN_CFW_DM_CONN_SM_ACTION_SETS
            || (action_set_id == 0U && action_id >= 6U)
            || (action_set_id == 1U && action_id >= 2U)
            || (action_set_id == 2U && action_id >= 4U)) {
        open_cfw_dm_conn_sm_none(control, message);
        return;
    }

    action_set_address = OPEN_CFW_DM_CONN_SM_ACTION_SET_TABLE[action_set_id];
    if (action_set_address == (uintptr_t)0U) {
        open_cfw_dm_conn_sm_none(control, message);
        return;
    }
    action_set = (const uintptr_t *)action_set_address;
    action_address = action_set[action_id];
    if (action_address == (uintptr_t)0U) {
        open_cfw_dm_conn_sm_none(control, message);
        return;
    }
    action_function = (open_cfw_cordio_dm_connection_action_t)action_address;
    action_function(control, message);
}
#endif
