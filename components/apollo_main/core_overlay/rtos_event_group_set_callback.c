/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS event-group set-bits timer callback matched to stock entry 0x0047EE1E.
 */

unsigned int open_cfw_rtos_event_group_set(
    void *group,
    unsigned int bits_to_set
);

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_CALLBACK_SET
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_CALLBACK_SET(group, bits) \
    open_cfw_rtos_event_group_set((group), (bits))
#endif

__attribute__((used, noinline))
void open_cfw_rtos_event_group_set_callback(
    void *group,
    unsigned int bits_to_set
)
{
    (void)OPEN_CFW_RTOS_EVENT_GROUP_SET_CALLBACK_SET(
        group,
        bits_to_set
    );
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_CALLBACK_SET
