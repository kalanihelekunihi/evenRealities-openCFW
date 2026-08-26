/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_atts_main.h"

#if !defined(OPEN_CFW_ATTS_MAIN_DATA_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CONNECTION_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_MESSAGE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CONTROL_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_ERROR_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CLEAR_WRITES_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_DISCOVERY_BUSY_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_PROCESS_HASH_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CHECK_HASH_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_HASHABLE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CCB_ID_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CCB_HANDLE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_HASH_STRING_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_CALCULATE_HASH_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_ADD_GROUP_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_REMOVE_GROUP_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_AUTHOR_REGISTER_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_SET_ATTRIBUTE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_GET_ATTRIBUTE_ONLY) && \
    !defined(OPEN_CFW_ATTS_MAIN_ERROR_TEST_ONLY)
#define OPEN_CFW_ATTS_MAIN_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_MAIN_PRODUCTION
#define OPEN_CFW_ATTS_MAIN_CONNECTIONS \
    ((struct open_cfw_cordio_atts_ind_connection *)0x2006E5F0U)
#define OPEN_CFW_ATTS_MAIN_PREPARED_BASE \
    ((struct open_cfw_cordio_wsf_queue_candidate *)0x2006E828U)
#define OPEN_CFW_ATTS_MAIN_GROUP_QUEUE \
    (*(struct open_cfw_cordio_wsf_queue_candidate *)0x2006E848U)
#define OPEN_CFW_ATTS_MAIN_INDICATION_INTERFACE \
    (*(struct open_cfw_cordio_atts_interface **)0x2006E850U)
#define OPEN_CFW_ATTS_MAIN_SIGN_CALLBACK \
    (*(open_cfw_cordio_atts_message_callback_t *)0x2006E854U)
#define OPEN_CFW_ATTS_MAIN_AUTHOR_CALLBACK \
    (*(open_cfw_cordio_atts_authorization_callback_t *)0x2006E858U)
#define OPEN_CFW_ATTS_MAIN_CONTROL_BLOCKS \
    ((struct open_cfw_cordio_att_main_control_block *)0x200610ACU)
#define OPEN_CFW_ATTS_MAIN_SERVER_INTERFACE \
    (*(struct open_cfw_cordio_atts_interface **)0x200610ECU)
#define OPEN_CFW_ATTS_MAIN_APPLICATION_CALLBACK \
    (*(void (**)(struct open_cfw_cordio_att_event *))0x20061104U)
#define OPEN_CFW_ATTS_MAIN_HANDLER_ID (*(uint8_t *)0x2006110CU)
#define OPEN_CFW_ATTS_MAIN_ERROR_TEST (*(uint8_t *)0x2006110DU)
#define OPEN_CFW_ATTS_MAIN_PROCESSORS \
    ((open_cfw_cordio_atts_processor_t *)0x2000045CU)
#define OPEN_CFW_ATTS_MAIN_MINIMUM_LENGTH ((uint8_t *)0x0077E2D0U)
#define OPEN_CFW_ATTS_MAIN_CONFIGURATION \
    (*(struct open_cfw_cordio_att_configuration **)0x200004B4U)
#define OPEN_CFW_ATTS_MAIN_DEFAULT_INTERFACE \
    ((struct open_cfw_cordio_atts_interface *)0x007852E0U)
#define OPEN_CFW_ATTS_MAIN_STOCK_INTERFACE \
    ((struct open_cfw_cordio_atts_interface *)0x007852F0U)
#define OPEN_CFW_ATTS_MAIN_EMPTY_HANDLER \
    ((open_cfw_cordio_atts_message_callback_t)(uintptr_t)0x004B4EE7U)
#define OPEN_CFW_ATTS_MAIN_DATABASE_HASH_UUID ((uint8_t *)0x0078F54EU)
#define OPEN_CFW_ATTS_MAIN_HASHABLE_NEXT_VALUE (*(uint8_t *)0x20074F95U)
#define OPEN_CFW_ATTS_MAIN_SOURCE_FILE ((const char *)0x006DC9F4U)
#else
#define OPEN_CFW_ATTS_MAIN_CONNECTIONS \
    (&open_cfw_cordio_atts_main_connections[0][0])
#define OPEN_CFW_ATTS_MAIN_PREPARED_BASE \
    (&open_cfw_cordio_atts_main_prepared_write_queues[0])
#define OPEN_CFW_ATTS_MAIN_GROUP_QUEUE open_cfw_cordio_atts_main_group_queue
#define OPEN_CFW_ATTS_MAIN_INDICATION_INTERFACE \
    open_cfw_cordio_atts_main_indication_interface
#define OPEN_CFW_ATTS_MAIN_SIGN_CALLBACK \
    open_cfw_cordio_atts_main_sign_message_callback
#define OPEN_CFW_ATTS_MAIN_AUTHOR_CALLBACK \
    open_cfw_cordio_atts_authorization_callback
#define OPEN_CFW_ATTS_MAIN_CONTROL_BLOCKS \
    (&open_cfw_cordio_atts_main_control_blocks[0])
#define OPEN_CFW_ATTS_MAIN_SERVER_INTERFACE \
    open_cfw_cordio_atts_main_server_interface
#define OPEN_CFW_ATTS_MAIN_APPLICATION_CALLBACK \
    open_cfw_cordio_atts_main_application_callback
#define OPEN_CFW_ATTS_MAIN_HANDLER_ID open_cfw_cordio_atts_main_handler_id
#define OPEN_CFW_ATTS_MAIN_ERROR_TEST open_cfw_cordio_atts_main_error_test
#define OPEN_CFW_ATTS_MAIN_PROCESSORS open_cfw_cordio_atts_main_processor_table
#define OPEN_CFW_ATTS_MAIN_MINIMUM_LENGTH \
    open_cfw_cordio_atts_main_minimum_pdu_length
#define OPEN_CFW_ATTS_MAIN_CONFIGURATION open_cfw_cordio_att_configuration
#define OPEN_CFW_ATTS_MAIN_DEFAULT_INTERFACE ((struct open_cfw_cordio_atts_interface *)0)
#define OPEN_CFW_ATTS_MAIN_STOCK_INTERFACE ((struct open_cfw_cordio_atts_interface *)0)
#define OPEN_CFW_ATTS_MAIN_EMPTY_HANDLER ((open_cfw_cordio_atts_message_callback_t)0)
#define OPEN_CFW_ATTS_MAIN_DATABASE_HASH_UUID \
    open_cfw_cordio_atts_database_hash_uuid
#define OPEN_CFW_ATTS_MAIN_HASHABLE_NEXT_VALUE \
    open_cfw_cordio_atts_main_hashable_next_value
#define OPEN_CFW_ATTS_MAIN_SOURCE_FILE "atts_main.c"
#endif

void open_cfw_cordio_wsf_task_lock(void);
void open_cfw_cordio_wsf_task_unlock(void);
void open_cfw_cordio_wsf_timer_start_seconds(
    struct open_cfw_cordio_wsf_timer *, uint32_t
);
void open_cfw_cordio_wsf_timer_stop(struct open_cfw_cordio_wsf_timer *);
void open_cfw_cordio_wsf_assert_candidate(const char *, uint16_t);

static __attribute__((unused)) uint16_t open_cfw_cordio_atts_main_u16(
    const uint8_t *value
)
{
    return (uint16_t)value[0] | ((uint16_t)value[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_atts_main_put_u16(
    uint8_t **destination, uint16_t value
)
{
    *(*destination)++ = (uint8_t)value;
    *(*destination)++ = (uint8_t)(value >> 8);
}

static __attribute__((unused)) void open_cfw_cordio_atts_main_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length--;
    }
}

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_DATA_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_data_callback(
    uint16_t handle, uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_ind_connection *connection;
    open_cfw_cordio_atts_processor_t processor;
    uint16_t attribute_handle = 0U;
    uint8_t opcode, method, error;
    connection = open_cfw_cordio_atts_ind_connection_by_handle(handle, 0U);
    if ((connection == NULL) || (length < 1U)) {
        return;
    }
    opcode = packet[8];
    if ((opcode <= OPEN_CFW_ATTS_MAIN_WRITE_REQUEST)
        || ((opcode >= OPEN_CFW_ATTS_MAIN_PREPARE_WRITE_REQUEST)
            && (opcode <= OPEN_CFW_ATTS_MAIN_VALUE_CONFIRMATION))) {
        method = (uint8_t)(opcode >> 1);
    } else if (opcode == OPEN_CFW_ATTS_MAIN_WRITE_COMMAND) {
        method = OPEN_CFW_ATTS_MAIN_METHOD_WRITE_COMMAND;
    } else if (opcode == OPEN_CFW_ATTS_MAIN_READ_MULTIPLE_VARIABLE_REQUEST) {
        method = OPEN_CFW_ATTS_MAIN_METHOD_READ_MULTIPLE_VARIABLE;
    } else if (opcode == OPEN_CFW_ATTS_MAIN_SIGNED_WRITE_COMMAND) {
        method = OPEN_CFW_ATTS_MAIN_METHOD_SIGNED_WRITE_COMMAND;
    } else {
        method = 0U;
    }
    if (((connection->main->bearer[0].control
                & OPEN_CFW_ATTS_MAIN_RESPONSE_PENDING) != 0U)
        && (method != 15U)) {
        return;
    }
    error = open_cfw_cordio_atts_csf_act_client_state(handle, opcode, packet);
    if (error != 0U) {
        if (length < 3U) {
            return;
        }
        attribute_handle = open_cfw_cordio_atts_main_u16(packet + 9U);
    }
    if (error == 0U) {
        processor = OPEN_CFW_ATTS_MAIN_PROCESSORS[method];
        if (processor != NULL) {
            if (length >= OPEN_CFW_ATTS_MAIN_MINIMUM_LENGTH[method]) {
                processor(
                    (struct open_cfw_cordio_atts_connection_control_block *)connection,
                    length, packet
                );
                error = 0U;
            } else {
                error = OPEN_CFW_ATTS_MAIN_ERR_INVALID_PDU;
            }
        } else {
            error = OPEN_CFW_ATTS_MAIN_ERR_NOT_SUPPORTED;
        }
    }
    if ((error != 0U) && (opcode != OPEN_CFW_ATTS_MAIN_MTU_REQUEST)
        && (opcode != OPEN_CFW_ATTS_MAIN_VALUE_CONFIRMATION)
        && ((opcode & OPEN_CFW_ATTS_MAIN_COMMAND_MASK) == 0U)) {
        open_cfw_cordio_atts_error_response(
            connection->main, 0U, opcode, attribute_handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CONNECTION_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_connection_callback(
    struct open_cfw_cordio_att_main_control_block *main,
    struct open_cfw_cordio_dm_event *event
)
{
    uint8_t slot;
    struct open_cfw_cordio_atts_ind_connection *connection;
    if (event->header.event == OPEN_CFW_ATTS_MAIN_CONNECTION_CLOSE_EVENT) {
        for (slot = 0U; slot < 3U; slot++) {
            connection = OPEN_CFW_ATTS_MAIN_CONNECTIONS
                + (uint32_t)(main->connection_id-1U)*3U + slot;
#ifdef OPEN_CFW_ATTS_MAIN_PRODUCTION
            open_cfw_cordio_atts_clear_prepared_writes(
                (struct open_cfw_cordio_atts_connection_control_block *)connection
            );
#else
            {
                struct open_cfw_cordio_atts_connection_control_block proxy = {0};
                proxy.main = main;
                proxy.connection_id = main->connection_id;
                proxy.slot = slot;
                open_cfw_cordio_atts_clear_prepared_writes(&proxy);
            }
#endif
            if ((open_cfw_cordio_dm_connection_check_idle(main->connection_id)
                    & OPEN_CFW_ATTS_MAIN_IDLE_DISCOVERY) != 0U) {
                open_cfw_cordio_wsf_timer_stop(&connection->idle_timer);
            }
        }
    }
    OPEN_CFW_ATTS_MAIN_INDICATION_INTERFACE->connection_callback(main, event);
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_MESSAGE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_message_callback(
    struct open_cfw_cordio_wsf_message_header *message
)
{
    if (message->event == OPEN_CFW_ATTS_MAIN_IDLE_TIMEOUT_EVENT) {
        open_cfw_cordio_dm_connection_set_idle(
            (uint8_t)message->parameter, OPEN_CFW_ATTS_MAIN_IDLE_DISCOVERY,
            OPEN_CFW_ATTS_MAIN_CONNECTION_IDLE
        );
    } else if (message->event <= OPEN_CFW_ATTS_MAIN_IND_TIMEOUT_EVENT) {
        OPEN_CFW_ATTS_MAIN_INDICATION_INTERFACE->message_callback(message);
    } else if (message->event == OPEN_CFW_ATTS_MAIN_SIGN_COMPLETE_EVENT) {
        OPEN_CFW_ATTS_MAIN_SIGN_CALLBACK(message);
    } else if (message->event == OPEN_CFW_ATTS_MAIN_HASH_COMPLETE_EVENT) {
        open_cfw_cordio_atts_process_database_hash_update(
            (struct open_cfw_cordio_sec_cmac_message *)message
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CONTROL_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_l2c_control_callback(
    struct open_cfw_cordio_wsf_message_header *message
)
{
    OPEN_CFW_ATTS_MAIN_INDICATION_INTERFACE->control_callback(message);
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_ERROR_RESPONSE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_error_response(
    struct open_cfw_cordio_att_main_control_block *main, uint8_t slot,
    uint8_t opcode, uint16_t handle, uint8_t reason
)
{
    uint8_t *buffer = open_cfw_cordio_att_message_allocate(13U);
    uint8_t *output;
    if (buffer != NULL) {
        output = buffer + 8U;
        *output++ = OPEN_CFW_ATTS_MAIN_ERROR_RESPONSE;
        *output++ = opcode;
        open_cfw_cordio_atts_main_put_u16(&output, handle);
        *output = reason;
        open_cfw_cordio_att_l2c_data_request(main, slot, 5U, buffer);
    }
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CLEAR_WRITES_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_clear_prepared_writes(
    struct open_cfw_cordio_atts_connection_control_block *connection
)
{
    void *buffer;
    struct open_cfw_cordio_wsf_queue_candidate *queue =
        OPEN_CFW_ATTS_MAIN_PREPARED_BASE + connection->connection_id;
    while ((buffer = open_cfw_cordio_wsf_queue_dequeue_candidate(queue)) != NULL) {
        open_cfw_cordio_wsf_buffer_free_candidate(buffer);
    }
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_DISCOVERY_BUSY_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_discovery_busy(
    struct open_cfw_cordio_atts_connection_control_block *connection
)
{
    if (OPEN_CFW_ATTS_MAIN_CONFIGURATION->discovery_idle_timeout > 0U) {
        uint8_t *timer = connection->idle_timer;
        open_cfw_cordio_dm_connection_set_idle(
            connection->main->connection_id,
            OPEN_CFW_ATTS_MAIN_IDLE_DISCOVERY,
            OPEN_CFW_ATTS_MAIN_CONNECTION_BUSY
        );
        timer[12] = OPEN_CFW_ATTS_MAIN_HANDLER_ID;
        timer[6] = OPEN_CFW_ATTS_MAIN_IDLE_TIMEOUT_EVENT;
        timer[4] = connection->main->connection_id;
        timer[5] = 0U;
        open_cfw_cordio_wsf_timer_start_seconds(
            (struct open_cfw_cordio_wsf_timer *)timer,
            OPEN_CFW_ATTS_MAIN_CONFIGURATION->discovery_idle_timeout
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_PROCESS_HASH_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_database_hash_update(
    struct open_cfw_cordio_sec_cmac_message *message
)
{
    struct open_cfw_cordio_att_event event = {0};
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    uint16_t handle;
    uint8_t left, right, index;
    event.header.event = OPEN_CFW_ATTS_MAIN_DB_HASH_EVENT;
    event.value_length = OPEN_CFW_ATTS_MAIN_DATABASE_HASH_LENGTH;
    if (message->plaintext != NULL) {
        open_cfw_cordio_wsf_buffer_free_candidate(message->plaintext);
        message->plaintext = NULL;
    }
    for (index = 0U; index < 8U; index++) {
        left = message->ciphertext[index];
        right = message->ciphertext[15U-index];
        message->ciphertext[index] = right;
        message->ciphertext[15U-index] = left;
    }
    event.value = message->ciphertext;
    handle = open_cfw_cordio_atts_find_uuid_in_range(
        1U, 0xFFFFU, 2U, OPEN_CFW_ATTS_MAIN_DATABASE_HASH_UUID,
        &attribute, &group
    );
    if (handle != 0U) {
        open_cfw_cordio_atts_main_copy(
            attribute->value, event.value, OPEN_CFW_ATTS_MAIN_DATABASE_HASH_LENGTH
        );
        if ((attribute->settings & OPEN_CFW_ATTS_MAIN_SET_VARIABLE_LENGTH) != 0U) {
            *attribute->length = OPEN_CFW_ATTS_MAIN_DATABASE_HASH_LENGTH;
        }
    }
    open_cfw_cordio_atts_csf_set_hash_update_status(0U);
    OPEN_CFW_ATTS_MAIN_APPLICATION_CALLBACK(&event);
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CHECK_HASH_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_check_pending_database_hash_read_response(void)
{
    uint8_t index;
    for (index = 0U; index < 3U; index++) {
        struct open_cfw_cordio_att_main_control_block *main =
            &OPEN_CFW_ATTS_MAIN_CONTROL_BLOCKS[index];
        struct open_cfw_cordio_atts_pending_database_hash_response *pending =
            main->pending_database_hash_response;
        if (pending != NULL) {
            uint8_t *buffer = open_cfw_cordio_att_message_allocate(
                (uint16_t)(main->bearer[0].mtu + 8U)
            );
            if (buffer != NULL) {
                struct open_cfw_cordio_atts_group *group;
                struct open_cfw_cordio_atts_attribute *attribute;
                uint8_t *output = buffer + 8U;
                *output++ = OPEN_CFW_ATTS_READ_TYPE_RESPONSE;
                *output++ = 18U;
                open_cfw_cordio_atts_main_put_u16(&output, pending->handle);
                attribute = open_cfw_cordio_atts_find_by_handle(
                    pending->handle, &group
                );
                if (attribute != NULL) {
                    open_cfw_cordio_atts_main_copy(
                        output, attribute->value, *attribute->length
                    );
                    output += *attribute->length;
                    open_cfw_cordio_att_l2c_data_request(
                        main, 0U, (uint16_t)(output-(buffer+8U)), buffer
                    );
                } else {
                    open_cfw_cordio_atts_error_response(
                        main, 0U, OPEN_CFW_ATTS_READ_TYPE_REQUEST,
                        pending->start_handle, OPEN_CFW_ATTS_MAIN_ERR_NOT_FOUND
                    );
                }
            } else {
                open_cfw_cordio_atts_error_response(
                    main, 0U, OPEN_CFW_ATTS_READ_TYPE_REQUEST,
                    pending->start_handle, OPEN_CFW_ATTS_MAIN_ERR_RESOURCES
                );
            }
            open_cfw_cordio_wsf_buffer_free_candidate(pending);
            main->pending_database_hash_response = NULL;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_HASHABLE_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_atts_is_hashable_attribute(
    struct open_cfw_cordio_atts_attribute *attribute
)
{
    uint16_t length = 2U;
    uint16_t uuid;
    if (OPEN_CFW_ATTS_MAIN_HASHABLE_NEXT_VALUE) {
        OPEN_CFW_ATTS_MAIN_HASHABLE_NEXT_VALUE = 0U;
        return 0U;
    }
    uuid = open_cfw_cordio_atts_main_u16(attribute->uuid);
    switch (uuid) {
    case 0x2803U:
        OPEN_CFW_ATTS_MAIN_HASHABLE_NEXT_VALUE = 1U;
        /* fall through */
    case 0x2800U:
    case 0x2801U:
    case 0x2802U:
    case 0x2900U:
        length = (uint16_t)(length + *attribute->length);
        /* fall through */
    case 0x2901U:
    case 0x2902U:
    case 0x2903U:
    case 0x2905U:
        length = (uint16_t)(length
            + (((attribute->settings & OPEN_CFW_ATTS_MAIN_SET_UUID_128) != 0U)
                ? 16U : 2U));
        break;
    default:
        length = 0U;
        break;
    }
    return length;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CCB_ID_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_atts_ind_connection *
open_cfw_cordio_atts_ind_connection_by_id(uint8_t connection_id, uint8_t slot)
{
    if (open_cfw_cordio_dm_connection_in_use(connection_id)) {
        return OPEN_CFW_ATTS_MAIN_CONNECTIONS
            + (uint32_t)(connection_id-1U)*3U + slot;
    }
    return NULL;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CCB_HANDLE_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_atts_ind_connection *
open_cfw_cordio_atts_ind_connection_by_handle(uint16_t handle, uint8_t slot)
{
    uint8_t connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    return (connection_id == 0U) ? NULL : OPEN_CFW_ATTS_MAIN_CONNECTIONS
        + (uint32_t)(connection_id-1U)*3U + slot;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_INITIALIZE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_initialize(void)
{
    uint8_t connection_index, slot;
    OPEN_CFW_ATTS_MAIN_GROUP_QUEUE.head = NULL;
    OPEN_CFW_ATTS_MAIN_GROUP_QUEUE.tail = NULL;
    OPEN_CFW_ATTS_MAIN_INDICATION_INTERFACE = OPEN_CFW_ATTS_MAIN_DEFAULT_INTERFACE;
    OPEN_CFW_ATTS_MAIN_SIGN_CALLBACK = OPEN_CFW_ATTS_MAIN_EMPTY_HANDLER;
    for (connection_index = 0U; connection_index < 3U; connection_index++) {
        for (slot = 0U; slot < 3U; slot++) {
            struct open_cfw_cordio_atts_ind_connection *connection =
                OPEN_CFW_ATTS_MAIN_CONNECTIONS
                + (uint32_t)connection_index*3U + slot;
            connection->main = &OPEN_CFW_ATTS_MAIN_CONTROL_BLOCKS[connection_index];
            connection->connection_id = (uint8_t)(connection_index+1U);
            connection->slot = slot;
        }
    }
    OPEN_CFW_ATTS_MAIN_SERVER_INTERFACE = OPEN_CFW_ATTS_MAIN_STOCK_INTERFACE;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_HASH_STRING_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_hash_database_string(
    uint8_t *key, uint8_t *message, uint16_t length
)
{
    return open_cfw_cordio_security_cmac(
        key, message, length, OPEN_CFW_ATTS_MAIN_HANDLER_ID,
        0U, OPEN_CFW_ATTS_MAIN_HASH_COMPLETE_EVENT
    );
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_CALCULATE_HASH_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_calculate_database_hash(void)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    uint8_t *message, *output;
    uint8_t key[16] = {0};
    uint16_t message_length = 0U, handle, value_length;
    uint8_t count, uuid_length;
    for (group = OPEN_CFW_ATTS_MAIN_GROUP_QUEUE.head;
         group != NULL; group = group->next) {
        count = (uint8_t)(group->end_handle-group->start_handle+1U);
        for (attribute = group->attributes; count != 0U; count--, attribute++) {
            message_length = (uint16_t)(message_length
                + open_cfw_cordio_atts_is_hashable_attribute(attribute));
        }
    }
    message = open_cfw_cordio_wsf_buffer_allocate_candidate(message_length);
    if (message != NULL) {
        output = message;
        for (group = OPEN_CFW_ATTS_MAIN_GROUP_QUEUE.head;
             group != NULL; group = group->next) {
            handle = group->start_handle;
            for (attribute = group->attributes; handle <= group->end_handle;
                 handle++, attribute++) {
                value_length = open_cfw_cordio_atts_is_hashable_attribute(attribute);
                if (value_length != 0U) {
                    open_cfw_cordio_atts_main_put_u16(&output, handle);
                    uuid_length = ((attribute->settings
                        & OPEN_CFW_ATTS_MAIN_SET_UUID_128) != 0U) ? 16U : 2U;
                    open_cfw_cordio_atts_main_copy(
                        output, attribute->uuid, uuid_length
                    );
                    output += uuid_length;
                    if (value_length > (uint16_t)(uuid_length+2U)) {
                        open_cfw_cordio_atts_main_copy(
                            output, attribute->value, *attribute->length
                        );
                        output += *attribute->length;
                    }
                }
            }
        }
        if (open_cfw_cordio_atts_hash_database_string(
                key, message, message_length)) {
            return;
        }
    }
    open_cfw_cordio_wsf_assert_candidate(OPEN_CFW_ATTS_MAIN_SOURCE_FILE, 0U);
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_ADD_GROUP_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_add_group(struct open_cfw_cordio_atts_group *group)
{
    struct open_cfw_cordio_atts_group *element, *previous = NULL;
    open_cfw_cordio_wsf_task_lock();
    element = OPEN_CFW_ATTS_MAIN_GROUP_QUEUE.head;
    while (element != NULL) {
        if (group->start_handle < element->start_handle) {
            break;
        }
        previous = element;
        element = element->next;
    }
    open_cfw_cordio_wsf_queue_insert_candidate(
        &OPEN_CFW_ATTS_MAIN_GROUP_QUEUE, group, previous
    );
    open_cfw_cordio_atts_csf_set_hash_update_status(1U);
    open_cfw_cordio_wsf_task_unlock();
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_REMOVE_GROUP_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_remove_group(uint16_t start_handle)
{
    struct open_cfw_cordio_atts_group *element, *previous = NULL;
    open_cfw_cordio_wsf_task_lock();
    element = OPEN_CFW_ATTS_MAIN_GROUP_QUEUE.head;
    while (element != NULL) {
        if (element->start_handle == start_handle) {
            break;
        }
        previous = element;
        element = element->next;
    }
    if (element != NULL) {
        open_cfw_cordio_wsf_queue_remove_candidate(
            &OPEN_CFW_ATTS_MAIN_GROUP_QUEUE, element, previous
        );
    }
    open_cfw_cordio_atts_csf_set_hash_update_status(1U);
    open_cfw_cordio_wsf_task_unlock();
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_AUTHOR_REGISTER_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_authorization_register(
    open_cfw_cordio_atts_authorization_callback_t callback
)
{
    OPEN_CFW_ATTS_MAIN_AUTHOR_CALLBACK = callback;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_SET_ATTRIBUTE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_set_attribute(
    uint16_t handle, uint16_t value_length, uint8_t *value
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    uint8_t error = 0U;
    open_cfw_cordio_wsf_task_lock();
    attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
    if (attribute == NULL) {
        error = OPEN_CFW_ATTS_MAIN_ERR_NOT_FOUND;
    } else if (value_length > attribute->maximum_length) {
        error = OPEN_CFW_ATTS_MAIN_ERR_LENGTH;
    } else {
        open_cfw_cordio_atts_main_copy(attribute->value, value, value_length);
        if ((attribute->settings & OPEN_CFW_ATTS_MAIN_SET_VARIABLE_LENGTH) != 0U) {
            *attribute->length = value_length;
        }
    }
    open_cfw_cordio_wsf_task_unlock();
    return error;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_GET_ATTRIBUTE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_get_attribute(
    uint16_t handle, uint16_t *length, uint8_t **value
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
    if (attribute == NULL) {
        return OPEN_CFW_ATTS_MAIN_ERR_NOT_FOUND;
    }
    *length = *attribute->length;
    *value = attribute->value;
    return 0U;
}
#endif

#if defined(OPEN_CFW_ATTS_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTS_MAIN_ERROR_TEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_error_test(uint8_t status)
{
    OPEN_CFW_ATTS_MAIN_ERROR_TEST = status;
}
#endif
