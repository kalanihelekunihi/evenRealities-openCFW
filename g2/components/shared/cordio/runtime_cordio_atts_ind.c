/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_atts_ind.h"

#if !defined(OPEN_CFW_ATTS_IND_PENDING_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_SET_PENDING_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_EXEC_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_NOTIFICATION_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_SETUP_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_CONNECTION_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_MESSAGE_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_CONTROL_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_HANDLE_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_INDICATION_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_NOTIFICATION_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_INDICATION_ZERO_COPY_ONLY) && \
    !defined(OPEN_CFW_ATTS_IND_NOTIFICATION_ZERO_COPY_ONLY)
#define OPEN_CFW_ATTS_IND_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_IND_PRODUCTION
#define OPEN_CFW_ATTS_IND_CONNECTIONS_BASE \
    ((struct open_cfw_cordio_atts_ind_connection *)0x2006E5F0U)
#define OPEN_CFW_ATTS_IND_HANDLER_ID (*(uint8_t *)0x2006110CU)
#define OPEN_CFW_ATTS_IND_SERVICE_CHANGED_UUID ((uint8_t *)0x0078F546U)
#define OPEN_CFW_ATTS_IND_INTERFACE_SLOT (*(void **)0x2006E850U)
#define OPEN_CFW_ATTS_IND_CONFIGURATION \
    (*(struct open_cfw_cordio_att_configuration **)0x200004B4U)
#else
#define OPEN_CFW_ATTS_IND_CONNECTIONS_BASE \
    (&open_cfw_cordio_atts_ind_connections[0][0])
#define OPEN_CFW_ATTS_IND_HANDLER_ID open_cfw_cordio_att_handler_id
#define OPEN_CFW_ATTS_IND_SERVICE_CHANGED_UUID \
    open_cfw_cordio_atts_service_changed_uuid
#define OPEN_CFW_ATTS_IND_INTERFACE_SLOT open_cfw_cordio_atts_indication_interface
#define OPEN_CFW_ATTS_IND_CONFIGURATION open_cfw_cordio_att_configuration
#endif

static __attribute__((unused)) void open_cfw_cordio_atts_ind_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length--;
    }
}

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_PENDING_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_ind_pending(
    struct open_cfw_cordio_atts_ind_connection *connection,
    struct open_cfw_cordio_atts_ind_packet *packet
)
{
    uint8_t pending = 0U;
    uint8_t index;
    if (packet->pdu[0] == OPEN_CFW_ATTS_IND_VALUE_INDICATION) {
        return connection->pending_indication_handle != 0U;
    }
    for (index = 0U; index < 10U; index++) {
        if (connection->pending_notification_handle[index] != 0U) {
            if (connection->pending_notification_handle[index]
                == packet->handle) {
                return 1U;
            }
            pending++;
        }
    }
    return pending >= 10U;
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_SET_PENDING_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_set_pending_notification(
    struct open_cfw_cordio_atts_ind_connection *connection, uint16_t handle
)
{
    uint8_t index;
    for (index = 0U; index < 10U; index++) {
        if (connection->pending_notification_handle[index] == 0U) {
            connection->pending_notification_handle[index] = handle;
            break;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_EXEC_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_execute_callback(
    uint8_t connection_id, uint16_t handle, uint8_t status
)
{
    open_cfw_cordio_att_execute_callback(
        connection_id, OPEN_CFW_ATTS_IND_VALUE_CONFIRM_EVENT,
        handle, status, 0U
    );
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_NOTIFICATION_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_notification_callback(
    uint8_t connection_id,
    struct open_cfw_cordio_atts_ind_connection *connection,
    uint8_t status
)
{
    uint8_t index;
    if (connection->pending_indication_handle != 0U) {
        open_cfw_cordio_atts_ind_execute_callback(
            connection_id, connection->pending_indication_handle, status
        );
        connection->pending_indication_handle = 0U;
    }
    for (index = 0U; index < 10U; index++) {
        if (connection->pending_notification_handle[index] != 0U) {
            open_cfw_cordio_atts_ind_execute_callback(
                connection_id,
                connection->pending_notification_handle[index], status
            );
            connection->pending_notification_handle[index] = 0U;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_SETUP_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_setup_message(
    struct open_cfw_cordio_atts_ind_connection *connection,
    uint8_t connection_id, uint8_t slot,
    struct open_cfw_cordio_atts_ind_packet *packet
)
{
    uint8_t opcode = packet->pdu[0];
    uint16_t handle = packet->handle;
    open_cfw_cordio_att_l2c_data_request(
        connection->main, slot, packet->length, (uint8_t *)packet
    );
    if (opcode == OPEN_CFW_ATTS_IND_VALUE_INDICATION) {
        connection->pending_indication_handle = handle;
        connection->outstanding_indication_handle = handle;
        connection->indication_timer.message.event =
            OPEN_CFW_ATTS_IND_TIMEOUT_EVENT;
        connection->indication_timer.message.parameter =
            open_cfw_cordio_att_message_parameter(
                connection->connection_id, connection->slot
            );
        open_cfw_cordio_wsf_timer_start_seconds(
            &connection->indication_timer,
            OPEN_CFW_ATTS_IND_CONFIGURATION->transaction_timeout
        );
    } else if ((connection->main->bearer[slot].control
            & OPEN_CFW_ATTS_IND_FLOW_DISABLED) != 0U) {
        open_cfw_cordio_atts_ind_set_pending_notification(connection, handle);
    } else if (opcode == OPEN_CFW_ATTS_IND_MULTIPLE_VALUE_NOTIFICATION) {
        open_cfw_cordio_att_execute_callback(
            connection_id, OPEN_CFW_ATTS_IND_MULTIPLE_CONFIRM_EVENT,
            handle, 0U, 0U
        );
    } else {
        open_cfw_cordio_atts_ind_execute_callback(
            connection_id, handle, 0U
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_CONNECTION_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_connection_callback(
    struct open_cfw_cordio_att_main_control_block *main,
    struct open_cfw_cordio_dm_event *event
)
{
    uint8_t index;
    uint8_t status;
    struct open_cfw_cordio_atts_ind_connection *connection;
    if (event->header.event != OPEN_CFW_ATTS_IND_CONNECTION_CLOSE_EVENT) {
        return;
    }
    status = (uint8_t)((event->header.status == 0U
        ? event->reason : event->header.status)
        + OPEN_CFW_ATTS_IND_G2_HCI_ERROR_BASE);
    if (main->connection_id == 0U) {
        return;
    }
    connection = OPEN_CFW_ATTS_IND_CONNECTIONS_BASE
        + ((uint32_t)(main->connection_id - 1U) * 3U);
    for (index = 0U; index < 3U; index++, connection++) {
        if (connection->outstanding_indication_handle != 0U) {
            open_cfw_cordio_wsf_timer_stop(&connection->indication_timer);
            connection->outstanding_indication_handle = 0U;
        }
        open_cfw_cordio_atts_ind_notification_callback(
            main->connection_id, connection, status
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_MESSAGE_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_message_callback(
    struct open_cfw_cordio_atts_ind_api_message *message
)
{
    struct open_cfw_cordio_atts_ind_connection *connection;
    uint8_t connection_id;
    uint8_t slot;
    if (message->header.event == OPEN_CFW_ATTS_IND_API_EVENT) {
        connection = open_cfw_cordio_atts_ind_connection_by_id(
            (uint8_t)message->header.parameter, message->slot
        );
        if (connection == NULL) {
            open_cfw_cordio_wsf_message_free(message->packet);
        } else if (open_cfw_cordio_atts_ind_pending(
                connection, message->packet)) {
            open_cfw_cordio_atts_ind_execute_callback(
                (uint8_t)message->header.parameter,
                message->packet->handle, OPEN_CFW_ATTS_IND_ERR_OVERFLOW
            );
            open_cfw_cordio_wsf_message_free(message->packet);
        } else {
            open_cfw_cordio_atts_ind_setup_message(
                connection, (uint8_t)message->header.parameter,
                message->slot, message->packet
            );
        }
    } else if (message->header.event == OPEN_CFW_ATTS_IND_TIMEOUT_EVENT) {
        open_cfw_cordio_att_decode_message_parameter(
            message->header.parameter, &connection_id, &slot
        );
        message->header.parameter = connection_id;
        /* Authenticated G2 performs the lookup but has no retained timeout
         * state transition after either lookup outcome. */
        (void)open_cfw_cordio_atts_ind_connection_by_id(connection_id, slot);
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_CONTROL_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_control_callback(
    struct open_cfw_cordio_wsf_message_header *message
)
{
    struct open_cfw_cordio_atts_ind_connection *connection =
        open_cfw_cordio_atts_ind_connection_by_id(
            (uint8_t)message->parameter, 0U
        );
    if (connection != NULL) {
        open_cfw_cordio_atts_ind_notification_callback(
            (uint8_t)message->parameter, connection, 0U
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_HANDLE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_handle_value_indication_notification(
    uint8_t connection_id, uint16_t handle, uint8_t slot,
    uint16_t value_length, uint8_t *value, uint8_t opcode, uint8_t zero_copy
)
{
    struct open_cfw_cordio_atts_ind_connection *connection;
    struct open_cfw_cordio_atts_ind_api_message *message;
    uint16_t mtu;
    uint8_t timed_out;
    uint8_t sent = 0U;
    open_cfw_cordio_wsf_task_lock();
    connection = open_cfw_cordio_atts_ind_connection_by_id(
        connection_id, slot
    );
    if (connection == NULL) {
        mtu = 0U;
        timed_out = 0U;
    } else {
        mtu = connection->main->bearer[slot].mtu;
        timed_out = (uint8_t)((connection->main->bearer[slot].control
            & OPEN_CFW_ATTS_IND_TRANSACTION_TIMEOUT) != 0U);
    }
    open_cfw_cordio_wsf_task_unlock();
    if (mtu > 0U) {
        if (!timed_out) {
            if (open_cfw_cordio_atts_csf_is_client_change_aware(
                    connection_id, handle)) {
                if ((uint32_t)value_length + 3U <= mtu) {
                    message = open_cfw_cordio_wsf_message_allocate(
                        (uint16_t)sizeof(*message)
                    );
                    if (message != NULL) {
                        message->header.parameter = connection_id;
                        message->header.event = OPEN_CFW_ATTS_IND_API_EVENT;
                        message->slot = slot;
                        message->packet = zero_copy
                            ? (struct open_cfw_cordio_atts_ind_packet *)(value - 11U)
                            : open_cfw_cordio_att_message_allocate(
                                (uint16_t)(11U + value_length)
                            );
                        if (message->packet != NULL) {
                            message->packet->length =
                                (uint16_t)(3U + value_length);
                            message->packet->handle = handle;
                            message->packet->pdu[0] = opcode;
                            message->packet->pdu[1] = (uint8_t)handle;
                            message->packet->pdu[2] = (uint8_t)(handle >> 8);
                            if (!zero_copy) {
                                open_cfw_cordio_atts_ind_copy(
                                    &message->packet->pdu[3], value,
                                    value_length
                                );
                            }
                            open_cfw_cordio_wsf_message_send(
                                OPEN_CFW_ATTS_IND_HANDLER_ID, message
                            );
                            sent = 1U;
                        } else {
                            open_cfw_cordio_wsf_message_free(message);
                        }
                    }
                } else {
                    open_cfw_cordio_atts_ind_execute_callback(
                        connection_id, handle,
                        OPEN_CFW_ATTS_IND_ERR_MTU_EXCEEDED
                    );
                }
            }
        } else {
            open_cfw_cordio_atts_ind_execute_callback(
                connection_id, handle, OPEN_CFW_ATTS_IND_ERR_TIMEOUT
            );
        }
    }
    if ((!sent) && zero_copy) {
        open_cfw_cordio_att_message_free(value, opcode);
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_CONFIRM_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_value_confirmation(
    struct open_cfw_cordio_atts_ind_connection *connection,
    uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    (void)length;
    (void)packet;
    if (connection->outstanding_indication_handle != 0U) {
        open_cfw_cordio_wsf_timer_stop(&connection->indication_timer);
        attribute = open_cfw_cordio_atts_find_by_handle(
            connection->outstanding_indication_handle, &group
        );
        if ((attribute != NULL)
            && (attribute->uuid[0] == OPEN_CFW_ATTS_IND_SERVICE_CHANGED_UUID[0])
            && (attribute->uuid[1] == OPEN_CFW_ATTS_IND_SERVICE_CHANGED_UUID[1])
            && (open_cfw_cordio_atts_csf_get_change_aware_state(
                connection->connection_id) != 0U)) {
            open_cfw_cordio_atts_csf_set_clients_change_awareness_state(
                connection->connection_id, 0U
            );
        }
        connection->outstanding_indication_handle = 0U;
        if ((connection->main->bearer[connection->slot].control
                & OPEN_CFW_ATTS_IND_FLOW_DISABLED) == 0U) {
            open_cfw_cordio_atts_ind_execute_callback(
                connection->connection_id,
                connection->pending_indication_handle, 0U
            );
            connection->pending_indication_handle = 0U;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_INITIALIZE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ind_initialize(void)
{
    uint8_t connection_index;
    uint8_t slot;
    struct open_cfw_cordio_atts_ind_connection *connection;
    for (connection_index = 0U; connection_index < 3U; connection_index++) {
        for (slot = 0U; slot < 3U; slot++) {
            connection = OPEN_CFW_ATTS_IND_CONNECTIONS_BASE
                + (uint32_t)connection_index * 3U + slot;
            connection->indication_timer.handler_id =
                OPEN_CFW_ATTS_IND_HANDLER_ID;
            connection->indication_timer.message.parameter =
                (uint16_t)(connection_index + 1U);
        }
    }
#ifdef OPEN_CFW_ATTS_IND_PRODUCTION
    OPEN_CFW_ATTS_IND_INTERFACE_SLOT = (void *)(uintptr_t)0x007852C0U;
#endif
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_INDICATION_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_handle_value_indication(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
)
{
    open_cfw_cordio_atts_handle_value_indication_notification(
        connection_id, handle, 0U, length, value,
        OPEN_CFW_ATTS_IND_VALUE_INDICATION, 0U
    );
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_NOTIFICATION_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_handle_value_notification(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
)
{
    open_cfw_cordio_atts_handle_value_indication_notification(
        connection_id, handle, 0U, length, value,
        OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION, 0U
    );
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_INDICATION_ZERO_COPY_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_handle_value_indication_zero_copy(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
)
{
    open_cfw_cordio_atts_handle_value_indication_notification(
        connection_id, handle, 0U, length, value,
        OPEN_CFW_ATTS_IND_VALUE_INDICATION, 1U
    );
}
#endif

#if defined(OPEN_CFW_ATTS_IND_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_IND_NOTIFICATION_ZERO_COPY_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_handle_value_notification_zero_copy(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
)
{
    open_cfw_cordio_atts_handle_value_indication_notification(
        connection_id, handle, 0U, length, value,
        OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION, 1U
    );
}
#endif
