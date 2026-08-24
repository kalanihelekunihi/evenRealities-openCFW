/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the G2 OTA packet transport.  The source
 * preserves the authenticated 0xAA header, C0/C1/C2 receive paths, 4 KiB
 * assembly buffer, CRC-16/CCITT boundary, delayed receive timeout, registered
 * callbacks, and fixed product buffer ABI.  Diagnostic logging is omitted.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_OTA_MAGIC 0xAAU
#define OPEN_CFW_OTA_HEADER_BYTES 8U
#define OPEN_CFW_OTA_CRC_BYTES 2U
#define OPEN_CFW_OTA_BUFFER_BYTES 0x1020U
#define OPEN_CFW_OTA_PACKET_BUFFER_BYTES 0xF7U
#define OPEN_CFW_OTA_TIMEOUT_MS 1500U
#define OPEN_CFW_OTA_COMMAND_START 0xC0U
#define OPEN_CFW_OTA_COMMAND_DATA 0xC1U
#define OPEN_CFW_OTA_COMMAND_CONTROL 0xC2U

typedef int (*open_cfw_ota_receive_callback)(
    uint8_t command, const uint8_t *data, uint16_t length);
typedef int8_t (*open_cfw_ota_transmit_callback)(
    const uint8_t *packet, uint16_t length);
typedef void (*open_cfw_ota_timeout_callback)(void *argument);

#ifndef OPEN_CFW_OTA_TOTAL_RX
#define OPEN_CFW_OTA_TOTAL_RX \
    (*(volatile uint32_t *)(uintptr_t)0x20074850U)
#endif
#ifndef OPEN_CFW_OTA_RECEIVE_BUFFER
#define OPEN_CFW_OTA_RECEIVE_BUFFER \
    (*(uint8_t *volatile *)(uintptr_t)0x20074854U)
#endif
#ifndef OPEN_CFW_OTA_AUTHENTICATED
#define OPEN_CFW_OTA_AUTHENTICATED \
    (*(volatile uint8_t *)(uintptr_t)0x20074FF4U)
#endif
#ifndef OPEN_CFW_OTA_ERROR_PENDING
#define OPEN_CFW_OTA_ERROR_PENDING \
    (*(volatile uint8_t *)(uintptr_t)0x20074FF5U)
#endif
#ifndef OPEN_CFW_OTA_ERROR_SEQUENCE
#define OPEN_CFW_OTA_ERROR_SEQUENCE \
    (*(volatile uint8_t *)(uintptr_t)0x20074FF6U)
#endif
#ifndef OPEN_CFW_OTA_LAST_SEQUENCE
#define OPEN_CFW_OTA_LAST_SEQUENCE \
    (*(volatile uint8_t *)(uintptr_t)0x20074FF7U)
#endif
#ifndef OPEN_CFW_OTA_DEFAULT_RECEIVE_BUFFER
#define OPEN_CFW_OTA_DEFAULT_RECEIVE_BUFFER \
    (*(uint8_t *volatile *)(uintptr_t)0x2000304CU)
#endif
#ifndef OPEN_CFW_OTA_SEND_BUFFER
#define OPEN_CFW_OTA_SEND_BUFFER \
    (*(uint8_t *volatile *)(uintptr_t)0x20003050U)
#endif
#ifndef OPEN_CFW_OTA_PACKET_BUFFER
#define OPEN_CFW_OTA_PACKET_BUFFER \
    (*(uint8_t *volatile *)(uintptr_t)0x20003054U)
#endif
#ifndef OPEN_CFW_OTA_RECEIVE_CALLBACK
#define OPEN_CFW_OTA_RECEIVE_CALLBACK \
    (*(open_cfw_ota_receive_callback volatile *)(uintptr_t)0x20003058U)
#endif
#ifndef OPEN_CFW_OTA_TRANSMIT_CALLBACK
#define OPEN_CFW_OTA_TRANSMIT_CALLBACK \
    (*(open_cfw_ota_transmit_callback volatile *)(uintptr_t)0x2000305CU)
#endif
#ifndef OPEN_CFW_OTA_HEADER_TEMPLATE
#define OPEN_CFW_OTA_HEADER_TEMPLATE \
    ((const uint8_t *)(uintptr_t)0x0078DE5CU)
#endif
#ifndef OPEN_CFW_OTA_TRANSFER_STATE
#define OPEN_CFW_OTA_TRANSFER_STATE \
    (*(volatile uint32_t *)(uintptr_t)0x20354C78U)
#endif
#ifndef OPEN_CFW_OTA_TIMEOUT_CALLBACK
#define OPEN_CFW_OTA_TIMEOUT_CALLBACK \
    ((open_cfw_ota_timeout_callback)(uintptr_t)0x0048D87DU)
#endif

#ifndef OPEN_CFW_OTA_PAYLOAD_CAPACITY
uint16_t open_cfw_ota_payload_capacity(void);
#define OPEN_CFW_OTA_PAYLOAD_CAPACITY() open_cfw_ota_payload_capacity()
#endif
#ifndef OPEN_CFW_OTA_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data, uint32_t length, const uint16_t *seed);
#define OPEN_CFW_OTA_CRC16(data, length) \
    open_cfw_crc16_ccitt((data), (length), (const uint16_t *)0)
#endif
#ifndef OPEN_CFW_OTA_FREE
void open_cfw_tlsf_free(void *pointer);
#define OPEN_CFW_OTA_FREE(pointer) open_cfw_tlsf_free((pointer))
#endif
#ifndef OPEN_CFW_OTA_EVENT_REMOVE
uint8_t open_cfw_event_loop_remove_delayed(const void *callback);
#define OPEN_CFW_OTA_EVENT_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed((callback))
#endif
#ifndef OPEN_CFW_OTA_EVENT_PUSH
void open_cfw_event_loop_push_delayed(
    const void *callback, void *argument, uint32_t milliseconds);
#define OPEN_CFW_OTA_EVENT_PUSH(callback, argument, milliseconds) \
    open_cfw_event_loop_push_delayed((callback), (argument), (milliseconds))
#endif
#ifndef OPEN_CFW_OTA_REPLY_CRC_ERROR
void open_cfw_ota_reply_crc_error(uint8_t command);
#define OPEN_CFW_OTA_REPLY_CRC_ERROR(command) \
    open_cfw_ota_reply_crc_error((command))
#endif
#ifndef OPEN_CFW_OTA_REPLY_NO_RESOURCES
void open_cfw_ota_reply_no_resources(uint8_t command);
#define OPEN_CFW_OTA_REPLY_NO_RESOURCES(command) \
    open_cfw_ota_reply_no_resources((command))
#endif

uint32_t OTA_ReceivePacket(const uint8_t *packet, uint16_t packet_length);
int8_t OTA_SendPacket(uint8_t response, uint8_t destination,
    uint8_t command, const uint8_t *payload, uint16_t payload_length);
uint32_t OTA_GetTransferState(void);

#if defined(OPEN_CFW_OTA_RECEIVE_ONLY)
#define OPEN_CFW_OTA_INCLUDE_RECEIVE 1
#elif defined(OPEN_CFW_OTA_SEND_ONLY)
#define OPEN_CFW_OTA_INCLUDE_SEND 1
#elif defined(OPEN_CFW_OTA_STATE_ONLY)
#define OPEN_CFW_OTA_INCLUDE_STATE 1
#else
#define OPEN_CFW_OTA_INCLUDE_RECEIVE 1
#define OPEN_CFW_OTA_INCLUDE_SEND 1
#define OPEN_CFW_OTA_INCLUDE_STATE 1
#endif

static __attribute__((always_inline, unused)) inline void
open_cfw_ota_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}

static __attribute__((always_inline, unused)) inline void
open_cfw_ota_copy(void *raw_destination, const void *raw_source,
    uint32_t length)
{
    uint8_t *destination = raw_destination;
    const uint8_t *source = raw_source;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline, unused)) inline uint16_t
open_cfw_ota_load16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline, unused)) inline void
open_cfw_ota_store16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_ota_mark_error(uint8_t sequence, uint8_t command)
{
    OPEN_CFW_OTA_ERROR_PENDING = 1U;
    OPEN_CFW_OTA_ERROR_SEQUENCE = sequence;
    OPEN_CFW_OTA_REPLY_CRC_ERROR(command);
}

static __attribute__((always_inline, unused)) inline int
open_cfw_ota_packet_valid(const uint8_t *packet, uint16_t packet_length)
{
    return packet != 0 && packet_length >= OPEN_CFW_OTA_HEADER_BYTES &&
        (uint32_t)packet[3] + OPEN_CFW_OTA_HEADER_BYTES <= packet_length;
}

#if defined(OPEN_CFW_OTA_INCLUDE_RECEIVE)
__attribute__((used, noinline))
uint32_t OTA_ReceivePacket(const uint8_t *packet, uint16_t packet_length)
{
    uint8_t command;
    uint8_t *receive_buffer;
    uint16_t received_crc;
    uint16_t calculated_crc;
    uint32_t payload_length;

    if (!open_cfw_ota_packet_valid(packet, packet_length)) {
        return 11U;
    }
    if (packet[0] != OPEN_CFW_OTA_MAGIC) {
        return 10U;
    }
    if (packet[3] == 0U && packet_length == OPEN_CFW_OTA_HEADER_BYTES) {
        return 0U;
    }
    if (packet[4] == 0U || packet[5] == 0U || packet[5] > packet[4]) {
        return 11U;
    }

    OPEN_CFW_OTA_LAST_SEQUENCE = packet[2];
    command = packet[6];
    if (OPEN_CFW_OTA_ERROR_PENDING != 0U && packet[5] > 1U &&
            packet[2] == OPEN_CFW_OTA_ERROR_SEQUENCE) {
        return 0U;
    }

    if (command == OPEN_CFW_OTA_COMMAND_START ||
            command == OPEN_CFW_OTA_COMMAND_CONTROL) {
        if (packet[3] < OPEN_CFW_OTA_CRC_BYTES) {
            open_cfw_ota_mark_error(packet[2], command);
            return 1U;
        }
        OPEN_CFW_OTA_AUTHENTICATED = 1U;
        payload_length = (uint32_t)packet[3] - OPEN_CFW_OTA_CRC_BYTES;
        received_crc = open_cfw_ota_load16(packet + 8U + payload_length);
        calculated_crc = OPEN_CFW_OTA_CRC16(packet + 8U, payload_length);
        if (received_crc == calculated_crc) {
            if (((packet[7] & 0x3FU) >> 5) == 0U &&
                    OPEN_CFW_OTA_RECEIVE_CALLBACK != 0) {
                (void)OPEN_CFW_OTA_RECEIVE_CALLBACK(
                    command, packet + 8U, (uint16_t)payload_length);
            }
        } else {
            open_cfw_ota_mark_error(packet[2], command);
        }

        if (command == OPEN_CFW_OTA_COMMAND_START &&
                payload_length != 0U && packet[8] == 2U) {
            OPEN_CFW_OTA_TOTAL_RX = 0U;
            OPEN_CFW_OTA_RECEIVE_BUFFER = OPEN_CFW_OTA_DEFAULT_RECEIVE_BUFFER;
            OPEN_CFW_OTA_ERROR_PENDING = 0U;
            OPEN_CFW_OTA_ERROR_SEQUENCE = 0U;
            if (OPEN_CFW_OTA_RECEIVE_BUFFER == 0) {
                open_cfw_ota_mark_error(packet[2], command);
                OPEN_CFW_OTA_REPLY_NO_RESOURCES(command);
                return 4U;
            }
            open_cfw_ota_zero(
                OPEN_CFW_OTA_RECEIVE_BUFFER, OPEN_CFW_OTA_BUFFER_BYTES);
        }
        return 0U;
    }

    if (command != OPEN_CFW_OTA_COMMAND_DATA) {
        return 0U;
    }

    (void)OPEN_CFW_OTA_EVENT_REMOVE(OPEN_CFW_OTA_TIMEOUT_CALLBACK);
    OPEN_CFW_OTA_ERROR_PENDING = 0U;
    receive_buffer = OPEN_CFW_OTA_RECEIVE_BUFFER;
    if (receive_buffer == 0 && packet[5] < packet[4]) {
        return 4U;
    }
    if (receive_buffer == 0 ||
            OPEN_CFW_OTA_TOTAL_RX + packet[3] > OPEN_CFW_OTA_BUFFER_BYTES) {
        OPEN_CFW_OTA_TOTAL_RX = 0U;
        open_cfw_ota_mark_error(packet[2], command);
        return 4U;
    }

    open_cfw_ota_copy(receive_buffer + OPEN_CFW_OTA_TOTAL_RX,
        packet + 8U, packet[3]);
    OPEN_CFW_OTA_TOTAL_RX += packet[3];
    if (packet[5] < packet[4]) {
        OPEN_CFW_OTA_EVENT_PUSH(
            OPEN_CFW_OTA_TIMEOUT_CALLBACK, 0, OPEN_CFW_OTA_TIMEOUT_MS);
        return 0U;
    }
    if (OPEN_CFW_OTA_TOTAL_RX < OPEN_CFW_OTA_CRC_BYTES) {
        OPEN_CFW_OTA_TOTAL_RX = 0U;
        open_cfw_ota_mark_error(packet[2], command);
        return 1U;
    }

    OPEN_CFW_OTA_TOTAL_RX -= OPEN_CFW_OTA_CRC_BYTES;
    received_crc = open_cfw_ota_load16(
        receive_buffer + OPEN_CFW_OTA_TOTAL_RX);
    calculated_crc = OPEN_CFW_OTA_CRC16(
        receive_buffer, OPEN_CFW_OTA_TOTAL_RX);
    if (received_crc != calculated_crc) {
        if (receive_buffer != OPEN_CFW_OTA_DEFAULT_RECEIVE_BUFFER) {
            OPEN_CFW_OTA_FREE(receive_buffer);
        }
        OPEN_CFW_OTA_RECEIVE_BUFFER = 0;
        OPEN_CFW_OTA_TOTAL_RX = 0U;
        open_cfw_ota_mark_error(packet[2], command);
        return 1U;
    }

    if (OPEN_CFW_OTA_RECEIVE_CALLBACK != 0) {
        (void)OPEN_CFW_OTA_RECEIVE_CALLBACK(
            command, receive_buffer, (uint16_t)OPEN_CFW_OTA_TOTAL_RX);
    }
    if (receive_buffer != OPEN_CFW_OTA_DEFAULT_RECEIVE_BUFFER) {
        OPEN_CFW_OTA_FREE(receive_buffer);
    }
    OPEN_CFW_OTA_RECEIVE_BUFFER = 0;
    OPEN_CFW_OTA_TOTAL_RX = 0U;
    return 0U;
}
#endif

#if defined(OPEN_CFW_OTA_INCLUDE_SEND)
__attribute__((used, noinline))
int8_t OTA_SendPacket(uint8_t response, uint8_t destination,
    uint8_t command, const uint8_t *payload, uint16_t payload_length)
{
    uint8_t *send_buffer = OPEN_CFW_OTA_SEND_BUFFER;
    uint8_t *packet = OPEN_CFW_OTA_PACKET_BUFFER;
    uint8_t header[OPEN_CFW_OTA_HEADER_BYTES];
    uint16_t fragment_capacity;
    uint16_t crc;
    uint16_t offset;
    uint16_t fragment_length;
    uint16_t total_packets;
    uint16_t packet_number;
    int8_t result = 0;

    if (payload == 0 || payload_length == 0U ||
            payload_length > OPEN_CFW_OTA_BUFFER_BYTES) {
        return 11;
    }
    fragment_capacity = OPEN_CFW_OTA_PAYLOAD_CAPACITY();
    if (fragment_capacity <= 11U || send_buffer == 0 || packet == 0) {
        return 4;
    }
    fragment_capacity = (uint16_t)(fragment_capacity - 11U);
    if ((uint32_t)fragment_capacity + OPEN_CFW_OTA_HEADER_BYTES +
            OPEN_CFW_OTA_CRC_BYTES > OPEN_CFW_OTA_PACKET_BUFFER_BYTES) {
        return 4;
    }

    open_cfw_ota_zero(send_buffer, OPEN_CFW_OTA_BUFFER_BYTES);
    open_cfw_ota_copy(send_buffer, payload, payload_length);
    open_cfw_ota_zero(packet, OPEN_CFW_OTA_PACKET_BUFFER_BYTES);
    crc = OPEN_CFW_OTA_CRC16(send_buffer, payload_length);
    total_packets = (uint16_t)(((uint32_t)payload_length +
        OPEN_CFW_OTA_CRC_BYTES + fragment_capacity - 1U) /
        fragment_capacity);
    if (total_packets == 0U || total_packets > 255U) {
        return 4;
    }

    open_cfw_ota_copy(header, OPEN_CFW_OTA_HEADER_TEMPLATE,
        OPEN_CFW_OTA_HEADER_BYTES);
    header[1] = (uint8_t)((header[1] & 0x0FU) |
        ((destination & 0x0FU) << 4));
    header[2] = OPEN_CFW_OTA_LAST_SEQUENCE;
    header[4] = (uint8_t)total_packets;
    header[6] = command;
    header[7] = (uint8_t)((header[7] & 0xFEU) | (response & 1U));

    for (packet_number = 1U; packet_number <= total_packets;
            ++packet_number) {
        offset = (uint16_t)((packet_number - 1U) * fragment_capacity);
        fragment_length = fragment_capacity;
        if (packet_number == total_packets) {
            fragment_length = (uint16_t)(payload_length - offset);
        }
        header[3] = (uint8_t)(fragment_length +
            (packet_number == total_packets ? OPEN_CFW_OTA_CRC_BYTES : 0U));
        header[5] = (uint8_t)packet_number;
        open_cfw_ota_copy(packet, header, OPEN_CFW_OTA_HEADER_BYTES);
        open_cfw_ota_copy(packet + OPEN_CFW_OTA_HEADER_BYTES,
            send_buffer + offset, fragment_length);
        if (packet_number == total_packets) {
            open_cfw_ota_store16(
                packet + OPEN_CFW_OTA_HEADER_BYTES + fragment_length, crc);
        }
        if (OPEN_CFW_OTA_TRANSMIT_CALLBACK != 0) {
            result = OPEN_CFW_OTA_TRANSMIT_CALLBACK(packet,
                (uint16_t)(OPEN_CFW_OTA_HEADER_BYTES + header[3]));
        }
        if (result != 0) {
            return result;
        }
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_OTA_INCLUDE_STATE)
__attribute__((used, noinline))
uint32_t OTA_GetTransferState(void)
{
    return OPEN_CFW_OTA_TRANSFER_STATE;
}
#endif
