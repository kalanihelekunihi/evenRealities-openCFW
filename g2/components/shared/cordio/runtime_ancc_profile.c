/* SPDX-License-Identifier: BSD-3-Clause */

/*
 * G2 ABI adapter for the maintained ANCS client core.  Each public function
 * is built as an isolated Cortex-M leaf.  The large parser entry also acts as
 * the internal dispatcher so the other twenty stock entries remain small and
 * every route shares one reviewed state machine.
 */
#include "runtime_ancc_profile_core.h"

typedef __UINTPTR_TYPE__ open_cfw_ancc_word;

struct open_cfw_ancc_att_event {
    open_cfw_ancc_u16 parameter;
    open_cfw_ancc_u8 event;
    open_cfw_ancc_u8 status;
    open_cfw_ancc_u8 *value;
    open_cfw_ancc_u16 value_length;
    open_cfw_ancc_u16 handle;
};

struct open_cfw_ancc_product_notification {
    open_cfw_ancc_u32 uid;
    open_cfw_ancc_u8 event_id;
    open_cfw_ancc_u8 category_id;
    open_cfw_ancc_u8 positive_action;
    open_cfw_ancc_u8 negative_action;
    open_cfw_ancc_u8 app_id[64];
    open_cfw_ancc_u8 app_name[32];
    open_cfw_ancc_u8 title[64];
    open_cfw_ancc_u8 subtitle[64];
    open_cfw_ancc_u8 message[512];
    open_cfw_ancc_u8 date[16];
    open_cfw_ancc_u8 reserved[4];
};

#if __UINTPTR_MAX__ == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_ancc_att_event) == 12U,
    "G2 ATT event ABI");
_Static_assert(sizeof(struct open_cfw_ancc_product_notification) == 0x2FCU,
    "G2 product notification ABI");
#endif

#ifdef OPEN_CFW_ANCC_PROFILE_PRODUCTION
#define OPEN_CFW_ANCC_STATE \
    ((struct open_cfw_ancc_state *)0x200695C8U)
#define OPEN_CFW_ANCC_PRODUCT \
    ((struct open_cfw_ancc_product_notification *)0x2006DDD4U)
#define OPEN_CFW_ANCC_PROFILE_CONTEXT (*(void **)0x20074898U)
#define OPEN_CFW_ANCC_PROFILE_ARGUMENT (*(void **)0x2007489CU)
#define OPEN_CFW_ANCC_HANDLE_LIST (*(open_cfw_ancc_u16 **)0x200748A0U)
#else
extern struct open_cfw_ancc_state open_cfw_ancc_profile_state;
extern struct open_cfw_ancc_product_notification
    open_cfw_ancc_product_notification;
extern void *open_cfw_ancc_profile_context;
extern void *open_cfw_ancc_profile_argument;
extern open_cfw_ancc_u16 *open_cfw_ancc_handle_list;
#define OPEN_CFW_ANCC_STATE (&open_cfw_ancc_profile_state)
#define OPEN_CFW_ANCC_PRODUCT (&open_cfw_ancc_product_notification)
#define OPEN_CFW_ANCC_PROFILE_CONTEXT open_cfw_ancc_profile_context
#define OPEN_CFW_ANCC_PROFILE_ARGUMENT open_cfw_ancc_profile_argument
#define OPEN_CFW_ANCC_HANDLE_LIST open_cfw_ancc_handle_list
#endif

void open_cfw_cordio_attc_write_request(
    open_cfw_ancc_u8, open_cfw_ancc_u16, open_cfw_ancc_u16,
    const open_cfw_ancc_u8 *
);
void *open_cfw_cordio_wsf_message_allocate_candidate(open_cfw_ancc_u16);
void open_cfw_cordio_wsf_message_send_candidate(open_cfw_ancc_u8, void *);
void open_cfw_event_loop_push_delayed(void (*)(open_cfw_ancc_u8), open_cfw_ancc_u32,
    open_cfw_ancc_u32);
void open_cfw_event_loop_remove_delayed(void (*)(open_cfw_ancc_u8));
void open_cfw_ancc_sync_send(
    open_cfw_ancc_u16, const void *, open_cfw_ancc_u16, int (*)(int)
);
open_cfw_ancc_u8 open_cfw_cordio_dm_connection_role(open_cfw_ancc_u8);
open_cfw_ancc_u8 open_cfw_ancc_product_role(void);
open_cfw_ancc_u8 open_cfw_ancc_service_enabled(void);
open_cfw_ancc_u8 open_cfw_ancc_ota_active(void);
open_cfw_ancc_u8 open_cfw_ancc_efs_active(void);
open_cfw_ancc_u32 open_cfw_cmsis_kernel_get_tick_count(void);
open_cfw_ancc_u32 open_cfw_ancc_connection_epoch(void);
open_cfw_ancc_u8 open_cfw_ancc_whitelist_result(const open_cfw_ancc_u8 *);
void open_cfw_ancc_report_unlisted_app(
    const open_cfw_ancc_u8 *, const open_cfw_ancc_u8 *
);
void open_cfw_ancc_discover_service(
    open_cfw_ancc_u8, open_cfw_ancc_u8, const open_cfw_ancc_u8 *,
    open_cfw_ancc_u8, const void *, open_cfw_ancc_u16 *
);

open_cfw_ancc_word open_cfw_ancc_dispatch(
    open_cfw_ancc_word, open_cfw_ancc_word, open_cfw_ancc_word,
    open_cfw_ancc_word
);
void open_cfw_ancc_get_next_notification_handler(open_cfw_ancc_u8);
int open_cfw_ancc_rx_sync_event_callback(int);

#if defined(__arm__) || defined(__thumb__)
__asm__(".type open_cfw_ancc_get_next_notification_handler,%function");
__asm__(".type open_cfw_ancc_rx_sync_event_callback,%function");
#endif

enum {
    OPEN_CFW_ANCC_OP_CONN_OPEN = 1,
    OPEN_CFW_ANCC_OP_CONN_CLOSE,
    OPEN_CFW_ANCC_OP_NO_CONNECTION,
    OPEN_CFW_ANCC_OP_POP,
    OPEN_CFW_ANCC_OP_GET_NEXT,
    OPEN_CFW_ANCC_OP_GET_NOTIFICATION,
    OPEN_CFW_ANCC_OP_ACTION,
    OPEN_CFW_ANCC_OP_GET_APP,
    OPEN_CFW_ANCC_OP_PUSH,
    OPEN_CFW_ANCC_OP_SYNC_CALLBACK,
    OPEN_CFW_ANCC_OP_COMPLETE,
    OPEN_CFW_ANCC_OP_REMOVE,
    OPEN_CFW_ANCC_OP_VALUE_UPDATE,
    OPEN_CFW_ANCC_OP_VALUE_GATE,
    OPEN_CFW_ANCC_OP_ATTRIBUTE_CALLBACK,
    OPEN_CFW_ANCC_OP_RESET,
    OPEN_CFW_ANCC_OP_INIT,
    OPEN_CFW_ANCC_OP_PROCESS_MESSAGE,
    OPEN_CFW_ANCC_OP_DISCOVER,
    OPEN_CFW_ANCC_OP_GET_ACTIVE,
    OPEN_CFW_ANCC_OP_LAST = OPEN_CFW_ANCC_OP_GET_ACTIVE
};

#if !defined(OPEN_CFW_ANCC_PROFILE_CONN_OPEN_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_CONN_CLOSE_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_NO_CONNECTION_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_POP_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_GET_NEXT_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_GET_NOTIFICATION_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_ACTION_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_GET_APP_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_PUSH_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_SYNC_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_REMOVE_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_VALUE_UPDATE_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_VALUE_GATE_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_ATTRIBUTE_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_DISPATCH_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_RESET_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_INIT_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_PROCESS_MESSAGE_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_DISCOVER_ONLY) && \
    !defined(OPEN_CFW_ANCC_PROFILE_GET_ACTIVE_ONLY)
#define OPEN_CFW_ANCC_PROFILE_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline void open_cfw_ancc_memory_zero(
    void *destination, open_cfw_ancc_u16 length
)
{
    open_cfw_ancc_u8 *output = destination;
    while (length-- != 0U) {
        *output++ = 0U;
    }
}

static __attribute__((always_inline, unused)) inline void open_cfw_ancc_memory_copy(
    void *destination, const void *source, open_cfw_ancc_u16 length
)
{
    open_cfw_ancc_u8 *output = destination;
    const open_cfw_ancc_u8 *input = source;
    while (length-- != 0U) {
        *output++ = *input++;
    }
}

static __attribute__((always_inline, unused)) inline open_cfw_ancc_u32
open_cfw_ancc_u32_read(const open_cfw_ancc_u8 *value)
{
    return (open_cfw_ancc_u32)value[0]
        | ((open_cfw_ancc_u32)value[1] << 8U)
        | ((open_cfw_ancc_u32)value[2] << 16U)
        | ((open_cfw_ancc_u32)value[3] << 24U);
}

static __attribute__((always_inline, unused)) inline void open_cfw_ancc_reset_inline(void)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    state->active.parse_state = OPEN_CFW_ANCC_PARSE_COMMAND;
    state->active.buffer_length = 0U;
    state->active.parse_index = 0U;
    state->active.attribute_length = 0U;
    state->active.attribute_id = 0U;
    state->active.attribute_count = 0U;
    state->active.command_id = 0U;
    state->active.notification_uid = 0U;
    open_cfw_ancc_memory_zero(state->app_id, sizeof(state->app_id));
    open_cfw_ancc_memory_zero(state->data, sizeof(state->data));
}

static __attribute__((always_inline, unused)) inline int open_cfw_ancc_write_inline(
    open_cfw_ancc_u16 *handles, const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    if (handles == (open_cfw_ancc_u16 *)0 || state->connection_id == 0U
        || handles[OPEN_CFW_ANCC_HANDLE_CONTROL_POINT] == 0U) {
        return 0;
    }
    open_cfw_cordio_attc_write_request(
        state->connection_id,
        handles[OPEN_CFW_ANCC_HANDLE_CONTROL_POINT], length, value
    );
    return 1;
}

static __attribute__((always_inline, unused)) inline int
open_cfw_ancc_get_notification_inline(
    open_cfw_ancc_u16 *handles, open_cfw_ancc_u32 uid
)
{
    open_cfw_ancc_u8 command[19];
    command[0] = 0U;
    command[1] = (open_cfw_ancc_u8)uid;
    command[2] = (open_cfw_ancc_u8)(uid >> 8U);
    command[3] = (open_cfw_ancc_u8)(uid >> 16U);
    command[4] = (open_cfw_ancc_u8)(uid >> 24U);
    command[5] = 0U;
    command[6] = 1U;
    command[7] = 0U;
    command[8] = 1U;
    command[9] = 2U;
    command[10] = 0U;
    command[11] = 1U;
    command[12] = 3U;
    command[13] = 0U;
    command[14] = 1U;
    command[15] = 4U;
    command[16] = 5U;
    command[17] = 6U;
    command[18] = 7U;
    return open_cfw_ancc_write_inline(handles, command, sizeof(command));
}

static __attribute__((always_inline, unused)) inline int open_cfw_ancc_action_inline(
    open_cfw_ancc_u16 *handles, open_cfw_ancc_u32 uid,
    open_cfw_ancc_u8 action
)
{
    open_cfw_ancc_u8 command[6] = {
        2U, (open_cfw_ancc_u8)uid, (open_cfw_ancc_u8)(uid >> 8U),
        (open_cfw_ancc_u8)(uid >> 16U), (open_cfw_ancc_u8)(uid >> 24U), action
    };
    return open_cfw_ancc_write_inline(handles, command, sizeof(command));
}

static __attribute__((always_inline, unused)) inline int open_cfw_ancc_get_app_inline(
    open_cfw_ancc_u16 *handles, const open_cfw_ancc_u8 *app_id
)
{
    open_cfw_ancc_u8 command[64];
    open_cfw_ancc_u16 length = 0U;
    if (app_id == (const open_cfw_ancc_u8 *)0) {
        return 0;
    }
    while (length < 62U && app_id[length] != 0U) {
        length++;
    }
    if (length == 62U) {
        return 0;
    }
    command[0] = 1U;
    open_cfw_ancc_memory_copy(command + 1U, app_id,
        (open_cfw_ancc_u16)(length + 1U));
    command[length + 2U] = 0U;
    return open_cfw_ancc_write_inline(
        handles, command, (open_cfw_ancc_u16)(length + 3U)
    );
}

static __attribute__((always_inline, unused)) inline int open_cfw_ancc_push_inline(
    const struct open_cfw_ancc_notification *notification
)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    open_cfw_ancc_u16 first_free = OPEN_CFW_ANCC_LIST_CAPACITY;
    if (notification == (const struct open_cfw_ancc_notification *)0) {
        return 0;
    }
    for (open_cfw_ancc_u16 index = 0U;
            index < OPEN_CFW_ANCC_LIST_CAPACITY; ++index) {
        if (state->list[index].valid != 0U
            && state->list[index].uid == notification->uid) {
            state->list[index] = *notification;
            state->list[index].valid = 1U;
            return 1;
        }
        if (first_free == OPEN_CFW_ANCC_LIST_CAPACITY
            && state->list[index].valid == 0U) {
            first_free = index;
        }
    }
    if (first_free == OPEN_CFW_ANCC_LIST_CAPACITY) {
        return 0;
    }
    state->list[first_free] = *notification;
    state->list[first_free].valid = 1U;
    return 1;
}

static __attribute__((always_inline, unused)) inline int open_cfw_ancc_pop_inline(void)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    for (open_cfw_ancc_u16 remaining = OPEN_CFW_ANCC_LIST_CAPACITY;
            remaining != 0U; --remaining) {
        open_cfw_ancc_u16 index = (open_cfw_ancc_u16)(remaining - 1U);
        if (state->list[index].valid != 0U) {
            state->list[index].valid = 0U;
            state->active.handle = index;
            return 1;
        }
    }
    return 0;
}

static __attribute__((always_inline, unused)) inline open_cfw_ancc_u16
open_cfw_ancc_bounded_copy_string(
    open_cfw_ancc_u8 *destination, open_cfw_ancc_u16 capacity,
    const open_cfw_ancc_u8 *source, open_cfw_ancc_u16 length
)
{
    open_cfw_ancc_u16 copied = length;
    if (capacity == 0U) {
        return 0U;
    }
    if (copied >= capacity) {
        copied = (open_cfw_ancc_u16)(capacity - 1U);
    }
    open_cfw_ancc_memory_copy(destination, source, copied);
    destination[copied] = 0U;
    return copied;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_ancc_complete_product_inline(void)
{
    open_cfw_ancc_sync_send(
        0x101U, OPEN_CFW_ANCC_PRODUCT,
        sizeof(struct open_cfw_ancc_product_notification),
        open_cfw_ancc_rx_sync_event_callback
    );
}

static __attribute__((always_inline, unused)) inline void
open_cfw_ancc_attribute_inline(void)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    struct open_cfw_ancc_active *active = &state->active;
    struct open_cfw_ancc_product_notification *product = OPEN_CFW_ANCC_PRODUCT;
    const open_cfw_ancc_u8 *value = state->data + active->parse_index;
    open_cfw_ancc_u16 length = active->attribute_length;
    if (active->command_id == OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES) {
        if (active->attribute_id == 0U && length != 0U) {
            open_cfw_ancc_bounded_copy_string(
                product->app_name, sizeof(product->app_name), value, length
            );
            if (open_cfw_ancc_whitelist_result(product->app_id) == 1U) {
                open_cfw_ancc_report_unlisted_app(
                    product->app_id, product->app_name
                );
            } else {
                open_cfw_ancc_complete_product_inline();
            }
        }
        return;
    }
    switch (active->attribute_id) {
    case 0U:
        open_cfw_ancc_bounded_copy_string(
            state->app_id, sizeof(state->app_id), value, length
        );
        open_cfw_ancc_bounded_copy_string(
            product->app_id, sizeof(product->app_id), value, length
        );
        if (active->handle < OPEN_CFW_ANCC_LIST_CAPACITY) {
            const struct open_cfw_ancc_notification *notification =
                &state->list[active->handle];
            product->uid = notification->uid;
            product->event_id = notification->event_id;
            product->category_id = notification->category_id;
            product->positive_action =
                (open_cfw_ancc_u8)((notification->event_flags & 0x08U) != 0U);
            product->negative_action =
                (open_cfw_ancc_u8)((notification->event_flags & 0x10U) != 0U);
        }
        if (state->app_id[0] != 0U
            && (product->event_id == OPEN_CFW_ANCC_EVENT_ADDED
                || product->event_id == OPEN_CFW_ANCC_EVENT_MODIFIED)) {
            (void)open_cfw_ancc_get_app_inline(state->handles, state->app_id);
        }
        break;
    case 1U:
        open_cfw_ancc_bounded_copy_string(
            product->title, sizeof(product->title), value, length
        );
        break;
    case 2U:
        open_cfw_ancc_bounded_copy_string(
            product->subtitle, sizeof(product->subtitle), value, length
        );
        break;
    case 3U:
        open_cfw_ancc_bounded_copy_string(
            product->message, sizeof(product->message), value, length
        );
        break;
    case 5U:
        open_cfw_ancc_bounded_copy_string(
            product->date, sizeof(product->date), value, length
        );
        break;
    case 6U:
        if (length != 0U) {
            product->positive_action = 1U;
        }
        break;
    case 7U:
        if (length != 0U) {
            product->negative_action = 1U;
        }
        break;
    default:
        break;
    }
}

static __attribute__((always_inline, unused)) inline int open_cfw_ancc_parse_inline(
    const open_cfw_ancc_u8 *value, open_cfw_ancc_u16 length
)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    struct open_cfw_ancc_active *active = &state->active;
    if (value == (const open_cfw_ancc_u8 *)0
        || length > OPEN_CFW_ANCC_ATTRIBUTE_CAPACITY - active->buffer_length) {
        open_cfw_ancc_reset_inline();
        return 0;
    }
    open_cfw_ancc_memory_copy(
        state->data + active->buffer_length, value, length
    );
    active->buffer_length = (open_cfw_ancc_u16)(
        active->buffer_length + length
    );
    if (active->parse_state == OPEN_CFW_ANCC_PARSE_FRAGMENT) {
        active->parse_state = OPEN_CFW_ANCC_PARSE_ATTRIBUTE;
    }
    for (;;) {
        open_cfw_ancc_u16 remaining = (open_cfw_ancc_u16)(
            active->buffer_length - active->parse_index
        );
        if (active->parse_state == OPEN_CFW_ANCC_PARSE_COMMAND) {
            open_cfw_ancc_u16 start = active->parse_index;
            open_cfw_ancc_u16 consumed = 0U;
            if (remaining < 1U) {
                return 1;
            }
            active->command_id = state->data[active->parse_index++];
            if (active->command_id ==
                    OPEN_CFW_ANCC_COMMAND_NOTIFICATION_ATTRIBUTES) {
                if (active->buffer_length - active->parse_index < 4U) {
                    active->parse_index = start;
                    return 1;
                }
                active->notification_uid = open_cfw_ancc_u32_read(
                    state->data + active->parse_index
                );
                active->parse_index += 4U;
            } else if (active->command_id ==
                    OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES) {
                while (active->parse_index + consumed < active->buffer_length
                    && state->data[active->parse_index + consumed] != 0U
                    && consumed + 1U < OPEN_CFW_ANCC_APP_ID_CAPACITY) {
                    state->app_id[consumed] =
                        state->data[active->parse_index + consumed];
                    consumed++;
                }
                if (active->parse_index + consumed >= active->buffer_length) {
                    active->parse_index = start;
                    return 1;
                }
                if (state->data[active->parse_index + consumed] != 0U) {
                    open_cfw_ancc_reset_inline();
                    return 0;
                }
                state->app_id[consumed] = 0U;
                active->parse_index = (open_cfw_ancc_u16)(
                    active->parse_index + consumed + 1U
                );
            } else {
                open_cfw_ancc_reset_inline();
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
            state->data[active->parse_index + 1U]
            | ((open_cfw_ancc_u16)state->data[active->parse_index + 2U] << 8U)
        );
        if (active->attribute_length > remaining - 3U) {
            active->parse_state = OPEN_CFW_ANCC_PARSE_FRAGMENT;
            return 1;
        }
        active->parse_index += 3U;
        active->attribute_count++;
        open_cfw_ancc_attribute_inline();
        active->parse_index = (open_cfw_ancc_u16)(
            active->parse_index + active->attribute_length
        );
        if (active->attribute_count >= (
                active->command_id == OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES
                    ? 1U : OPEN_CFW_ANCC_ATTRIBUTE_COUNT
            )) {
            open_cfw_ancc_u8 command = active->command_id;
            open_cfw_ancc_u32 uid = active->notification_uid;
            open_cfw_ancc_reset_inline();
            if (command == OPEN_CFW_ANCC_COMMAND_NOTIFICATION_ATTRIBUTES) {
                (void)open_cfw_ancc_action_inline(state->handles, uid, 1U);
            }
            return 0;
        }
        active->parse_state = OPEN_CFW_ANCC_PARSE_ATTRIBUTE;
    }
}

#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || \
    defined(OPEN_CFW_ANCC_PROFILE_DISPATCH_ONLY)
__attribute__((used, noinline)) open_cfw_ancc_word open_cfw_ancc_dispatch(
    open_cfw_ancc_word operation, open_cfw_ancc_word a,
    open_cfw_ancc_word b, open_cfw_ancc_word c
)
{
    struct open_cfw_ancc_state *state = OPEN_CFW_ANCC_STATE;
    if (operation > OPEN_CFW_ANCC_OP_LAST) {
        return (open_cfw_ancc_word)open_cfw_ancc_parse_inline(
            (const open_cfw_ancc_u8 *)operation, (open_cfw_ancc_u16)a
        );
    }
    switch (operation) {
    case OPEN_CFW_ANCC_OP_CONN_OPEN:
        state->connection_id = (open_cfw_ancc_u8)a;
        state->handles = (open_cfw_ancc_u16 *)b;
        open_cfw_ancc_reset_inline();
        return 0U;
    case OPEN_CFW_ANCC_OP_CONN_CLOSE:
        state->connection_id = 0U;
        state->handles = (open_cfw_ancc_u16 *)0;
        open_cfw_ancc_memory_zero(state->list, sizeof(state->list));
        open_cfw_ancc_reset_inline();
        return 0U;
    case OPEN_CFW_ANCC_OP_NO_CONNECTION:
        return state->connection_id == 0U;
    case OPEN_CFW_ANCC_OP_POP:
        return (open_cfw_ancc_word)open_cfw_ancc_pop_inline();
    case OPEN_CFW_ANCC_OP_GET_NEXT: {
        open_cfw_ancc_u16 *message =
            open_cfw_cordio_wsf_message_allocate_candidate(12U);
        if (message != (open_cfw_ancc_u16 *)0) {
            *message = *(open_cfw_ancc_u16 *)state;
            ((open_cfw_ancc_u8 *)message)[2] = (open_cfw_ancc_u8)a;
            open_cfw_cordio_wsf_message_send_candidate(
                state->handler_id, message
            );
        }
        return 0U;
    }
    case OPEN_CFW_ANCC_OP_GET_NOTIFICATION:
        return (open_cfw_ancc_word)open_cfw_ancc_get_notification_inline(
            (open_cfw_ancc_u16 *)a, (open_cfw_ancc_u32)b
        );
    case OPEN_CFW_ANCC_OP_ACTION:
        return (open_cfw_ancc_word)open_cfw_ancc_action_inline(
            (open_cfw_ancc_u16 *)a, (open_cfw_ancc_u32)b,
            (open_cfw_ancc_u8)c
        );
    case OPEN_CFW_ANCC_OP_GET_APP:
        return (open_cfw_ancc_word)open_cfw_ancc_get_app_inline(
            (open_cfw_ancc_u16 *)a, (const open_cfw_ancc_u8 *)b
        );
    case OPEN_CFW_ANCC_OP_PUSH:
        return (open_cfw_ancc_word)open_cfw_ancc_push_inline(
            (const struct open_cfw_ancc_notification *)a
        );
    case OPEN_CFW_ANCC_OP_SYNC_CALLBACK:
        return a;
    case OPEN_CFW_ANCC_OP_COMPLETE:
        open_cfw_ancc_sync_send(
            0x101U, (const void *)a, (open_cfw_ancc_u16)b,
            open_cfw_ancc_rx_sync_event_callback
        );
        return 0U;
    case OPEN_CFW_ANCC_OP_REMOVE:
        return 0U;
    case OPEN_CFW_ANCC_OP_VALUE_UPDATE: {
        open_cfw_ancc_u16 *handles = (open_cfw_ancc_u16 *)a;
        struct open_cfw_ancc_att_event *event =
            (struct open_cfw_ancc_att_event *)b;
        if (handles == (open_cfw_ancc_u16 *)0
            || event == (struct open_cfw_ancc_att_event *)0
            || event->value == (open_cfw_ancc_u8 *)0) {
            return 0U;
        }
        if (event->handle == handles[OPEN_CFW_ANCC_HANDLE_NOTIFICATION_SOURCE]) {
            struct open_cfw_ancc_notification notification;
            if (event->value_length != 8U) {
                return 0U;
            }
            open_cfw_ancc_memory_zero(&notification, sizeof(notification));
            notification.event_id = event->value[0];
            notification.event_flags = event->value[1];
            notification.category_id = event->value[2];
            notification.category_count = event->value[3];
            notification.uid = open_cfw_ancc_u32_read(event->value + 4U);
            if (notification.event_id == OPEN_CFW_ANCC_EVENT_REMOVED) {
                return 1U;
            }
            if (open_cfw_ancc_push_inline(&notification) != 0
                && state->connection_id != 0U) {
                open_cfw_event_loop_push_delayed(
                    open_cfw_ancc_get_next_notification_handler, 0xA2U, 200U
                );
                return 1U;
            }
            return 0U;
        }
        if (event->handle == handles[OPEN_CFW_ANCC_HANDLE_DATA_SOURCE]) {
            return (open_cfw_ancc_word)open_cfw_ancc_parse_inline(
                event->value, event->value_length
            );
        }
        return 0U;
    }
    case OPEN_CFW_ANCC_OP_VALUE_GATE: {
        struct open_cfw_ancc_att_event *event =
            (struct open_cfw_ancc_att_event *)a;
        open_cfw_ancc_u16 *handles = OPEN_CFW_ANCC_HANDLE_LIST;
        if (event == (struct open_cfw_ancc_att_event *)0
            || handles == (open_cfw_ancc_u16 *)0
            || (event->handle != handles[0] && event->handle != handles[2]
                && event->handle != handles[3])
            || open_cfw_ancc_service_enabled() != 1U
            || open_cfw_ancc_ota_active() != 0U
            || open_cfw_ancc_efs_active() != 0U
            || (open_cfw_ancc_u32)(open_cfw_cmsis_kernel_get_tick_count()
                - open_cfw_ancc_connection_epoch()) < 5000U) {
            return 0U;
        }
        return open_cfw_ancc_dispatch(
            OPEN_CFW_ANCC_OP_VALUE_UPDATE,
            (open_cfw_ancc_word)handles, a, 0U
        );
    }
    case OPEN_CFW_ANCC_OP_ATTRIBUTE_CALLBACK:
        open_cfw_ancc_attribute_inline();
        return 0U;
    case OPEN_CFW_ANCC_OP_RESET:
        open_cfw_ancc_reset_inline();
        return 0U;
    case OPEN_CFW_ANCC_OP_INIT:
        open_cfw_ancc_memory_zero(state, sizeof(*state));
        open_cfw_ancc_memory_zero(
            OPEN_CFW_ANCC_PRODUCT,
            sizeof(struct open_cfw_ancc_product_notification)
        );
        state->handler_id = (open_cfw_ancc_u8)a;
        OPEN_CFW_ANCC_PROFILE_CONTEXT = (void *)b;
        OPEN_CFW_ANCC_PROFILE_ARGUMENT = (void *)c;
        OPEN_CFW_ANCC_HANDLE_LIST = b == 0U
            ? (open_cfw_ancc_u16 *)0
            : (open_cfw_ancc_u16 *)(b + 0x30U);
        open_cfw_ancc_reset_inline();
        return 0U;
    case OPEN_CFW_ANCC_OP_PROCESS_MESSAGE: {
        struct open_cfw_ancc_att_event *message =
            (struct open_cfw_ancc_att_event *)b;
        if (message == (struct open_cfw_ancc_att_event *)0) {
            return 0U;
        }
        if (message->event == 5U || message->event == 13U
            || message->event == 14U) {
            return open_cfw_ancc_dispatch(
                OPEN_CFW_ANCC_OP_VALUE_GATE,
                (open_cfw_ancc_word)message, 0U, 0U
            );
        }
        if (message->event == 0x27U
            && open_cfw_cordio_dm_connection_role(
                (open_cfw_ancc_u8)message->parameter) == 1U) {
            state->connection_id = (open_cfw_ancc_u8)message->parameter;
            state->handles = OPEN_CFW_ANCC_HANDLE_LIST;
            open_cfw_ancc_reset_inline();
        } else if (message->event == 0x28U
            && open_cfw_cordio_dm_connection_role(
                (open_cfw_ancc_u8)message->parameter) == 1U) {
            state->connection_id = 0U;
            open_cfw_ancc_reset_inline();
        } else if (message->event == 0xA2U) {
            if (open_cfw_ancc_pop_inline() != 0) {
                open_cfw_ancc_u16 index = state->active.handle;
                (void)open_cfw_ancc_get_notification_inline(
                    state->handles, state->list[index].uid
                );
                if (state->connection_id != 0U) {
                    open_cfw_event_loop_push_delayed(
                        open_cfw_ancc_get_next_notification_handler,
                        0xA2U, 200U
                    );
                }
            } else {
                open_cfw_event_loop_remove_delayed(
                    open_cfw_ancc_get_next_notification_handler
                );
            }
        }
        return 0U;
    }
    case OPEN_CFW_ANCC_OP_DISCOVER:
        if (open_cfw_ancc_product_role() != 1U) {
            return 0U;
        }
        open_cfw_ancc_discover_service(
            (open_cfw_ancc_u8)a, 16U,
            (const open_cfw_ancc_u8 *)0x00787FC0U, 5U,
            (const void *)0x200030BCU, (open_cfw_ancc_u16 *)b
        );
        return 1U;
    case OPEN_CFW_ANCC_OP_GET_ACTIVE:
        return (open_cfw_ancc_word)OPEN_CFW_ANCC_PRODUCT;
    default:
        return 0U;
    }
}
#endif

#define OPEN_CFW_ANCC_WRAPPER0(selector, return_type, name, operation) \
    selector __attribute__((used, noinline)) return_type name(void) { \
        return (return_type)open_cfw_ancc_dispatch(operation, 0U, 0U, 0U); \
    }

#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_CONN_OPEN_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_connection_open_adapter(
    open_cfw_ancc_u8 connection_id, open_cfw_ancc_u16 *handles
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_CONN_OPEN,
        connection_id, (open_cfw_ancc_word)handles, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_CONN_CLOSE_ONLY)
OPEN_CFW_ANCC_WRAPPER0(, void, open_cfw_ancc_connection_close_adapter,
    OPEN_CFW_ANCC_OP_CONN_CLOSE)
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_NO_CONNECTION_ONLY)
OPEN_CFW_ANCC_WRAPPER0(, int, open_cfw_ancc_no_connection_adapter,
    OPEN_CFW_ANCC_OP_NO_CONNECTION)
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_POP_ONLY)
OPEN_CFW_ANCC_WRAPPER0(, int, open_cfw_ancc_action_list_pop_adapter,
    OPEN_CFW_ANCC_OP_POP)
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_GET_NEXT_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_get_next_notification_handler(
    open_cfw_ancc_u8 event
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_GET_NEXT, event, 0U, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_GET_NOTIFICATION_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_get_notification_attributes(
    open_cfw_ancc_u16 *handles, open_cfw_ancc_u32 uid
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_GET_NOTIFICATION,
        (open_cfw_ancc_word)handles, uid, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_ACTION_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_perform_notification_action(
    open_cfw_ancc_u16 *handles, open_cfw_ancc_u32 uid,
    open_cfw_ancc_u8 action
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_ACTION,
        (open_cfw_ancc_word)handles, uid, action); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_GET_APP_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_get_app_attributes(
    open_cfw_ancc_u16 *handles, const open_cfw_ancc_u8 *app_id
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_GET_APP,
        (open_cfw_ancc_word)handles, (open_cfw_ancc_word)app_id, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_PUSH_ONLY)
__attribute__((used, noinline)) int open_cfw_ancc_action_list_push_adapter(
    const struct open_cfw_ancc_notification *notification
) { return (int)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_PUSH,
        (open_cfw_ancc_word)notification, 0U, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_SYNC_CALLBACK_ONLY)
__attribute__((used, noinline)) int open_cfw_ancc_rx_sync_event_callback(int value)
{ return (int)open_cfw_ancc_dispatch(
    OPEN_CFW_ANCC_OP_SYNC_CALLBACK, (open_cfw_ancc_word)value, 0U, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_COMPLETE_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_send_complete_notification(
    const void *payload, open_cfw_ancc_u16 length
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_COMPLETE,
        (open_cfw_ancc_word)payload, length, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_REMOVE_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_notification_remove_callback(
    const struct open_cfw_ancc_notification *notification
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_REMOVE,
        (open_cfw_ancc_word)notification, 0U, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_VALUE_UPDATE_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_notification_value_update(
    open_cfw_ancc_u16 *handles, struct open_cfw_ancc_att_event *event,
    open_cfw_ancc_u8 timer_event
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_VALUE_UPDATE,
        (open_cfw_ancc_word)handles, (open_cfw_ancc_word)event, timer_event); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_VALUE_GATE_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_value_update_gate(
    struct open_cfw_ancc_att_event *event
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_VALUE_GATE,
        (open_cfw_ancc_word)event, 0U, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_ATTRIBUTE_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_attribute_callback_adapter(
    struct open_cfw_ancc_active *active
) { (void)active; (void)open_cfw_ancc_dispatch(
        OPEN_CFW_ANCC_OP_ATTRIBUTE_CALLBACK, 0U, 0U, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_RESET_ONLY)
OPEN_CFW_ANCC_WRAPPER0(, void, open_cfw_ancc_reset_state_machine,
    OPEN_CFW_ANCC_OP_RESET)
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_INIT_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_profile_initialize(
    open_cfw_ancc_u8 handler_id, void *context, void *argument
) { (void)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_INIT, handler_id,
        (open_cfw_ancc_word)context, (open_cfw_ancc_word)argument); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_PROCESS_MESSAGE_ONLY)
__attribute__((used, noinline)) void open_cfw_ancc_profile_process_message(
    void *unused, struct open_cfw_ancc_att_event *message
) { (void)unused; (void)open_cfw_ancc_dispatch(
        OPEN_CFW_ANCC_OP_PROCESS_MESSAGE, 0U,
        (open_cfw_ancc_word)message, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_DISCOVER_ONLY)
__attribute__((used, noinline)) int open_cfw_ancc_service_discover(
    open_cfw_ancc_u8 connection_id, open_cfw_ancc_u16 *handles
) { return (int)open_cfw_ancc_dispatch(OPEN_CFW_ANCC_OP_DISCOVER,
        connection_id, (open_cfw_ancc_word)handles, 0U); }
#endif
#if defined(OPEN_CFW_ANCC_PROFILE_BUILD_ALL) || defined(OPEN_CFW_ANCC_PROFILE_GET_ACTIVE_ONLY)
OPEN_CFW_ANCC_WRAPPER0(, void *, open_cfw_ancc_get_active_notification,
    OPEN_CFW_ANCC_OP_GET_ACTIVE)
#endif
