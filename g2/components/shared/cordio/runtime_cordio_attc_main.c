/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_attc_main.h"

#if !defined(OPEN_CFW_ATTC_MAIN_PEND_WRITE_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_SET_PEND_WRITE_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_WRITE_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_SIMPLE_REQ_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_CONTINUING_REQ_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_MTU_REQ_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_WRITE_CMD_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_PREP_WRITE_REQ_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_SEND_REQ_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_SETUP_REQ_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_DATA_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_CONTROL_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_CONNECTION_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_MESSAGE_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_CCB_BY_ID_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_CCB_BY_HANDLE_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_FREE_PACKET_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_EXEC_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_REQUEST_CLEAR_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_ATTC_MAIN_AUTO_CONFIRM_ONLY)
#define OPEN_CFW_ATTC_MAIN_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTC_MAIN_PRODUCTION
#define OPEN_CFW_ATTC_MAIN_CONNECTION_BASE \
    ((struct open_cfw_cordio_attc_connection_control_block *)0x2006F904U)
#define OPEN_CFW_ATTC_MAIN_ON_DECK \
    ((struct open_cfw_cordio_attc_api_message *)0x2006FA90U)
#define OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE \
    (*(const struct open_cfw_cordio_attc_sign_interface **)0x2006FAB4U)
#define OPEN_CFW_ATTC_MAIN_AUTO_CONFIRM (*(uint8_t *)0x2006FAB8U)
#define OPEN_CFW_ATTC_MAIN_CONTROL_BLOCKS \
    ((struct open_cfw_cordio_attc_main_control_block *)0x200610ACU)
#define OPEN_CFW_ATTC_MAIN_CLIENT_INTERFACE \
    (*(struct open_cfw_cordio_attc_interface **)0x200610E8U)
#define OPEN_CFW_ATTC_MAIN_STOCK_INTERFACE \
    ((struct open_cfw_cordio_attc_interface *)0x00785250U)
#define OPEN_CFW_ATTC_MAIN_HANDLER_ID (*(uint8_t *)0x2006110CU)
#define OPEN_CFW_ATTC_MAIN_CONFIGURATION \
    (*(struct open_cfw_cordio_attc_configuration **)0x200004B4U)
#else
#define OPEN_CFW_ATTC_MAIN_CONNECTION_BASE \
    (&open_cfw_cordio_attc_main_connections[0][0])
#define OPEN_CFW_ATTC_MAIN_ON_DECK open_cfw_cordio_attc_on_deck
#define OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE open_cfw_cordio_attc_sign_interface
#define OPEN_CFW_ATTC_MAIN_AUTO_CONFIRM open_cfw_cordio_attc_auto_confirm
#define OPEN_CFW_ATTC_MAIN_CONTROL_BLOCKS open_cfw_cordio_attc_main_control_blocks
#define OPEN_CFW_ATTC_MAIN_CLIENT_INTERFACE open_cfw_cordio_attc_client_interface
#define OPEN_CFW_ATTC_MAIN_STOCK_INTERFACE open_cfw_cordio_attc_stock_interface
#define OPEN_CFW_ATTC_MAIN_HANDLER_ID open_cfw_cordio_attc_handler_id
#define OPEN_CFW_ATTC_MAIN_CONFIGURATION open_cfw_cordio_attc_configuration
#endif

static __attribute__((unused)) void *
open_cfw_cordio_attc_main_timer(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    return connection->outstanding_timer;
}

static __attribute__((unused)) void open_cfw_cordio_attc_main_timer_event(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint8_t event
)
{
    connection->outstanding_timer[10] = event;
}

static __attribute__((unused)) void open_cfw_cordio_attc_main_copy(
    void *destination, const void *source, uint16_t length
)
{
    uint8_t *output = destination;
    const uint8_t *input = source;
    while (length != 0U) {
        *output++ = *input++;
        length--;
    }
}

static __attribute__((unused)) void open_cfw_cordio_attc_main_put_u16(
    uint8_t *output, uint16_t value
)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8);
}

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_PEND_WRITE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_pending_write_command(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t handle
)
{
    return (uint8_t)(connection->pending_write_handles[0] != 0U
        && (connection->pending_write_handles[0] == handle
            || connection->pending_write_handles[0] != 0U));
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_SET_PEND_WRITE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_set_pending_write_command(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    if (connection->pending_write_handles[0] == 0U) {
        connection->pending_write_handles[0] =
            connection->outstanding_request.handle;
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_WRITE_CALLBACK_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_write_command_callback(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint8_t status
)
{
    uint16_t handle = connection->pending_write_handles[0];
    if (handle != 0U) {
        open_cfw_cordio_attc_execute_callback(
            connection_id, OPEN_CFW_ATTC_MAIN_WRITE_COMMAND_RESPONSE,
            handle, status
        );
        connection->pending_write_handles[0] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_SIMPLE_REQ_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_send_simple_request(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        connection->outstanding_request.packet;
    if (packet == NULL) {
        open_cfw_cordio_attc_request_clear(
            connection->connection_id, &connection->outstanding_request,
            OPEN_CFW_ATTC_MAIN_ERROR_MEMORY
        );
        return;
    }
    connection->outstanding_request.packet = NULL;
    if (connection->outstanding_request.header.event !=
            OPEN_CFW_ATTC_MAIN_WRITE_COMMAND_RESPONSE) {
        void *timer = open_cfw_cordio_attc_main_timer(connection);
        open_cfw_cordio_attc_main_timer_event(
            connection, OPEN_CFW_ATTC_MAIN_MESSAGE_TIMEOUT
        );
        open_cfw_cordio_wsf_timer_start_sec_candidate(
            timer, OPEN_CFW_ATTC_MAIN_CONFIGURATION->transaction_timeout
        );
    }
    open_cfw_cordio_att_l2c_data_request(
        connection->main, connection->outstanding_request.slot,
        packet->length, (uint8_t *)packet
    );
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_CONTINUING_REQ_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_send_continuing_request(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    union open_cfw_cordio_attc_packet_parameter *stored =
        connection->outstanding_request.packet;
    union open_cfw_cordio_attc_packet_parameter *packet;
    uint8_t *output;
    if (stored == NULL) {
        open_cfw_cordio_attc_request_clear(
            connection->connection_id, &connection->outstanding_request,
            OPEN_CFW_ATTC_MAIN_ERROR_MEMORY
        );
        return;
    }
    if (connection->outstanding_request.header.status != 0U) {
        packet = open_cfw_cordio_att_message_allocate(
            (uint16_t)(stored->length + OPEN_CFW_ATTC_MAIN_L2C_PAYLOAD_START)
        );
        if (packet == NULL) {
            open_cfw_cordio_attc_request_clear(
                connection->connection_id, &connection->outstanding_request,
                OPEN_CFW_ATTC_MAIN_ERROR_MEMORY
            );
            return;
        }
        open_cfw_cordio_attc_main_copy(
            packet, stored,
            (uint16_t)(stored->length + OPEN_CFW_ATTC_MAIN_L2C_PAYLOAD_START)
        );
    } else {
        packet = stored;
        connection->outstanding_request.packet = NULL;
    }
    output = (uint8_t *)packet + 9U;
    if (connection->outstanding_request.header.event == 6U) {
        output += 2U;
        open_cfw_cordio_attc_main_put_u16(
            output, connection->outstanding_parameters.offset.offset
        );
    } else {
        open_cfw_cordio_attc_main_put_u16(
            output, connection->outstanding_parameters.handles.start_handle
        );
        open_cfw_cordio_attc_main_put_u16(
            output + 2U,
            connection->outstanding_parameters.handles.end_handle
        );
    }
    open_cfw_cordio_attc_main_timer_event(
        connection, OPEN_CFW_ATTC_MAIN_MESSAGE_TIMEOUT
    );
    open_cfw_cordio_wsf_timer_start_sec_candidate(
        open_cfw_cordio_attc_main_timer(connection),
        OPEN_CFW_ATTC_MAIN_CONFIGURATION->transaction_timeout
    );
    open_cfw_cordio_att_l2c_data_request(
        connection->main, connection->outstanding_request.slot,
        packet->length, (uint8_t *)packet
    );
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_MTU_REQ_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_send_mtu_request(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    struct open_cfw_cordio_attc_main_control_block *main = connection->main;
    uint8_t slot = connection->outstanding_request.slot;
    if ((main->bearer[slot].control & OPEN_CFW_ATTC_MAIN_MTU_SENT) != 0U) {
        open_cfw_cordio_attc_free_packet(&connection->outstanding_request);
        connection->outstanding_request.header.event = 0U;
    } else {
        main->bearer[slot].control |= OPEN_CFW_ATTC_MAIN_MTU_SENT;
        open_cfw_cordio_attc_send_simple_request(connection);
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_WRITE_CMD_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_send_write_command(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    struct open_cfw_cordio_attc_main_control_block *main = connection->main;
    uint16_t handle = connection->outstanding_request.handle;
    uint8_t slot = connection->outstanding_request.slot;
    open_cfw_cordio_attc_send_simple_request(connection);
    if ((main->bearer[slot].control & OPEN_CFW_ATTC_MAIN_FLOW_DISABLED) == 0U) {
        open_cfw_cordio_attc_execute_callback(
            main->connection_id, OPEN_CFW_ATTC_MAIN_WRITE_COMMAND_RESPONSE,
            handle, OPEN_CFW_ATTC_MAIN_SUCCESS
        );
    } else {
        open_cfw_cordio_attc_set_pending_write_command(connection);
    }
    connection->outstanding_request.header.event = 0U;
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_PREP_WRITE_REQ_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_send_prepare_write_request(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    struct open_cfw_cordio_attc_main_control_block *main = connection->main;
    union open_cfw_cordio_attc_packet_parameter *stored =
        connection->outstanding_request.packet;
    union open_cfw_cordio_attc_packet_parameter *packet;
    uint16_t data_length, mtu = main->bearer[connection->slot].mtu;
    if (stored == NULL || mtu < OPEN_CFW_ATTC_MAIN_PREPARE_REQUEST_LENGTH) {
        open_cfw_cordio_attc_request_clear(
            connection->connection_id, &connection->outstanding_request,
            OPEN_CFW_ATTC_MAIN_ERROR_MTU_EXCEEDED
        );
        return;
    }
    if (connection->outstanding_request.header.status != 0U) {
        uint16_t capacity =
            (uint16_t)(mtu - OPEN_CFW_ATTC_MAIN_PREPARE_REQUEST_LENGTH);
        data_length = connection->outstanding_parameters.prepare.length;
        if (data_length > capacity) {
            data_length = capacity;
        }
        packet = open_cfw_cordio_att_message_allocate(
            (uint16_t)(data_length + OPEN_CFW_ATTC_MAIN_PREPARE_REQUEST_LENGTH
                + OPEN_CFW_ATTC_MAIN_L2C_PAYLOAD_START)
        );
        if (packet == NULL) {
            open_cfw_cordio_attc_request_clear(
                connection->connection_id, &connection->outstanding_request,
                OPEN_CFW_ATTC_MAIN_ERROR_MEMORY
            );
            return;
        }
        open_cfw_cordio_attc_main_copy(
            packet, stored,
            OPEN_CFW_ATTC_MAIN_PREPARE_REQUEST_LENGTH
                + OPEN_CFW_ATTC_MAIN_L2C_PAYLOAD_START
        );
        open_cfw_cordio_attc_main_copy(
            (uint8_t *)packet + 13U,
            connection->outstanding_parameters.prepare.value, data_length
        );
        connection->outstanding_parameters.prepare.value += data_length;
        connection->outstanding_parameters.prepare.length = (uint16_t)(
            connection->outstanding_parameters.prepare.length - data_length
        );
    } else {
        data_length = connection->outstanding_parameters.prepare.length;
        packet = stored;
        connection->outstanding_request.packet = NULL;
    }
    open_cfw_cordio_attc_main_put_u16(
        (uint8_t *)packet + 11U,
        connection->outstanding_parameters.prepare.offset
    );
    connection->outstanding_parameters.prepare.offset = (uint16_t)(
        connection->outstanding_parameters.prepare.offset + data_length
    );
    open_cfw_cordio_attc_main_timer_event(
        connection, OPEN_CFW_ATTC_MAIN_MESSAGE_TIMEOUT
    );
    open_cfw_cordio_wsf_timer_start_sec_candidate(
        open_cfw_cordio_attc_main_timer(connection),
        OPEN_CFW_ATTC_MAIN_CONFIGURATION->transaction_timeout
    );
    open_cfw_cordio_att_l2c_data_request(
        main, connection->outstanding_request.slot,
        (uint16_t)(data_length + OPEN_CFW_ATTC_MAIN_PREPARE_REQUEST_LENGTH),
        (uint8_t *)packet
    );
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_SEND_REQ_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_send_request(
    struct open_cfw_cordio_attc_connection_control_block *connection
)
{
    switch (connection->outstanding_request.header.event) {
    case 1U: open_cfw_cordio_attc_send_mtu_request(connection); break;
    case 2U: case 3U: case 4U: case 6U: case 8U:
        open_cfw_cordio_attc_send_continuing_request(connection); break;
    case 5U: case 7U: case 9U: case 12U: case 16U:
        open_cfw_cordio_attc_send_simple_request(connection); break;
    case 10U: open_cfw_cordio_attc_send_write_command(connection); break;
    case 11U: open_cfw_cordio_attc_send_prepare_write_request(connection); break;
    default:
        open_cfw_cordio_attc_request_clear(
            connection->connection_id, &connection->outstanding_request,
            OPEN_CFW_ATTC_MAIN_ERROR_OVERFLOW
        );
        break;
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_SETUP_REQ_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_setup_request(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    struct open_cfw_cordio_attc_api_message *message
)
{
    connection->outstanding_request = *message;
    if (message->packet == NULL) {
        open_cfw_cordio_attc_request_clear(
            connection->connection_id, &connection->outstanding_request,
            OPEN_CFW_ATTC_MAIN_ERROR_MEMORY
        );
        return;
    }
    if (message->header.event == 11U) {
        if (message->packet->prepare == NULL) {
            open_cfw_cordio_attc_request_clear(
                connection->connection_id, &connection->outstanding_request,
                OPEN_CFW_ATTC_MAIN_ERROR_MEMORY
            );
            return;
        }
        connection->outstanding_parameters.prepare = *message->packet->prepare;
    } else {
        open_cfw_cordio_attc_main_copy(
            &connection->outstanding_parameters, message->packet,
            sizeof(connection->outstanding_parameters)
        );
    }
    open_cfw_cordio_attc_send_request(connection);
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_DATA_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_data_callback(
    uint16_t handle, uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_attc_connection_control_block *connection =
        open_cfw_cordio_attc_connection_by_handle(handle, 0U);
    uint8_t opcode;
    if (connection == NULL || packet == NULL || length < 1U) {
        return;
    }
    opcode = packet[8];
    if (opcode <= OPEN_CFW_ATTC_MAIN_PDU_EXECUTE_WRITE_RESPONSE) {
        open_cfw_cordio_attc_process_response(connection, length, packet);
    } else if (opcode == OPEN_CFW_ATTC_MAIN_PDU_VALUE_NOTIFICATION
        || opcode == OPEN_CFW_ATTC_MAIN_PDU_VALUE_INDICATION) {
        open_cfw_cordio_attc_process_indication_notification(
            connection, length, packet
        );
    } else if (opcode ==
        OPEN_CFW_ATTC_MAIN_PDU_MULTIPLE_VALUE_NOTIFICATION) {
        open_cfw_cordio_attc_process_multiple_variable_notification(
            connection, length, packet
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_CONTROL_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_control_callback(
    struct open_cfw_cordio_wsf_message_header *message
)
{
    struct open_cfw_cordio_attc_connection_control_block *connection;
    if (message == NULL || message->parameter > 0xFFU) {
        return;
    }
    connection = open_cfw_cordio_attc_connection_by_id(
        (uint8_t)message->parameter, 0U
    );
    if (connection != NULL) {
        open_cfw_cordio_attc_indication_confirm((uint8_t)message->parameter);
        open_cfw_cordio_attc_write_command_callback(
            (uint8_t)message->parameter, connection,
            OPEN_CFW_ATTC_MAIN_SUCCESS
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_CONNECTION_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_connection_callback(
    struct open_cfw_cordio_attc_main_control_block *main,
    struct open_cfw_cordio_attc_dm_event *event
)
{
    uint8_t slot, status;
    if (main == NULL || event == NULL || main->connection_id < 1U
        || main->connection_id > OPEN_CFW_ATTC_MAIN_CONNECTIONS) {
        return;
    }
    if (event->header.event == OPEN_CFW_ATTC_MAIN_CONNECTION_OPEN_EVENT) {
        if (open_cfw_cordio_dm_connection_role(main->connection_id) ==
            OPEN_CFW_ATTC_MAIN_MASTER_ROLE) {
            uint16_t max_rx = open_cfw_cordio_hci_get_max_rx_acl_length();
            uint16_t local_mtu = max_rx > 4U ? (uint16_t)(max_rx - 4U) : 0U;
            if (local_mtu > OPEN_CFW_ATTC_MAIN_CONFIGURATION->mtu) {
                local_mtu = OPEN_CFW_ATTC_MAIN_CONFIGURATION->mtu;
            }
            if (local_mtu != OPEN_CFW_ATTC_MAIN_DEFAULT_MTU) {
                open_cfw_cordio_attc_mtu_request(main->connection_id, local_mtu);
            }
        }
        return;
    }
    if (event->header.event != OPEN_CFW_ATTC_MAIN_CONNECTION_CLOSE_EVENT) {
        return;
    }
    status = (uint8_t)((event->header.status == 0U ? event->reason
        : event->header.status) + OPEN_CFW_ATTC_MAIN_G2_HCI_ERROR_BASE);
    if (OPEN_CFW_ATTC_MAIN_ON_DECK[main->connection_id-1U].header.event != 0U) {
        open_cfw_cordio_attc_request_clear(
            main->connection_id,
            &OPEN_CFW_ATTC_MAIN_ON_DECK[main->connection_id-1U], status
        );
    }
    for (slot = 0U; slot < OPEN_CFW_ATTC_MAIN_BEARERS; slot++) {
        struct open_cfw_cordio_attc_connection_control_block *connection =
            OPEN_CFW_ATTC_MAIN_CONNECTION_BASE
            + (uint32_t)(main->connection_id-1U)*3U + slot;
        if (connection->outstanding_request.header.event != 0U) {
            open_cfw_cordio_wsf_timer_stop_candidate(
                open_cfw_cordio_attc_main_timer(connection)
            );
            open_cfw_cordio_attc_request_clear(
                connection->connection_id,
                &connection->outstanding_request, status
            );
        }
        main->bearer[slot].control &= (uint8_t)~(
            OPEN_CFW_ATTC_MAIN_FLOW_DISABLED
            | OPEN_CFW_ATTC_MAIN_CONFIRM_PENDING
        );
        if (OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE != NULL
            && OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE->close_callback != NULL) {
            OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE->close_callback(connection, status);
        }
        open_cfw_cordio_attc_write_command_callback(
            main->connection_id, connection, status
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_MESSAGE_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_message_callback(
    struct open_cfw_cordio_attc_api_message *message
)
{
    struct open_cfw_cordio_attc_connection_control_block *connection;
    uint8_t connection_id;
    if (message == NULL) {
        return;
    }
    if (message->header.event >= OPEN_CFW_ATTC_MAIN_MESSAGE_SIGNED_WRITE
        && message->header.event <= OPEN_CFW_ATTC_MAIN_MESSAGE_CMAC_COMPLETE) {
        if (OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE != NULL
            && OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE->message_callback != NULL) {
            OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE->message_callback(NULL, message);
        }
        return;
    }
    if (message->header.parameter > 0xFFU) {
        open_cfw_cordio_attc_free_packet(message);
        return;
    }
    connection_id = (uint8_t)message->header.parameter;
    connection = open_cfw_cordio_attc_connection_by_id(
        connection_id, message->slot
    );
    if (connection == NULL) {
        if (message->header.event >= 1U
            && message->header.event <=
                OPEN_CFW_ATTC_MAIN_MESSAGE_SIGNED_WRITE) {
            open_cfw_cordio_attc_free_packet(message);
        }
        return;
    }
    if (message->header.event <=
        OPEN_CFW_ATTC_MAIN_MESSAGE_READ_MULTIPLE_VARIABLE) {
        struct open_cfw_cordio_attc_api_message *on_deck =
            &OPEN_CFW_ATTC_MAIN_ON_DECK[connection_id-1U];
        if ((connection->slot == 0U && on_deck->header.event != 0U)
            || connection->outstanding_request.header.event > 1U
            || (message->header.event ==
                    OPEN_CFW_ATTC_MAIN_WRITE_COMMAND_RESPONSE
                && open_cfw_cordio_attc_pending_write_command(
                    connection, message->handle))) {
            open_cfw_cordio_attc_request_clear(
                connection_id, message, OPEN_CFW_ATTC_MAIN_ERROR_OVERFLOW
            );
        } else if (connection->slot == 0U
            && connection->outstanding_request.header.event == 1U) {
            *on_deck = *message;
        } else {
            open_cfw_cordio_attc_setup_request(connection, message);
        }
    } else if (message->header.event == OPEN_CFW_ATTC_MAIN_MESSAGE_CANCEL) {
        if (connection->outstanding_request.header.event != 0U
            && connection->outstanding_request.header.event != 1U) {
            open_cfw_cordio_wsf_timer_stop_candidate(
                open_cfw_cordio_attc_main_timer(connection)
            );
            open_cfw_cordio_attc_request_clear(
                connection_id, &connection->outstanding_request,
                OPEN_CFW_ATTC_MAIN_ERROR_CANCELLED
            );
        } else if (connection->slot == 0U
            && OPEN_CFW_ATTC_MAIN_ON_DECK[connection_id-1U].header.event != 0U) {
            open_cfw_cordio_attc_request_clear(
                connection_id,
                &OPEN_CFW_ATTC_MAIN_ON_DECK[connection_id-1U],
                OPEN_CFW_ATTC_MAIN_ERROR_CANCELLED
            );
        }
    } else if (message->header.event == OPEN_CFW_ATTC_MAIN_MESSAGE_TIMEOUT
        && connection->outstanding_request.header.event != 0U) {
        open_cfw_cordio_attc_request_clear(
            connection_id, &connection->outstanding_request,
            OPEN_CFW_ATTC_MAIN_ERROR_TIMEOUT
        );
        ((struct open_cfw_cordio_attc_main_control_block *)connection->main)
            ->bearer[message->slot].control |=
                OPEN_CFW_ATTC_MAIN_TRANSACTION_TIMEOUT;
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_CCB_BY_ID_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_attc_connection_control_block *
open_cfw_cordio_attc_connection_by_id(uint8_t connection_id, uint8_t slot)
{
    if (connection_id >= 1U
        && connection_id <= OPEN_CFW_ATTC_MAIN_CONNECTIONS
        && slot < OPEN_CFW_ATTC_MAIN_BEARERS
        && open_cfw_cordio_dm_connection_in_use(connection_id)) {
        return OPEN_CFW_ATTC_MAIN_CONNECTION_BASE
            + (uint32_t)(connection_id-1U)*3U + slot;
    }
    return NULL;
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_CCB_BY_HANDLE_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_attc_connection_control_block *
open_cfw_cordio_attc_connection_by_handle(uint16_t handle, uint8_t slot)
{
    uint8_t connection_id;
    if (slot >= OPEN_CFW_ATTC_MAIN_BEARERS) {
        return NULL;
    }
    connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    if (connection_id < 1U || connection_id > OPEN_CFW_ATTC_MAIN_CONNECTIONS) {
        return NULL;
    }
    return OPEN_CFW_ATTC_MAIN_CONNECTION_BASE
        + (uint32_t)(connection_id-1U)*3U + slot;
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_FREE_PACKET_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_free_packet(
    struct open_cfw_cordio_attc_api_message *message
)
{
    if (message->packet != NULL) {
        open_cfw_cordio_wsf_message_free_candidate(message->packet);
        message->packet = NULL;
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_EXEC_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_execute_callback(
    uint8_t connection_id, uint8_t event, uint16_t handle, uint8_t status
)
{
    if (event != OPEN_CFW_ATTC_MAIN_MESSAGE_MTU) {
        open_cfw_cordio_att_execute_callback(
            connection_id, event, handle, status, 0U
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_REQUEST_CLEAR_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_request_clear(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_api_message *message,
    uint8_t status
)
{
    uint8_t event = message->header.event;
    uint16_t handle = message->handle;
    open_cfw_cordio_attc_free_packet(message);
    open_cfw_cordio_attc_execute_callback(
        connection_id, event, handle, status
    );
    message->header.event = 0U;
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_INITIALIZE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_initialize(void)
{
    uint8_t connection_index, slot;
    OPEN_CFW_ATTC_MAIN_SIGN_INTERFACE = NULL;
    OPEN_CFW_ATTC_MAIN_AUTO_CONFIRM = 1U;
    for (connection_index = 0U;
         connection_index < OPEN_CFW_ATTC_MAIN_CONNECTIONS;
         connection_index++) {
        OPEN_CFW_ATTC_MAIN_ON_DECK[connection_index].header.event = 0U;
        for (slot = 0U; slot < OPEN_CFW_ATTC_MAIN_BEARERS; slot++) {
            struct open_cfw_cordio_attc_connection_control_block *connection =
                OPEN_CFW_ATTC_MAIN_CONNECTION_BASE
                + (uint32_t)connection_index*3U + slot;
            connection->main =
                &OPEN_CFW_ATTC_MAIN_CONTROL_BLOCKS[connection_index];
            connection->outstanding_timer[12] = OPEN_CFW_ATTC_MAIN_HANDLER_ID;
            connection->outstanding_timer[8] = (uint8_t)(connection_index+1U);
            connection->outstanding_timer[9] = 0U;
            connection->slot = slot;
            connection->connection_id = (uint8_t)(connection_index+1U);
            connection->pending_write_handles[0] = 0U;
        }
    }
    OPEN_CFW_ATTC_MAIN_CLIENT_INTERFACE = OPEN_CFW_ATTC_MAIN_STOCK_INTERFACE;
}
#endif

#if defined(OPEN_CFW_ATTC_MAIN_BUILD_ALL) || defined(OPEN_CFW_ATTC_MAIN_AUTO_CONFIRM_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_set_auto_confirm(
    uint8_t enable
)
{
    OPEN_CFW_ATTC_MAIN_AUTO_CONFIRM = (uint8_t)(enable != 0U);
}
#endif
