/* SPDX-License-Identifier: Apache-2.0 */

/* G2 Cordio application-framework service-discovery state machine. */

typedef unsigned char open_cfw_app_disc_u8;
typedef unsigned short open_cfw_app_disc_u16;
typedef unsigned int open_cfw_app_disc_u32;

typedef void (*open_cfw_app_disc_callback_t)(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8
);

typedef struct {
    open_cfw_app_disc_u16 parameter;
    open_cfw_app_disc_u8 event;
    open_cfw_app_disc_u8 status;
    open_cfw_app_disc_u8 *value;
    open_cfw_app_disc_u16 value_length;
} open_cfw_app_disc_event_t;

typedef struct {
    void *discovery;
    open_cfw_app_disc_u16 *handle_list;
    open_cfw_app_disc_u8 connection_configuration_status;
    open_cfw_app_disc_u8 completion_status;
    open_cfw_app_disc_u8 handle_list_length;
    open_cfw_app_disc_u8 in_progress;
    open_cfw_app_disc_u8 already_secure;
    open_cfw_app_disc_u8 security_required;
    open_cfw_app_disc_u8 service_changed_pending;
    open_cfw_app_disc_u8 reserved;
} open_cfw_app_disc_control_t;

enum {
    OPEN_CFW_APP_DISC_CONNECTION_MAX = 3,
    OPEN_CFW_APP_DISC_IDLE = 0,
    OPEN_CFW_APP_DISC_SERVICE_IN_PROGRESS = 1,
    OPEN_CFW_APP_DISC_CONFIG_IN_PROGRESS = 2,
    OPEN_CFW_APP_DISC_READ_HASH_IN_PROGRESS = 3,
    OPEN_CFW_APP_DISC_SECURITY_REQUIRED = 2,
    OPEN_CFW_APP_DISC_START = 3,
    OPEN_CFW_APP_DISC_COMPLETE = 4,
    OPEN_CFW_APP_DISC_FAILED = 5,
    OPEN_CFW_APP_DISC_CONFIG_START = 6,
    OPEN_CFW_APP_DISC_CONNECTION_CONFIG_START = 7,
    OPEN_CFW_APP_DISC_CONFIG_COMPLETE = 8,
    OPEN_CFW_APP_DISC_ATT_FIND_INFO_RESPONSE = 2,
    OPEN_CFW_APP_DISC_ATT_FIND_SERVICE_RESPONSE = 3,
    OPEN_CFW_APP_DISC_ATT_READ_BY_TYPE_RESPONSE = 4,
    OPEN_CFW_APP_DISC_ATT_READ_RESPONSE = 5,
    OPEN_CFW_APP_DISC_ATT_WRITE_RESPONSE = 9,
    OPEN_CFW_APP_DISC_ATT_SUCCESS = 0,
    OPEN_CFW_APP_DISC_ATT_AUTH_ERROR = 5,
    OPEN_CFW_APP_DISC_ATT_ENCRYPTION_ERROR = 15,
    OPEN_CFW_APP_DISC_ATT_DATABASE_OUT_OF_SYNC = 0x12,
    OPEN_CFW_APP_DISC_ATT_CONTINUING = 0x79,
    OPEN_CFW_APP_DISC_IDLE_CLIENT = 8,
    OPEN_CFW_APP_DISC_CONNECTION_IDLE = 0,
    OPEN_CFW_APP_DISC_CONNECTION_BUSY = 1,
    OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE = 0,
    OPEN_CFW_APP_DISC_DATABASE_HASH_LENGTH = 16,
    OPEN_CFW_APP_DISC_DISCOVERY_CONTROL_SIZE = 20
};

#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
typedef char open_cfw_app_disc_control_is_sixteen_bytes[
    sizeof(open_cfw_app_disc_control_t) == 16U ? 1 : -1
];
#define OPEN_CFW_APP_DISC_CONTROL \
    ((volatile open_cfw_app_disc_control_t *)0x200733FCU)
#define OPEN_CFW_APP_DISC_CALLBACK \
    (*(open_cfw_app_disc_callback_t volatile *)0x20074348U)
#define OPEN_CFW_APP_DISC_CONNECTION_STATE \
    ((volatile open_cfw_app_disc_u8 *)0x200717B0U)
#else
extern volatile open_cfw_app_disc_control_t
    open_cfw_app_disc_control[OPEN_CFW_APP_DISC_CONNECTION_MAX];
extern open_cfw_app_disc_callback_t open_cfw_app_disc_callback;
extern open_cfw_app_disc_u32
    open_cfw_app_disc_connection_database[OPEN_CFW_APP_DISC_CONNECTION_MAX];
#define OPEN_CFW_APP_DISC_CONTROL open_cfw_app_disc_control
#define OPEN_CFW_APP_DISC_CALLBACK open_cfw_app_disc_callback
#endif

open_cfw_app_disc_u32 open_cfw_app_disc_database_handle(
    open_cfw_app_disc_u8
);
open_cfw_app_disc_u32 open_cfw_app_disc_database_new_record(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8 *, int
);
open_cfw_app_disc_u8 open_cfw_cordio_dm_connection_role(
    open_cfw_app_disc_u8
);
open_cfw_app_disc_u8 *open_cfw_cordio_dm_connection_peer_address(
    open_cfw_app_disc_u8
);
open_cfw_app_disc_u8 open_cfw_cordio_dm_connection_peer_address_type(
    open_cfw_app_disc_u8
);
void open_cfw_app_disc_database_set_peer_hash(
    open_cfw_app_disc_u32, open_cfw_app_disc_u8 *
);
void open_cfw_app_disc_database_set_cache_by_hash(
    open_cfw_app_disc_u32, open_cfw_app_disc_u8
);
void open_cfw_app_disc_database_set_status(
    open_cfw_app_disc_u32, open_cfw_app_disc_u8
);
void open_cfw_app_disc_database_set_handle_list(
    open_cfw_app_disc_u32, open_cfw_app_disc_u16 *
);
int open_cfw_app_check_bonded(open_cfw_app_disc_u8);
void open_cfw_cordio_dm_connection_set_idle(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8, open_cfw_app_disc_u8
);
void *open_cfw_cordio_wsf_buffer_allocate_candidate(open_cfw_app_disc_u32);
void open_cfw_cordio_wsf_buffer_free_candidate(void *);
open_cfw_app_disc_u8 open_cfw_cordio_attc_discovery_service_complete(
    void *, open_cfw_app_disc_event_t *
);
void open_cfw_cordio_attc_discovery_characteristic_start(
    open_cfw_app_disc_u8, void *
);
open_cfw_app_disc_u8 open_cfw_cordio_attc_discovery_characteristic_complete(
    void *, open_cfw_app_disc_event_t *
);
open_cfw_app_disc_u8 open_cfw_cordio_attc_discovery_configuration_complete(
    open_cfw_app_disc_u8, void *
);
void open_cfw_cordio_attc_discover_service(
    open_cfw_app_disc_u8, void *, open_cfw_app_disc_u8,
    open_cfw_app_disc_u8 *
);
open_cfw_app_disc_u8 open_cfw_cordio_attc_start_configuration(
    open_cfw_app_disc_u8, void *
);
void open_cfw_cordio_attc_read_by_type_request(
    open_cfw_app_disc_u8, open_cfw_app_disc_u16,
    open_cfw_app_disc_u16, open_cfw_app_disc_u8,
    open_cfw_app_disc_u8 *, open_cfw_app_disc_u8
);
open_cfw_app_disc_u8 open_cfw_cordio_dm_connection_security_level(
    open_cfw_app_disc_u8
);

#ifndef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
open_cfw_app_disc_u8 *open_cfw_app_disc_test_record_hash(open_cfw_app_disc_u32);
open_cfw_app_disc_u16 *open_cfw_app_disc_test_record_handles(open_cfw_app_disc_u32);
open_cfw_app_disc_u8 open_cfw_app_disc_test_record_status(open_cfw_app_disc_u32);
void open_cfw_app_disc_test_prepare_service_control(
    void *, void *, open_cfw_app_disc_u16 *, open_cfw_app_disc_u8
);
void open_cfw_app_disc_test_prepare_configuration_control(
    void *, void *, open_cfw_app_disc_u8,
    open_cfw_app_disc_u16 *, open_cfw_app_disc_u8
);
#endif

void open_cfw_app_disc_configuration_start(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8
);
void open_cfw_app_disc_start(open_cfw_app_disc_u8);
void open_cfw_app_disc_restart(open_cfw_app_disc_u8);
void open_cfw_app_disc_parse_read_by_type(
    void *, open_cfw_app_disc_event_t *
);
void open_cfw_app_disc_parse_find_information(
    void *, open_cfw_app_disc_event_t *
);
void open_cfw_app_disc_process_att_message(open_cfw_app_disc_event_t *);
void open_cfw_app_disc_set_handle_list(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8,
    open_cfw_app_disc_u16 *
);
void open_cfw_app_disc_complete(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8
);
void open_cfw_app_disc_find_service(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8,
    open_cfw_app_disc_u8 *, open_cfw_app_disc_u8,
    void *, open_cfw_app_disc_u16 *
);
void open_cfw_app_disc_configure(
    open_cfw_app_disc_u8, open_cfw_app_disc_u8,
    open_cfw_app_disc_u8, void *, open_cfw_app_disc_u8,
    open_cfw_app_disc_u16 *
);
void open_cfw_app_disc_read_database_hash(open_cfw_app_disc_u8);

#if !defined(OPEN_CFW_CORDIO_APP_DISC_CFG_START_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_START_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_RESTART_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_PARSE_READ_TYPE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_PARSE_FIND_INFO_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_PROCESS_ATT_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_SET_HANDLE_LIST_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_FIND_SERVICE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_CONFIGURE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_DISC_READ_HASH_ONLY)
#define OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline int
open_cfw_app_disc_connection_valid(open_cfw_app_disc_u8 connection_id)
{
    return connection_id != 0U
        && connection_id <= OPEN_CFW_APP_DISC_CONNECTION_MAX;
}

static __attribute__((always_inline, unused)) inline volatile open_cfw_app_disc_control_t *
open_cfw_app_disc_state(open_cfw_app_disc_u8 connection_id)
{
    return &OPEN_CFW_APP_DISC_CONTROL[connection_id - 1U];
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_disc_notify(
    open_cfw_app_disc_u8 connection_id, open_cfw_app_disc_u8 status
)
{
    open_cfw_app_disc_callback_t callback = OPEN_CFW_APP_DISC_CALLBACK;
    if (callback != (open_cfw_app_disc_callback_t)0) {
        callback(connection_id, status);
    }
}

static __attribute__((always_inline, unused)) inline open_cfw_app_disc_u32
open_cfw_app_disc_connection_db_get(open_cfw_app_disc_u8 connection_id)
{
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    volatile open_cfw_app_disc_u8 *value = OPEN_CFW_APP_DISC_CONNECTION_STATE
        + (open_cfw_app_disc_u32)(connection_id - 1U) * 0x30U;
    return (open_cfw_app_disc_u32)value[0]
        | ((open_cfw_app_disc_u32)value[1] << 8U)
        | ((open_cfw_app_disc_u32)value[2] << 16U)
        | ((open_cfw_app_disc_u32)value[3] << 24U);
#else
    return open_cfw_app_disc_connection_database[connection_id - 1U];
#endif
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_disc_connection_db_set(
    open_cfw_app_disc_u8 connection_id, open_cfw_app_disc_u32 handle
)
{
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    volatile open_cfw_app_disc_u8 *value = OPEN_CFW_APP_DISC_CONNECTION_STATE
        + (open_cfw_app_disc_u32)(connection_id - 1U) * 0x30U;
    value[0] = (open_cfw_app_disc_u8)handle;
    value[1] = (open_cfw_app_disc_u8)(handle >> 8U);
    value[2] = (open_cfw_app_disc_u8)(handle >> 16U);
    value[3] = (open_cfw_app_disc_u8)(handle >> 24U);
#else
    open_cfw_app_disc_connection_database[connection_id - 1U] = handle;
#endif
}

static __attribute__((always_inline, unused)) inline open_cfw_app_disc_u8 *
open_cfw_app_disc_record_hash(open_cfw_app_disc_u32 handle)
{
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    return (open_cfw_app_disc_u8 *)(handle + 0x87U);
#else
    return open_cfw_app_disc_test_record_hash(handle);
#endif
}

static __attribute__((always_inline, unused)) inline open_cfw_app_disc_u16 *
open_cfw_app_disc_record_handles(open_cfw_app_disc_u32 handle)
{
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    return (open_cfw_app_disc_u16 *)(handle + 0x98U);
#else
    return open_cfw_app_disc_test_record_handles(handle);
#endif
}

static __attribute__((always_inline, unused)) inline open_cfw_app_disc_u8
open_cfw_app_disc_record_status(open_cfw_app_disc_u32 handle)
{
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    return *(volatile open_cfw_app_disc_u8 *)(handle + 0xC2U);
#else
    return open_cfw_app_disc_test_record_status(handle);
#endif
}

static __attribute__((always_inline, unused)) inline int
open_cfw_app_disc_hash_equal(
    const open_cfw_app_disc_u8 *left, const open_cfw_app_disc_u8 *right
)
{
    open_cfw_app_disc_u32 index;
    if (left == (const open_cfw_app_disc_u8 *)0
        || right == (const open_cfw_app_disc_u8 *)0) {
        return 0;
    }
    for (index = 0U; index < OPEN_CFW_APP_DISC_DATABASE_HASH_LENGTH; ++index) {
        if (left[index] != right[index]) {
            return 0;
        }
    }
    return 1;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_disc_copy_handles(
    open_cfw_app_disc_u16 *destination,
    const open_cfw_app_disc_u16 *source,
    open_cfw_app_disc_u8 count
)
{
    open_cfw_app_disc_u8 index;
    if (destination == (open_cfw_app_disc_u16 *)0
        || source == (const open_cfw_app_disc_u16 *)0) {
        return;
    }
    for (index = 0U; index < count; ++index) {
        destination[index] = source[index];
    }
}

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_CFG_START_ONLY)
void open_cfw_app_disc_configuration_start(
    open_cfw_app_disc_u8 connection_id, open_cfw_app_disc_u8 status
)
{
    volatile open_cfw_app_disc_control_t *state;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    if (status < OPEN_CFW_APP_DISC_CONFIG_COMPLETE) {
        open_cfw_app_disc_notify(connection_id, OPEN_CFW_APP_DISC_CONFIG_START);
    } else if (status == OPEN_CFW_APP_DISC_CONFIG_COMPLETE
               && state->connection_configuration_status == 0U) {
        open_cfw_app_disc_notify(
            connection_id, OPEN_CFW_APP_DISC_CONNECTION_CONFIG_START
        );
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_START_ONLY)
void open_cfw_app_disc_start(open_cfw_app_disc_u8 connection_id)
{
    volatile open_cfw_app_disc_control_t *state;
    open_cfw_app_disc_u32 handle;
    open_cfw_app_disc_u8 status;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    if (state->in_progress != OPEN_CFW_APP_DISC_IDLE) {
        return;
    }
    handle = open_cfw_app_disc_database_handle(connection_id);
    status = handle == OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE
        ? state->completion_status : OPEN_CFW_APP_DISC_START;
    if (status < OPEN_CFW_APP_DISC_COMPLETE) {
        open_cfw_app_disc_notify(connection_id, OPEN_CFW_APP_DISC_START);
    } else if (status != OPEN_CFW_APP_DISC_FAILED) {
        if (handle != OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE
            && state->handle_list != (open_cfw_app_disc_u16 *)0) {
            open_cfw_app_disc_copy_handles(
                state->handle_list, open_cfw_app_disc_record_handles(handle),
                state->handle_list_length
            );
        }
        open_cfw_app_disc_configuration_start(connection_id, status);
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_RESTART_ONLY)
void open_cfw_app_disc_restart(open_cfw_app_disc_u8 connection_id)
{
    volatile open_cfw_app_disc_control_t *state;
    open_cfw_app_disc_u32 handle;
    open_cfw_app_disc_u8 index;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    state->connection_configuration_status = 0U;
    state->completion_status = 0U;
    state->security_required = 0U;
    state->service_changed_pending = 0U;
    if (state->handle_list != (open_cfw_app_disc_u16 *)0) {
        for (index = 0U; index < state->handle_list_length; ++index) {
            state->handle_list[index] = 0U;
        }
    }
    handle = open_cfw_app_disc_database_handle(connection_id);
    if (handle != OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE) {
        open_cfw_app_disc_database_set_status(handle, 0U);
        open_cfw_app_disc_database_set_handle_list(handle, state->handle_list);
    }
    if (state->in_progress == OPEN_CFW_APP_DISC_CONFIG_IN_PROGRESS) {
        state->service_changed_pending = 1U;
    } else {
        state->in_progress = OPEN_CFW_APP_DISC_IDLE;
        open_cfw_app_disc_start(connection_id);
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_PARSE_READ_TYPE_ONLY)
void open_cfw_app_disc_parse_read_by_type(
    void *discovery, open_cfw_app_disc_event_t *message
)
{
    volatile open_cfw_app_disc_u8 sink = 0U;
    open_cfw_app_disc_u16 index;
    (void)discovery;
    if (message == (open_cfw_app_disc_event_t *)0
        || message->value == (open_cfw_app_disc_u8 *)0
        || message->value_length < 8U) {
        return;
    }
    for (index = 0U; index < message->value_length; ++index) {
        sink ^= message->value[index];
    }
    (void)sink;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_PARSE_FIND_INFO_ONLY)
void open_cfw_app_disc_parse_find_information(
    void *discovery, open_cfw_app_disc_event_t *message
)
{
    volatile open_cfw_app_disc_u8 sink = 0U;
    open_cfw_app_disc_u16 index;
    (void)discovery;
    if (message == (open_cfw_app_disc_event_t *)0
        || message->value == (open_cfw_app_disc_u8 *)0
        || message->value_length < 5U) {
        return;
    }
    for (index = 0U; index < message->value_length; ++index) {
        sink ^= message->value[index];
    }
    (void)sink;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_PROCESS_ATT_ONLY)
void open_cfw_app_disc_process_att_message(open_cfw_app_disc_event_t *message)
{
    volatile open_cfw_app_disc_control_t *state;
    open_cfw_app_disc_u8 connection_id;
    open_cfw_app_disc_u8 result;
    open_cfw_app_disc_u32 handle;
    open_cfw_app_disc_u8 *new_hash;
    if (message == (open_cfw_app_disc_event_t *)0) {
        return;
    }
    connection_id = (open_cfw_app_disc_u8)message->parameter;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    if (message->status == OPEN_CFW_APP_DISC_ATT_DATABASE_OUT_OF_SYNC) {
        open_cfw_app_disc_restart(connection_id);
    }
    if (state->in_progress == OPEN_CFW_APP_DISC_READ_HASH_IN_PROGRESS) {
        if (message->event != OPEN_CFW_APP_DISC_ATT_READ_BY_TYPE_RESPONSE) {
            return;
        }
        if (message->status != OPEN_CFW_APP_DISC_ATT_SUCCESS
            || message->value == (open_cfw_app_disc_u8 *)0
            || message->value_length < 19U) {
            open_cfw_app_disc_notify(connection_id, OPEN_CFW_APP_DISC_START);
            return;
        }
        state->in_progress = OPEN_CFW_APP_DISC_IDLE;
        handle = open_cfw_app_disc_database_handle(connection_id);
        if (handle == OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE) {
            handle = open_cfw_app_disc_database_new_record(
                open_cfw_cordio_dm_connection_peer_address_type(connection_id),
                open_cfw_cordio_dm_connection_peer_address(connection_id),
                open_cfw_cordio_dm_connection_role(connection_id) == 0U
            );
            open_cfw_app_disc_connection_db_set(connection_id, handle);
        }
        if (handle == OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE) {
            open_cfw_app_disc_notify(connection_id, OPEN_CFW_APP_DISC_START);
            return;
        }
        new_hash = message->value + 3U;
        if (!open_cfw_app_disc_hash_equal(
                open_cfw_app_disc_record_hash(handle), new_hash
            )) {
            open_cfw_app_disc_database_set_peer_hash(handle, new_hash);
            open_cfw_app_disc_database_set_cache_by_hash(handle, 1U);
            open_cfw_app_disc_notify(connection_id, OPEN_CFW_APP_DISC_START);
        } else {
            open_cfw_app_disc_copy_handles(
                state->handle_list, open_cfw_app_disc_record_handles(handle),
                state->handle_list_length
            );
            open_cfw_app_disc_configuration_start(
                connection_id, open_cfw_app_disc_record_status(handle)
            );
        }
        return;
    }
    if (state->in_progress == OPEN_CFW_APP_DISC_SERVICE_IN_PROGRESS) {
        if (message->event == OPEN_CFW_APP_DISC_ATT_FIND_SERVICE_RESPONSE) {
            result = open_cfw_cordio_attc_discovery_service_complete(
                state->discovery, message
            );
            if (result == OPEN_CFW_APP_DISC_ATT_SUCCESS) {
                open_cfw_cordio_attc_discovery_characteristic_start(
                    connection_id, state->discovery
                );
            } else if (result != OPEN_CFW_APP_DISC_ATT_CONTINUING) {
                open_cfw_cordio_dm_connection_set_idle(
                    connection_id, OPEN_CFW_APP_DISC_IDLE_CLIENT,
                    OPEN_CFW_APP_DISC_CONNECTION_IDLE
                );
                open_cfw_app_disc_notify(
                    connection_id, OPEN_CFW_APP_DISC_FAILED
                );
            }
        } else if (message->event == OPEN_CFW_APP_DISC_ATT_READ_BY_TYPE_RESPONSE
                   || message->event == OPEN_CFW_APP_DISC_ATT_FIND_INFO_RESPONSE) {
            result = open_cfw_cordio_attc_discovery_characteristic_complete(
                state->discovery, message
            );
            if (message->event == OPEN_CFW_APP_DISC_ATT_READ_BY_TYPE_RESPONSE) {
                open_cfw_app_disc_parse_read_by_type(state->discovery, message);
            } else {
                open_cfw_app_disc_parse_find_information(
                    state->discovery, message
                );
            }
            if (result == OPEN_CFW_APP_DISC_ATT_SUCCESS) {
                open_cfw_app_disc_notify(
                    connection_id, OPEN_CFW_APP_DISC_COMPLETE
                );
            } else if (result != OPEN_CFW_APP_DISC_ATT_CONTINUING) {
                open_cfw_cordio_dm_connection_set_idle(
                    connection_id, OPEN_CFW_APP_DISC_IDLE_CLIENT,
                    OPEN_CFW_APP_DISC_CONNECTION_IDLE
                );
                open_cfw_app_disc_notify(
                    connection_id, OPEN_CFW_APP_DISC_FAILED
                );
            }
        }
        return;
    }
    if (state->in_progress == OPEN_CFW_APP_DISC_CONFIG_IN_PROGRESS
        && (message->event == OPEN_CFW_APP_DISC_ATT_READ_RESPONSE
            || message->event == OPEN_CFW_APP_DISC_ATT_WRITE_RESPONSE)) {
        if (state->service_changed_pending != 0U) {
            state->service_changed_pending = 0U;
            state->in_progress = OPEN_CFW_APP_DISC_IDLE;
            open_cfw_app_disc_start(connection_id);
        } else if ((message->status == OPEN_CFW_APP_DISC_ATT_AUTH_ERROR
                    || message->status
                        == OPEN_CFW_APP_DISC_ATT_ENCRYPTION_ERROR)
                   && open_cfw_cordio_dm_connection_security_level(
                        connection_id
                    ) == 0U) {
            state->security_required = 1U;
            open_cfw_app_disc_notify(
                connection_id, OPEN_CFW_APP_DISC_SECURITY_REQUIRED
            );
        } else {
            result = open_cfw_cordio_attc_discovery_configuration_complete(
                connection_id, state->discovery
            );
            if (result != OPEN_CFW_APP_DISC_ATT_CONTINUING) {
                open_cfw_app_disc_notify(
                    connection_id, OPEN_CFW_APP_DISC_CONFIG_COMPLETE
                );
            }
        }
    } else if (state->in_progress == OPEN_CFW_APP_DISC_CONFIG_IN_PROGRESS
               && message->status != OPEN_CFW_APP_DISC_ATT_SUCCESS
               && message->status != OPEN_CFW_APP_DISC_ATT_CONTINUING) {
        open_cfw_cordio_dm_connection_set_idle(
            connection_id, OPEN_CFW_APP_DISC_IDLE_CLIENT,
            OPEN_CFW_APP_DISC_CONNECTION_IDLE
        );
        state->in_progress = OPEN_CFW_APP_DISC_IDLE;
        open_cfw_app_disc_notify(connection_id, OPEN_CFW_APP_DISC_FAILED);
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_SET_HANDLE_LIST_ONLY)
void open_cfw_app_disc_set_handle_list(
    open_cfw_app_disc_u8 connection_id,
    open_cfw_app_disc_u8 handle_list_length,
    open_cfw_app_disc_u16 *handle_list
)
{
    volatile open_cfw_app_disc_control_t *state;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    state->handle_list_length = handle_list_length;
    state->handle_list = handle_list;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_COMPLETE_ONLY)
void open_cfw_app_disc_complete(
    open_cfw_app_disc_u8 connection_id, open_cfw_app_disc_u8 status
)
{
    volatile open_cfw_app_disc_control_t *state;
    open_cfw_app_disc_u32 handle;
    open_cfw_app_disc_u8 maximum_status;
    int connection_configuration;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    open_cfw_cordio_dm_connection_set_idle(
        connection_id, OPEN_CFW_APP_DISC_IDLE_CLIENT,
        OPEN_CFW_APP_DISC_CONNECTION_IDLE
    );
    connection_configuration =
        status == OPEN_CFW_APP_DISC_CONFIG_COMPLETE
        && state->connection_configuration_status
            == OPEN_CFW_APP_DISC_CONNECTION_CONFIG_START;
    if (!connection_configuration) {
        state->completion_status = status;
    }
    state->in_progress = OPEN_CFW_APP_DISC_IDLE;
    if (state->discovery != (void *)0) {
        open_cfw_cordio_wsf_buffer_free_candidate(state->discovery);
        state->discovery = (void *)0;
    }
    handle = open_cfw_app_disc_database_handle(connection_id);
    if (handle != OPEN_CFW_APP_DISC_DATABASE_HANDLE_NONE) {
        maximum_status = open_cfw_app_check_bonded(connection_id)
            ? OPEN_CFW_APP_DISC_CONFIG_COMPLETE : OPEN_CFW_APP_DISC_COMPLETE;
        if (!connection_configuration && status <= maximum_status) {
            open_cfw_app_disc_database_set_status(handle, status);
        }
        if (state->handle_list != (open_cfw_app_disc_u16 *)0
            && status == OPEN_CFW_APP_DISC_COMPLETE) {
            open_cfw_app_disc_database_set_handle_list(
                handle, state->handle_list
            );
        }
    }
    if (status == OPEN_CFW_APP_DISC_CONFIG_COMPLETE) {
        state->connection_configuration_status =
            OPEN_CFW_APP_DISC_CONFIG_COMPLETE;
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_FIND_SERVICE_ONLY)
void open_cfw_app_disc_find_service(
    open_cfw_app_disc_u8 connection_id, open_cfw_app_disc_u8 uuid_length,
    open_cfw_app_disc_u8 *uuid, open_cfw_app_disc_u8 list_length,
    void *characteristic_list, open_cfw_app_disc_u16 *handle_list
)
{
    volatile open_cfw_app_disc_control_t *state;
    volatile open_cfw_app_disc_u8 *discovery;
    if (!open_cfw_app_disc_connection_valid(connection_id)
        || uuid == (open_cfw_app_disc_u8 *)0) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    if (state->discovery == (void *)0) {
        state->discovery = open_cfw_cordio_wsf_buffer_allocate_candidate(
            OPEN_CFW_APP_DISC_DISCOVERY_CONTROL_SIZE
        );
    }
    if (state->discovery == (void *)0) {
        return;
    }
    open_cfw_cordio_dm_connection_set_idle(
        connection_id, OPEN_CFW_APP_DISC_IDLE_CLIENT,
        OPEN_CFW_APP_DISC_CONNECTION_BUSY
    );
    state->in_progress = OPEN_CFW_APP_DISC_SERVICE_IN_PROGRESS;
    discovery = (volatile open_cfw_app_disc_u8 *)state->discovery;
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    *(void * volatile *)(void *)(discovery + 0U) = characteristic_list;
    *(open_cfw_app_disc_u16 * volatile *)(void *)(discovery + 4U) = handle_list;
    discovery[12] = list_length;
#else
    (void)discovery;
    open_cfw_app_disc_test_prepare_service_control(
        state->discovery, characteristic_list, handle_list, list_length
    );
#endif
    open_cfw_cordio_attc_discover_service(
        connection_id, state->discovery, uuid_length, uuid
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_CONFIGURE_ONLY)
void open_cfw_app_disc_configure(
    open_cfw_app_disc_u8 connection_id, open_cfw_app_disc_u8 status,
    open_cfw_app_disc_u8 configuration_list_length,
    void *configuration_list, open_cfw_app_disc_u8 handle_list_length,
    open_cfw_app_disc_u16 *handle_list
)
{
    volatile open_cfw_app_disc_control_t *state;
    volatile open_cfw_app_disc_u8 *discovery;
    open_cfw_app_disc_u8 result;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    if (state->discovery == (void *)0) {
        state->discovery = open_cfw_cordio_wsf_buffer_allocate_candidate(
            OPEN_CFW_APP_DISC_DISCOVERY_CONTROL_SIZE
        );
    }
    if (state->discovery == (void *)0) {
        return;
    }
    open_cfw_cordio_dm_connection_set_idle(
        connection_id, OPEN_CFW_APP_DISC_IDLE_CLIENT,
        OPEN_CFW_APP_DISC_CONNECTION_BUSY
    );
    state->in_progress = OPEN_CFW_APP_DISC_CONFIG_IN_PROGRESS;
    if (status == OPEN_CFW_APP_DISC_CONNECTION_CONFIG_START) {
        state->connection_configuration_status = status;
    }
    discovery = (volatile open_cfw_app_disc_u8 *)state->discovery;
#ifdef OPEN_CFW_CORDIO_APP_DISC_PRODUCTION
    *(void * volatile *)(void *)(discovery + 8U) = configuration_list;
    discovery[13] = configuration_list_length;
    *(open_cfw_app_disc_u16 * volatile *)(void *)(discovery + 4U) = handle_list;
    discovery[12] = handle_list_length;
#else
    (void)discovery;
    open_cfw_app_disc_test_prepare_configuration_control(
        state->discovery, configuration_list, configuration_list_length,
        handle_list, handle_list_length
    );
#endif
    result = open_cfw_cordio_attc_start_configuration(
        connection_id, state->discovery
    );
    if (result == OPEN_CFW_APP_DISC_ATT_SUCCESS) {
        open_cfw_app_disc_notify(
            connection_id, OPEN_CFW_APP_DISC_CONFIG_COMPLETE
        );
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_DISC_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_DISC_READ_HASH_ONLY)
void open_cfw_app_disc_read_database_hash(open_cfw_app_disc_u8 connection_id)
{
    open_cfw_app_disc_u8 database_hash_uuid[2] = {0x2AU, 0x2BU};
    volatile open_cfw_app_disc_control_t *state;
    if (!open_cfw_app_disc_connection_valid(connection_id)) {
        return;
    }
    state = open_cfw_app_disc_state(connection_id);
    if (state->in_progress != OPEN_CFW_APP_DISC_IDLE) {
        return;
    }
    state->in_progress = OPEN_CFW_APP_DISC_READ_HASH_IN_PROGRESS;
    open_cfw_cordio_attc_read_by_type_request(
        connection_id, 1U, 0xFFFFU, 2U, database_hash_uuid, 0U
    );
}
#endif
