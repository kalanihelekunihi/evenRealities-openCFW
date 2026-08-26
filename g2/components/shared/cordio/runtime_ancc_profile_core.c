/* SPDX-License-Identifier: BSD-3-Clause */

/*
 * Maintained ANCS client core derived from AmbiqSuite 2.5.1's BSD-3-Clause
 * ancc_main.c and hardened at every externally supplied length boundary.
 */
#include "runtime_ancc_profile_core.h"

static __attribute__((always_inline)) inline void open_cfw_ancc_zero(
    void *destination, open_cfw_ancc_u32 length
)
{
    open_cfw_ancc_u8 *bytes = (open_cfw_ancc_u8 *)destination;
    while (length != 0U) {
        *bytes++ = 0U;
        length -= 1U;
    }
}

static __attribute__((always_inline)) inline void open_cfw_ancc_copy(
    open_cfw_ancc_u8 *destination,
    const open_cfw_ancc_u8 *source,
    open_cfw_ancc_u16 length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length -= 1U;
    }
}

static __attribute__((always_inline)) inline open_cfw_ancc_u32
open_cfw_ancc_read_u32(
    const open_cfw_ancc_u8 *value
)
{
    return (open_cfw_ancc_u32)value[0]
        | ((open_cfw_ancc_u32)value[1] << 8U)
        | ((open_cfw_ancc_u32)value[2] << 16U)
        | ((open_cfw_ancc_u32)value[3] << 24U);
}

static __attribute__((always_inline)) inline int open_cfw_ancc_write(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
)
{
    if (state == (struct open_cfw_ancc_state *)0
        || hooks == (const struct open_cfw_ancc_hooks *)0
        || hooks->write == (open_cfw_ancc_write_fn)0
        || state->handles == (open_cfw_ancc_u16 *)0
        || state->connection_id == OPEN_CFW_ANCC_CONN_NONE
        || state->handles[OPEN_CFW_ANCC_HANDLE_CONTROL_POINT]
            == OPEN_CFW_ANCC_HANDLE_NONE) {
        return 0;
    }
    return hooks->write(
        hooks->context,
        state->connection_id,
        state->handles[OPEN_CFW_ANCC_HANDLE_CONTROL_POINT],
        value,
        length
    ) != 0;
}

OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_state_initialize(
    struct open_cfw_ancc_state *state,
    open_cfw_ancc_u8 handler_id
)
{
    if (state != (struct open_cfw_ancc_state *)0) {
        open_cfw_ancc_zero(state, sizeof(*state));
        state->handler_id = handler_id;
    }
}

OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_connection_open(
    struct open_cfw_ancc_state *state,
    open_cfw_ancc_u8 connection_id,
    open_cfw_ancc_u16 *handles
)
{
    if (state != (struct open_cfw_ancc_state *)0) {
        state->connection_id = connection_id;
        state->handles = handles;
        open_cfw_ancc_parser_reset(state);
    }
}

OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_connection_close(
    struct open_cfw_ancc_state *state
)
{
    if (state != (struct open_cfw_ancc_state *)0) {
        state->connection_id = OPEN_CFW_ANCC_CONN_NONE;
        state->handles = (open_cfw_ancc_u16 *)0;
        open_cfw_ancc_zero(state->list, sizeof(state->list));
        open_cfw_ancc_parser_reset(state);
    }
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_no_connection_active(
    const struct open_cfw_ancc_state *state
)
{
    return state == (const struct open_cfw_ancc_state *)0
        || state->connection_id == OPEN_CFW_ANCC_CONN_NONE;
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_notification_push(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_notification *notification
)
{
    open_cfw_ancc_u16 index;
    open_cfw_ancc_u16 available = OPEN_CFW_ANCC_LIST_CAPACITY;

    if (state == (struct open_cfw_ancc_state *)0
        || notification == (const struct open_cfw_ancc_notification *)0) {
        return 0;
    }
    for (index = 0U; index < OPEN_CFW_ANCC_LIST_CAPACITY; index += 1U) {
        if (state->list[index].valid != 0U
            && state->list[index].uid == notification->uid) {
            available = index;
            break;
        }
        if (available == OPEN_CFW_ANCC_LIST_CAPACITY
            && state->list[index].valid == 0U) {
            available = index;
        }
    }
    if (available == OPEN_CFW_ANCC_LIST_CAPACITY) {
        return 0;
    }
    state->list[available] = *notification;
    state->list[available].valid = 1U;
    return 1;
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_notification_pop(
    struct open_cfw_ancc_state *state
)
{
    open_cfw_ancc_u16 remaining = OPEN_CFW_ANCC_LIST_CAPACITY;

    if (state == (struct open_cfw_ancc_state *)0) {
        return 0;
    }
    while (remaining != 0U) {
        open_cfw_ancc_u16 index = (open_cfw_ancc_u16)(remaining - 1U);
        if (state->list[index].valid != 0U) {
            state->list[index].valid = 0U;
            state->active.handle = index;
            return 1;
        }
        remaining -= 1U;
    }
    return 0;
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_request_notification_attributes(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    open_cfw_ancc_u32 uid
)
{
    open_cfw_ancc_u8 command[19] = {
        0U, 0U, 0U, 0U, 0U,
        0U, 1U, 0U, 1U, 2U, 0U, 1U, 3U, 0U, 1U,
        4U, 5U, 6U, 7U
    };
    command[1] = (open_cfw_ancc_u8)uid;
    command[2] = (open_cfw_ancc_u8)(uid >> 8U);
    command[3] = (open_cfw_ancc_u8)(uid >> 16U);
    command[4] = (open_cfw_ancc_u8)(uid >> 24U);
    return open_cfw_ancc_write(state, hooks, command, sizeof(command));
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_request_app_attributes(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    const open_cfw_ancc_u8 *app_id
)
{
    open_cfw_ancc_u8 command[64];
    open_cfw_ancc_u16 length = 0U;

    if (app_id == (const open_cfw_ancc_u8 *)0) {
        return 0;
    }
    while (length < 62U && app_id[length] != 0U) {
        length += 1U;
    }
    if (length == 62U) {
        return 0;
    }
    command[0] = OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES;
    open_cfw_ancc_copy(command + 1, app_id, (open_cfw_ancc_u16)(length + 1U));
    command[length + 2U] = 0U;
    return open_cfw_ancc_write(
        state, hooks, command, (open_cfw_ancc_u16)(length + 3U)
    );
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_perform_action(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    open_cfw_ancc_u32 uid,
    open_cfw_ancc_u8 action
)
{
    open_cfw_ancc_u8 command[6];
    command[0] = OPEN_CFW_ANCC_COMMAND_PERFORM_ACTION;
    command[1] = (open_cfw_ancc_u8)uid;
    command[2] = (open_cfw_ancc_u8)(uid >> 8U);
    command[3] = (open_cfw_ancc_u8)(uid >> 16U);
    command[4] = (open_cfw_ancc_u8)(uid >> 24U);
    command[5] = action;
    return open_cfw_ancc_write(state, hooks, command, sizeof(command));
}

OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_parser_reset(
    struct open_cfw_ancc_state *state
)
{
    if (state != (struct open_cfw_ancc_state *)0) {
        state->active.parse_state = OPEN_CFW_ANCC_PARSE_COMMAND;
        state->active.buffer_length = 0U;
        state->active.parse_index = 0U;
        state->active.attribute_length = 0U;
        state->active.attribute_id = 0U;
        state->active.attribute_count = 0U;
        state->active.command_id = 0U;
        state->active.notification_uid = 0U;
        open_cfw_ancc_zero(
            state->app_id, OPEN_CFW_ANCC_APP_ID_CAPACITY
        );
        open_cfw_ancc_zero(
            state->data, OPEN_CFW_ANCC_ATTRIBUTE_CAPACITY
        );
    }
}

static __attribute__((always_inline)) inline int open_cfw_ancc_parse_available(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks
)
{
    struct open_cfw_ancc_active *active = &state->active;

    for (;;) {
        open_cfw_ancc_u16 remaining = (open_cfw_ancc_u16)(
            active->buffer_length - active->parse_index
        );
        if (active->parse_state == OPEN_CFW_ANCC_PARSE_COMMAND) {
            open_cfw_ancc_u16 command_start = active->parse_index;
            open_cfw_ancc_u16 consumed;
            if (remaining < 1U) {
                return 1;
            }
            active->command_id = state->data[active->parse_index++];
            if (active->command_id
                == OPEN_CFW_ANCC_COMMAND_NOTIFICATION_ATTRIBUTES) {
                if (active->buffer_length - active->parse_index < 4U) {
                    active->parse_index -= 1U;
                    return 1;
                }
                active->notification_uid = open_cfw_ancc_read_u32(
                    state->data + active->parse_index
                );
                active->parse_index += 4U;
            }
            else if (active->command_id
                == OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES) {
                consumed = 0U;
                while (active->parse_index + consumed
                        < active->buffer_length
                    && state->data[active->parse_index + consumed] != 0U
                    && consumed + 1U < OPEN_CFW_ANCC_APP_ID_CAPACITY) {
                    state->app_id[consumed] =
                        state->data[active->parse_index + consumed];
                    consumed += 1U;
                }
                if (active->parse_index + consumed >= active->buffer_length) {
                    /* The NUL-terminated app identifier may span packets. */
                    active->parse_index = command_start;
                    return 1;
                }
                if (state->data[active->parse_index + consumed] != 0U) {
                    open_cfw_ancc_parser_reset(state);
                    return 0;
                }
                state->app_id[consumed] = 0U;
                active->parse_index = (open_cfw_ancc_u16)(
                    active->parse_index + consumed + 1U
                );
            }
            else {
                open_cfw_ancc_parser_reset(state);
                return 0;
            }
            active->parse_state = OPEN_CFW_ANCC_PARSE_ATTRIBUTE;
            continue;
        }

        remaining = (open_cfw_ancc_u16)(
            active->buffer_length - active->parse_index
        );
        if (remaining < 3U) {
            active->parse_state = OPEN_CFW_ANCC_PARSE_FRAGMENT;
            return 1;
        }
        active->attribute_id = state->data[active->parse_index];
        active->attribute_length = (open_cfw_ancc_u16)(
            (open_cfw_ancc_u16)state->data[active->parse_index + 1U]
            | ((open_cfw_ancc_u16)state->data[active->parse_index + 2U]
                << 8U)
        );
        if (active->attribute_length > remaining - 3U) {
            active->parse_state = OPEN_CFW_ANCC_PARSE_FRAGMENT;
            return 1;
        }
        active->parse_index += 3U;
        active->attribute_count += 1U;
        if (hooks != (const struct open_cfw_ancc_hooks *)0
            && hooks->attribute != (open_cfw_ancc_attribute_fn)0) {
            hooks->attribute(hooks->context, state);
        }
        active->parse_index = (open_cfw_ancc_u16)(
            active->parse_index + active->attribute_length
        );
        if (active->attribute_count == (
                active->command_id == OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES
                    ? 1U : OPEN_CFW_ANCC_ATTRIBUTE_COUNT
            )) {
            if (hooks != (const struct open_cfw_ancc_hooks *)0
                && hooks->complete != (open_cfw_ancc_complete_fn)0) {
                hooks->complete(
                    hooks->context, state, active->notification_uid
                );
            }
            open_cfw_ancc_parser_reset(state);
            return 0;
        }
        active->parse_state = OPEN_CFW_ANCC_PARSE_ATTRIBUTE;
    }
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_feed_data(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
)
{
    struct open_cfw_ancc_active *active = &state->active;

    if (length > OPEN_CFW_ANCC_ATTRIBUTE_CAPACITY - active->buffer_length) {
        open_cfw_ancc_parser_reset(state);
        return 0;
    }
    open_cfw_ancc_copy(state->data + active->buffer_length, value, length);
    active->buffer_length = (open_cfw_ancc_u16)(
        active->buffer_length + length
    );
    if (active->parse_state == OPEN_CFW_ANCC_PARSE_FRAGMENT) {
        active->parse_state = OPEN_CFW_ANCC_PARSE_ATTRIBUTE;
    }
    return open_cfw_ancc_parse_available(state, hooks);
}

OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_feed_value(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    open_cfw_ancc_u16 handle,
    const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
)
{
    struct open_cfw_ancc_notification notification;

    if (state == (struct open_cfw_ancc_state *)0
        || state->handles == (open_cfw_ancc_u16 *)0
        || value == (const open_cfw_ancc_u8 *)0) {
        return 0;
    }
    if (handle == state->handles[OPEN_CFW_ANCC_HANDLE_NOTIFICATION_SOURCE]) {
        if (length != 8U) {
            return 0;
        }
        open_cfw_ancc_zero(&notification, sizeof(notification));
        notification.event_id = value[0];
        notification.event_flags = value[1];
        notification.category_id = value[2];
        notification.category_count = value[3];
        notification.uid = open_cfw_ancc_read_u32(value + 4);
        if (notification.event_id == OPEN_CFW_ANCC_EVENT_REMOVED) {
            if (hooks != (const struct open_cfw_ancc_hooks *)0
                && hooks->remove != (open_cfw_ancc_remove_fn)0) {
                hooks->remove(hooks->context, &notification);
            }
            return 1;
        }
        return open_cfw_ancc_notification_push(state, &notification);
    }
    if (handle == state->handles[OPEN_CFW_ANCC_HANDLE_DATA_SOURCE]) {
        return open_cfw_ancc_feed_data(state, hooks, value, length);
    }
    return 0;
}
