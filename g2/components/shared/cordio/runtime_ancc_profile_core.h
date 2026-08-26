/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_RUNTIME_ANCC_PROFILE_CORE_H
#define OPEN_CFW_RUNTIME_ANCC_PROFILE_CORE_H

typedef __UINT8_TYPE__ open_cfw_ancc_u8;
typedef __UINT16_TYPE__ open_cfw_ancc_u16;
typedef __UINT32_TYPE__ open_cfw_ancc_u32;

#ifdef OPEN_CFW_ANCC_CORE_INLINE
#define OPEN_CFW_ANCC_CORE_API \
    static __attribute__((always_inline)) inline
#else
#define OPEN_CFW_ANCC_CORE_API
#endif

enum {
    OPEN_CFW_ANCC_LIST_CAPACITY = 64,
    OPEN_CFW_ANCC_APP_ID_CAPACITY = 64,
    OPEN_CFW_ANCC_ATTRIBUTE_CAPACITY = 512,
    OPEN_CFW_ANCC_ATTRIBUTE_COUNT = 8,
    OPEN_CFW_ANCC_HANDLE_NOTIFICATION_SOURCE = 0,
    OPEN_CFW_ANCC_HANDLE_NOTIFICATION_SOURCE_CCC = 1,
    OPEN_CFW_ANCC_HANDLE_CONTROL_POINT = 2,
    OPEN_CFW_ANCC_HANDLE_DATA_SOURCE = 3,
    OPEN_CFW_ANCC_HANDLE_DATA_SOURCE_CCC = 4,
    OPEN_CFW_ANCC_HANDLE_COUNT = 5,
    OPEN_CFW_ANCC_HANDLE_NONE = 0,
    OPEN_CFW_ANCC_CONN_NONE = 0,
    OPEN_CFW_ANCC_EVENT_ADDED = 0,
    OPEN_CFW_ANCC_EVENT_MODIFIED = 1,
    OPEN_CFW_ANCC_EVENT_REMOVED = 2,
    OPEN_CFW_ANCC_COMMAND_NOTIFICATION_ATTRIBUTES = 0,
    OPEN_CFW_ANCC_COMMAND_APP_ATTRIBUTES = 1,
    OPEN_CFW_ANCC_COMMAND_PERFORM_ACTION = 2,
    OPEN_CFW_ANCC_PARSE_COMMAND = 0,
    OPEN_CFW_ANCC_PARSE_ATTRIBUTE = 1,
    OPEN_CFW_ANCC_PARSE_FRAGMENT = 2
};

struct open_cfw_ancc_notification {
    open_cfw_ancc_u8 event_id;
    open_cfw_ancc_u8 event_flags;
    open_cfw_ancc_u8 category_id;
    open_cfw_ancc_u8 category_count;
    open_cfw_ancc_u32 uid;
    open_cfw_ancc_u8 valid;
    open_cfw_ancc_u8 reserved[3];
};

struct open_cfw_ancc_active {
    open_cfw_ancc_u16 handle;
    open_cfw_ancc_u8 parse_state;
    open_cfw_ancc_u8 reserved0;
    open_cfw_ancc_u16 buffer_length;
    open_cfw_ancc_u16 parse_index;
    open_cfw_ancc_u16 attribute_length;
    open_cfw_ancc_u8 attribute_id;
    open_cfw_ancc_u8 reserved1;
    open_cfw_ancc_u16 attribute_count;
    open_cfw_ancc_u8 command_id;
    open_cfw_ancc_u8 reserved2;
    open_cfw_ancc_u32 notification_uid;
};

struct open_cfw_ancc_state {
    open_cfw_ancc_u8 connection_id;
    open_cfw_ancc_u8 handler_id;
    open_cfw_ancc_u16 reserved;
    open_cfw_ancc_u16 *handles;
    struct open_cfw_ancc_active active;
    struct open_cfw_ancc_notification list[OPEN_CFW_ANCC_LIST_CAPACITY];
    open_cfw_ancc_u8 app_id[OPEN_CFW_ANCC_APP_ID_CAPACITY];
    open_cfw_ancc_u8 data[OPEN_CFW_ANCC_ATTRIBUTE_CAPACITY];
};

typedef int (*open_cfw_ancc_write_fn)(
    void *context,
    open_cfw_ancc_u8 connection_id,
    open_cfw_ancc_u16 handle,
    const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
);
typedef void (*open_cfw_ancc_attribute_fn)(
    void *context,
    const struct open_cfw_ancc_state *state
);
typedef void (*open_cfw_ancc_complete_fn)(
    void *context,
    const struct open_cfw_ancc_state *state,
    open_cfw_ancc_u32 uid
);
typedef void (*open_cfw_ancc_remove_fn)(
    void *context,
    const struct open_cfw_ancc_notification *notification
);

struct open_cfw_ancc_hooks {
    void *context;
    open_cfw_ancc_write_fn write;
    open_cfw_ancc_attribute_fn attribute;
    open_cfw_ancc_complete_fn complete;
    open_cfw_ancc_remove_fn remove;
};

OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_state_initialize(
    struct open_cfw_ancc_state *state,
    open_cfw_ancc_u8 handler_id
);
OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_connection_open(
    struct open_cfw_ancc_state *state,
    open_cfw_ancc_u8 connection_id,
    open_cfw_ancc_u16 *handles
);
OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_connection_close(
    struct open_cfw_ancc_state *state
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_no_connection_active(
    const struct open_cfw_ancc_state *state
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_notification_push(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_notification *notification
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_notification_pop(
    struct open_cfw_ancc_state *state
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_request_notification_attributes(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    open_cfw_ancc_u32 uid
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_request_app_attributes(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    const open_cfw_ancc_u8 *app_id
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_perform_action(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    open_cfw_ancc_u32 uid,
    open_cfw_ancc_u8 action
);
OPEN_CFW_ANCC_CORE_API void open_cfw_ancc_parser_reset(
    struct open_cfw_ancc_state *state
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_feed_data(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
);
OPEN_CFW_ANCC_CORE_API int open_cfw_ancc_feed_value(
    struct open_cfw_ancc_state *state,
    const struct open_cfw_ancc_hooks *hooks,
    open_cfw_ancc_u16 handle,
    const open_cfw_ancc_u8 *value,
    open_cfw_ancc_u16 length
);

#if __UINTPTR_MAX__ == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_ancc_notification) == 12U,
    "G2 ANCC notification ABI");
_Static_assert(__builtin_offsetof(struct open_cfw_ancc_state, active) == 8U,
    "G2 ANCC active-state offset");
_Static_assert(__builtin_offsetof(struct open_cfw_ancc_state, list) == 0x1CU,
    "G2 ANCC action-list offset");
_Static_assert(__builtin_offsetof(struct open_cfw_ancc_state, app_id) == 0x31CU,
    "G2 ANCC app-id offset");
_Static_assert(__builtin_offsetof(struct open_cfw_ancc_state, data) == 0x35CU,
    "G2 ANCC attribute-buffer offset");
_Static_assert(sizeof(struct open_cfw_ancc_state) == 0x55CU,
    "G2 ANCC control-block ABI");
#endif

#endif
