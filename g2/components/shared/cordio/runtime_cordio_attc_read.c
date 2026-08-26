/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 Cordio ATT client optional-read implementation.
 * Behavior follows Packetcraft r20.05--r20.05c and its byte-identical
 * official AmbiqSuite R4.4.1 import, with a bounded truncated-pair guard.
 */

#include "runtime_cordio_attc_read.h"

#if !defined(OPEN_CFW_ATTC_READ_FIND_TYPE_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_READ_LONG_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_READ_FIND_TYPE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_READ_TYPE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_READ_LONG_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_READ_MULTIPLE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_READ_GROUP_TYPE_REQUEST_ONLY)
#define OPEN_CFW_ATTC_READ_BUILD_ALL 1
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_attc_read_u16(
    const uint8_t *source
)
{
    return (uint16_t)source[0] | ((uint16_t)source[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_attc_read_write_u16(
    uint8_t *destination,
    uint16_t value
)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8);
}

static __attribute__((unused)) void open_cfw_cordio_attc_read_copy(
    uint8_t *destination,
    const uint8_t *source,
    uint16_t length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length--;
    }
}

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_FIND_TYPE_RESPONSE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_process_find_by_type_response(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet,
    struct open_cfw_cordio_att_event *event
)
{
    uint8_t *cursor = packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START + 1U;
    uint8_t *end = packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START + length;
    uint16_t next_handle =
        connection->outstanding_parameters.handles.start_handle;

    while (cursor < end) {
        uint16_t start_handle;
        uint16_t end_handle;
        if ((size_t)(end - cursor) < 4U) {
            event->header.status = OPEN_CFW_ATTC_READ_INVALID_RESPONSE;
            break;
        }
        start_handle = open_cfw_cordio_attc_read_u16(cursor);
        cursor += 2;
        end_handle = open_cfw_cordio_attc_read_u16(cursor);
        cursor += 2;
        if (start_handle > end_handle || start_handle < next_handle
            || start_handle
                > connection->outstanding_parameters.handles.end_handle
            || next_handle == 0U) {
            event->header.status = OPEN_CFW_ATTC_READ_INVALID_RESPONSE;
            break;
        }
        next_handle = end_handle == OPEN_CFW_ATTC_READ_HANDLE_MAX
            ? 0U : (uint16_t)(end_handle + 1U);
    }

    if (event->header.status == OPEN_CFW_ATTC_READ_SUCCESS
        && connection->outstanding_request.header.status
            == OPEN_CFW_ATTC_CONTINUING) {
        if (next_handle == 0U || next_handle
            > connection->outstanding_parameters.handles.end_handle) {
            connection->outstanding_request.header.status =
                OPEN_CFW_ATTC_NOT_CONTINUING;
        } else {
            connection->outstanding_parameters.handles.start_handle =
                next_handle;
            connection->outstanding_request.handle = next_handle;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_LONG_RESPONSE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_process_read_long_response(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet,
    struct open_cfw_cordio_att_event *event
)
{
    struct open_cfw_cordio_attc_main_control_block *main =
        (struct open_cfw_cordio_attc_main_control_block *)connection->main;
    (void)packet;
    if (connection->outstanding_request.header.status
        == OPEN_CFW_ATTC_CONTINUING) {
        if (length < main->bearer[connection->slot].mtu) {
            connection->outstanding_request.header.status =
                OPEN_CFW_ATTC_NOT_CONTINUING;
        } else {
            connection->outstanding_parameters.offset.offset = (uint16_t)(
                connection->outstanding_parameters.offset.offset
                + event->value_length
            );
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_FIND_TYPE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_find_by_type_value_request(
    uint8_t connection_id,
    uint16_t start_handle,
    uint16_t end_handle,
    uint16_t uuid16,
    uint16_t value_length,
    uint8_t *value,
    uint8_t continuing
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        open_cfw_cordio_att_message_allocate((uint16_t)(
            OPEN_CFW_ATTC_READ_FIND_TYPE_BUFFER_LENGTH + value_length
        ));
    uint8_t *cursor;
    if (packet == NULL) {
        return;
    }
    packet->handles.length = (uint16_t)(
        OPEN_CFW_ATTC_READ_FIND_TYPE_LENGTH + value_length
    );
    packet->handles.start_handle = start_handle;
    packet->handles.end_handle = end_handle;
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_READ_FIND_TYPE_REQUEST;
    cursor += 4;
    open_cfw_cordio_attc_read_write_u16(cursor, uuid16);
    cursor += 2;
    open_cfw_cordio_attc_read_copy(cursor, value, value_length);
    open_cfw_cordio_attc_send_message(
        connection_id, start_handle, OPEN_CFW_ATTC_READ_MESSAGE_FIND_TYPE,
        packet, continuing
    );
}
#endif

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_TYPE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_read_by_type_request(
    uint8_t connection_id,
    uint16_t start_handle,
    uint16_t end_handle,
    uint8_t uuid_length,
    uint8_t *uuid,
    uint8_t continuing
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        open_cfw_cordio_att_message_allocate((uint16_t)(
            OPEN_CFW_ATTC_READ_TYPE_BUFFER_LENGTH + uuid_length
        ));
    uint8_t *cursor;
    if (packet == NULL) {
        return;
    }
    packet->handles.length = (uint16_t)(
        OPEN_CFW_ATTC_READ_TYPE_LENGTH + uuid_length
    );
    packet->handles.start_handle = start_handle;
    packet->handles.end_handle = end_handle;
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_READ_TYPE_REQUEST;
    cursor += 4;
    open_cfw_cordio_attc_read_copy(cursor, uuid, uuid_length);
    open_cfw_cordio_attc_send_message(
        connection_id, start_handle, OPEN_CFW_ATTC_READ_MESSAGE_TYPE,
        packet, continuing
    );
}
#endif

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_LONG_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_read_long_request(
    uint8_t connection_id,
    uint16_t handle,
    uint16_t offset,
    uint8_t continuing
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        open_cfw_cordio_att_message_allocate(
            OPEN_CFW_ATTC_READ_BLOB_BUFFER_LENGTH
        );
    uint8_t *cursor;
    if (packet == NULL) {
        return;
    }
    packet->offset.length = OPEN_CFW_ATTC_READ_BLOB_LENGTH;
    packet->offset.offset = offset;
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_READ_BLOB_REQUEST;
    open_cfw_cordio_attc_read_write_u16(cursor, handle);
    open_cfw_cordio_attc_send_message(
        connection_id, handle, OPEN_CFW_ATTC_READ_MESSAGE_LONG,
        packet, continuing
    );
}
#endif

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_MULTIPLE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_read_multiple_request(
    uint8_t connection_id,
    uint8_t handle_count,
    uint16_t *handles
)
{
    union open_cfw_cordio_attc_packet_parameter *packet;
    uint8_t *cursor;
    uint16_t first_handle;
    uint8_t remaining = handle_count;
    if (handle_count == 0U || handles == NULL) {
        return;
    }
    packet = open_cfw_cordio_att_message_allocate((uint16_t)(
        OPEN_CFW_ATTC_READ_MULTIPLE_BUFFER_LENGTH
        + ((uint16_t)handle_count * 2U)
    ));
    if (packet == NULL) {
        return;
    }
    packet->length = (uint16_t)(
        OPEN_CFW_ATTC_READ_MULTIPLE_LENGTH
        + ((uint16_t)handle_count * 2U)
    );
    first_handle = handles[0];
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_READ_MULTIPLE_REQUEST;
    while (remaining != 0U) {
        open_cfw_cordio_attc_read_write_u16(cursor, *handles++);
        cursor += 2;
        remaining--;
    }
    open_cfw_cordio_attc_send_message(
        connection_id, first_handle, OPEN_CFW_ATTC_READ_MESSAGE_MULTIPLE,
        packet, OPEN_CFW_ATTC_NOT_CONTINUING
    );
}
#endif

#if defined(OPEN_CFW_ATTC_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_READ_GROUP_TYPE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_read_by_group_type_request(
    uint8_t connection_id,
    uint16_t start_handle,
    uint16_t end_handle,
    uint8_t uuid_length,
    uint8_t *uuid,
    uint8_t continuing
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        open_cfw_cordio_att_message_allocate((uint16_t)(
            OPEN_CFW_ATTC_READ_GROUP_TYPE_BUFFER_LENGTH + uuid_length
        ));
    uint8_t *cursor;
    if (packet == NULL) {
        return;
    }
    packet->handles.length = (uint16_t)(
        OPEN_CFW_ATTC_READ_GROUP_TYPE_LENGTH + uuid_length
    );
    packet->handles.start_handle = start_handle;
    packet->handles.end_handle = end_handle;
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_READ_GROUP_TYPE_REQUEST;
    cursor += 4;
    open_cfw_cordio_attc_read_copy(cursor, uuid, uuid_length);
    open_cfw_cordio_attc_send_message(
        connection_id, start_handle, OPEN_CFW_ATTC_READ_MESSAGE_GROUP_TYPE,
        packet, continuing
    );
}
#endif
