/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 Cordio ATT client optional-write implementation.
 * Behavior follows Packetcraft r20.05--r20.05c and the byte-identical
 * official AmbiqSuite R4.4.1 import.
 */

#include "runtime_cordio_attc_write.h"

#if !defined(OPEN_CFW_ATTC_WRITE_PREP_ALLOC_ONLY) && \
    !defined(OPEN_CFW_ATTC_WRITE_PROCESS_PREP_RSP_ONLY) && \
    !defined(OPEN_CFW_ATTC_WRITE_COMMAND_ONLY) && \
    !defined(OPEN_CFW_ATTC_WRITE_PREPARE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_WRITE_EXECUTE_REQUEST_ONLY)
#define OPEN_CFW_ATTC_WRITE_BUILD_ALL 1
#endif

static __attribute__((unused)) void open_cfw_cordio_attc_write_u16(
    uint8_t *destination,
    uint16_t value
)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8);
}

static __attribute__((unused)) void open_cfw_cordio_attc_copy(
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

#if defined(OPEN_CFW_ATTC_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_WRITE_PREP_ALLOC_ONLY)
__attribute__((used, noinline))
union open_cfw_cordio_attc_packet_parameter *
open_cfw_cordio_attc_prepare_write_allocate_message(uint16_t buffer_length)
{
    union open_cfw_cordio_attc_packet_parameter *packet;
    uint16_t alignment = (uint16_t)sizeof(void *);
    uint16_t remainder = (uint16_t)(buffer_length % alignment);

    if (remainder != 0U) {
        buffer_length = (uint16_t)(
            buffer_length + alignment - remainder
        );
    }
    packet = open_cfw_cordio_att_message_allocate((uint16_t)(
        buffer_length + sizeof(struct open_cfw_cordio_attc_prepare_parameter)
    ));
    if (packet != NULL) {
        packet->prepare = (struct open_cfw_cordio_attc_prepare_parameter *)(
            (uint8_t *)packet + buffer_length
        );
    }
    return packet;
}
#endif

#if defined(OPEN_CFW_ATTC_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_WRITE_PROCESS_PREP_RSP_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_process_prepare_write_response(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet,
    struct open_cfw_cordio_att_event *event
)
{
    (void)length;
    (void)packet;
    if (connection->outstanding_request.header.status
            == OPEN_CFW_ATTC_CONTINUING
        && connection->outstanding_parameters.prepare.length == 0U) {
        connection->outstanding_request.header.status =
            OPEN_CFW_ATTC_NOT_CONTINUING;
    }
    event->value += OPEN_CFW_ATTC_PREPARE_RESPONSE_VALUE_PREFIX;
    event->value_length = (uint16_t)(
        event->value_length - OPEN_CFW_ATTC_PREPARE_RESPONSE_VALUE_PREFIX
    );
}
#endif

#if defined(OPEN_CFW_ATTC_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_WRITE_COMMAND_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_write_command(
    uint8_t connection_id,
    uint16_t handle,
    uint16_t value_length,
    uint8_t *value
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        open_cfw_cordio_att_message_allocate((uint16_t)(
            OPEN_CFW_ATTC_WRITE_COMMAND_BUFFER_LENGTH + value_length
        ));
    uint8_t *cursor;

    if (packet == NULL) {
        return;
    }
    packet->length = (uint16_t)(
        OPEN_CFW_ATTC_WRITE_COMMAND_LENGTH + value_length
    );
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_PDU_WRITE_COMMAND;
    open_cfw_cordio_attc_write_u16(cursor, handle);
    cursor += 2;
    open_cfw_cordio_attc_copy(cursor, value, value_length);
    open_cfw_cordio_attc_send_message(
        connection_id,
        handle,
        OPEN_CFW_ATTC_MESSAGE_WRITE_COMMAND,
        packet,
        OPEN_CFW_ATTC_NOT_CONTINUING
    );
}
#endif

#if defined(OPEN_CFW_ATTC_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_WRITE_PREPARE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_prepare_write_request(
    uint8_t connection_id,
    uint16_t handle,
    uint16_t offset,
    uint16_t value_length,
    uint8_t *value,
    uint8_t value_by_reference,
    uint8_t continuing
)
{
    uint16_t buffer_length = OPEN_CFW_ATTC_PREPARE_REQUEST_BUFFER_LENGTH;
    union open_cfw_cordio_attc_packet_parameter *packet;
    uint8_t *cursor;

    if (!(continuing != 0U && value_by_reference != 0U)) {
        buffer_length = (uint16_t)(buffer_length + value_length);
    }
    packet = open_cfw_cordio_attc_prepare_write_allocate_message(
        buffer_length
    );
    if (packet == NULL) {
        return;
    }
    packet->prepare->length = value_length;
    packet->prepare->offset = offset;
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_PDU_PREPARE_WRITE_REQUEST;
    open_cfw_cordio_attc_write_u16(cursor, handle);
    cursor += 4;
    if (continuing != 0U && value_by_reference != 0U) {
        packet->prepare->value = value;
    } else {
        open_cfw_cordio_attc_copy(cursor, value, value_length);
        packet->prepare->value = cursor;
    }
    open_cfw_cordio_attc_send_message(
        connection_id,
        handle,
        OPEN_CFW_ATTC_MESSAGE_PREPARE_WRITE,
        packet,
        continuing
    );
}
#endif

#if defined(OPEN_CFW_ATTC_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTC_WRITE_EXECUTE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_attc_execute_write_request(
    uint8_t connection_id,
    uint8_t write_all
)
{
    union open_cfw_cordio_attc_packet_parameter *packet =
        open_cfw_cordio_att_message_allocate(
            OPEN_CFW_ATTC_EXECUTE_REQUEST_BUFFER_LENGTH
        );
    uint8_t *cursor;

    if (packet == NULL) {
        return;
    }
    packet->length = OPEN_CFW_ATTC_EXECUTE_REQUEST_LENGTH;
    cursor = (uint8_t *)packet + OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START;
    *cursor++ = OPEN_CFW_ATTC_PDU_EXECUTE_WRITE_REQUEST;
    *cursor = write_all;
    open_cfw_cordio_attc_send_message(
        connection_id,
        0U,
        OPEN_CFW_ATTC_MESSAGE_EXECUTE_WRITE,
        packet,
        OPEN_CFW_ATTC_NOT_CONTINUING
    );
}
#endif
