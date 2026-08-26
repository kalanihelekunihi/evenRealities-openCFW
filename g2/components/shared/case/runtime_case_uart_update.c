/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room G2 charging-case UART and update protocol implementation.
 * The contract is recovered from the authenticated STM32G0 case image; no
 * proprietary source was used. Destructive operations are callback-only so
 * this unit cannot erase, program, swap, or reset hardware by itself.
 */
#include "runtime_case_uart_update.h"

static uint32_t open_cfw_case_read_be32(const uint8_t *bytes)
{
    return ((uint32_t)bytes[0] << 24) |
           ((uint32_t)bytes[1] << 16) |
           ((uint32_t)bytes[2] << 8) |
           (uint32_t)bytes[3];
}

uint8_t open_cfw_case_frame_checksum(uint8_t length, const uint8_t *payload)
{
    uint8_t checksum = (uint8_t)(length - 2U);
    uint8_t index;

    if (payload == NULL && length != 0U) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        checksum = (uint8_t)(checksum + payload[index]);
    }
    return checksum;
}

int open_cfw_case_frame_find_validate(const uint8_t *bytes, size_t size,
                                      open_cfw_case_frame *frame)
{
    size_t offset;
    uint8_t length;
    const uint8_t *payload;

    if (bytes == NULL || frame == NULL) {
        return OPEN_CFW_CASE_FRAME_BAD_ARGUMENT;
    }
    for (offset = 0U; offset < 4U && offset + 4U <= size; ++offset) {
        if (bytes[offset] != OPEN_CFW_CASE_FRAME_CHANNEL ||
            bytes[offset + 1U] != OPEN_CFW_CASE_FRAME_SYNC_1 ||
            bytes[offset + 2U] != OPEN_CFW_CASE_FRAME_SYNC_2) {
            continue;
        }
        length = bytes[offset + 3U];
        if (offset + 5U + (size_t)length > size) {
            return OPEN_CFW_CASE_FRAME_TRUNCATED;
        }
        payload = &bytes[offset + 4U];
        frame->command = length == 0U ? 0U : payload[0];
        frame->length = length;
        frame->payload = payload;
        frame->checksum = payload[length];
        frame->header_offset = (uint8_t)offset;
        if (open_cfw_case_frame_checksum(length, payload) != frame->checksum) {
            return OPEN_CFW_CASE_FRAME_BAD_CHECKSUM;
        }
        return OPEN_CFW_CASE_FRAME_OK;
    }
    return OPEN_CFW_CASE_FRAME_NO_HEADER;
}

uint32_t open_cfw_case_image_be32_sum(const uint8_t *bytes, size_t size)
{
    uint32_t sum = 0U;
    size_t offset;

    if (bytes == NULL || (size & 3U) != 0U) {
        return 0U;
    }
    for (offset = 0U; offset < size; offset += 4U) {
        sum += open_cfw_case_read_be32(&bytes[offset]);
    }
    return sum;
}

int open_cfw_case_parse_ota_offer(const open_cfw_case_frame *frame,
                                  open_cfw_case_ota_offer *offer)
{
    const uint8_t *payload;

    if (frame == NULL || offer == NULL || frame->payload == NULL ||
        frame->command != 0x58U || frame->length < 20U ||
        frame->payload[3] != 0x20U) {
        return 0;
    }
    payload = frame->payload;
    offer->format_major = payload[9];
    offer->version_major = payload[9];
    offer->version_minor = payload[10];
    offer->image_length = open_cfw_case_read_be32(&payload[12]);
    offer->image_checksum = open_cfw_case_read_be32(&payload[16]);
    return offer->version_major == OPEN_CFW_CASE_CURRENT_MAJOR &&
           offer->version_minor > OPEN_CFW_CASE_CURRENT_MINOR;
}

int open_cfw_case_validate_chunk(const open_cfw_case_frame *frame)
{
    const uint8_t *payload;
    uint8_t data_size;
    uint8_t sum = 0U;
    uint8_t index;

    if (frame == NULL || frame->payload == NULL || frame->command != 0x5AU ||
        frame->length < 5U) {
        return 0;
    }
    payload = frame->payload;
    if ((payload[3] & 7U) != 1U) {
        return 0;
    }
    data_size = (uint8_t)(payload[3] - 1U);
    if ((uint16_t)data_size + 5U > frame->length) {
        return 0;
    }
    for (index = 0U; index < data_size; ++index) {
        sum = (uint8_t)(sum + payload[4U + index]);
    }
    return payload[4U + data_size] == sum;
}

int open_cfw_case_channel_send_retry(uint8_t command, uint8_t length,
                                     uint8_t *payload, int fill_on_failure,
                                     open_cfw_case_channel_write writer,
                                     void *context)
{
    uint8_t attempt;
    uint8_t index;

    if (writer == NULL || (payload == NULL && length != 0U)) {
        return 0;
    }
    for (attempt = 1U; attempt < 10U; ++attempt) {
        if (writer(OPEN_CFW_CASE_FRAME_CHANNEL, command, length, payload,
                   context) != 0) {
            return 1;
        }
    }
    if (fill_on_failure != 0) {
        for (index = 0U; index < length; ++index) {
            payload[index] = 0xFFU;
        }
    }
    return 0;
}

void open_cfw_case_ota_begin(open_cfw_case_ota_context *ota,
                             const open_cfw_case_ota_offer *offer)
{
    if (ota == NULL || offer == NULL) {
        return;
    }
    ota->state = OPEN_CFW_CASE_OTA_CHECK_READY;
    ota->offer = *offer;
    ota->running_bank = 0U;
    ota->target_bank = 0U;
    ota->retry_count = 0U;
    ota->result = 0U;
}

static open_cfw_case_ota_state open_cfw_case_ota_fail(
    open_cfw_case_ota_context *ota)
{
    ota->result = 1U;
    ota->state = OPEN_CFW_CASE_OTA_INFORM_RESULT;
    return ota->state;
}

open_cfw_case_ota_state open_cfw_case_ota_advance(
    open_cfw_case_ota_context *ota, const open_cfw_case_ota_port *port)
{
    int status;

    if (ota == NULL || port == NULL) {
        return OPEN_CFW_CASE_OTA_FAILED;
    }
    switch (ota->state) {
    case OPEN_CFW_CASE_OTA_CHECK_READY:
        if (port->glasses_ready == NULL || port->glasses_ready(port->context) == 0) {
            return open_cfw_case_ota_fail(ota);
        }
        ota->state = OPEN_CFW_CASE_OTA_GET_RUNNING_BANK;
        break;
    case OPEN_CFW_CASE_OTA_GET_RUNNING_BANK:
        if (port->get_running_bank == NULL ||
            port->get_running_bank(port->context, &ota->running_bank) == 0 ||
            (ota->running_bank != 1U && ota->running_bank != 2U)) {
            return open_cfw_case_ota_fail(ota);
        }
        ota->target_bank = ota->running_bank == 1U ? 2U : 1U;
        ota->state = OPEN_CFW_CASE_OTA_ERASE_TARGET;
        break;
    case OPEN_CFW_CASE_OTA_ERASE_TARGET:
        status = port->erase_bank == NULL ? 0 :
            port->erase_bank(port->context, ota->target_bank);
        if (status == 0) {
            if (++ota->retry_count < 10U) {
                break;
            }
            return open_cfw_case_ota_fail(ota);
        }
        ota->retry_count = 0U;
        ota->state = OPEN_CFW_CASE_OTA_COPY_SERIAL;
        break;
    case OPEN_CFW_CASE_OTA_COPY_SERIAL:
        if (port->copy_serial_windows == NULL ||
            port->copy_serial_windows(port->context, ota->running_bank,
                                      ota->target_bank) == 0) {
            return open_cfw_case_ota_fail(ota);
        }
        ota->state = OPEN_CFW_CASE_OTA_RECEIVE_IMAGE;
        break;
    case OPEN_CFW_CASE_OTA_RECEIVE_IMAGE:
        if (port->receive_image == NULL ||
            port->receive_image(port->context, ota->target_bank,
                                ota->offer.image_length) == 0) {
            return open_cfw_case_ota_fail(ota);
        }
        ota->state = OPEN_CFW_CASE_OTA_VERIFY_IMAGE;
        break;
    case OPEN_CFW_CASE_OTA_VERIFY_IMAGE:
        if (port->verify_image == NULL ||
            port->verify_image(port->context, ota->target_bank,
                               ota->offer.image_length,
                               ota->offer.image_checksum) == 0) {
            return open_cfw_case_ota_fail(ota);
        }
        ota->result = 0U;
        ota->state = OPEN_CFW_CASE_OTA_INFORM_RESULT;
        break;
    case OPEN_CFW_CASE_OTA_INFORM_RESULT:
        if (port->inform_glasses == NULL ||
            port->inform_glasses(port->context, ota->result) == 0) {
            ota->state = OPEN_CFW_CASE_OTA_FAILED;
            break;
        }
        ota->state = ota->result == 0U ? OPEN_CFW_CASE_OTA_SWAP_AND_RESET :
                                        OPEN_CFW_CASE_OTA_FAILED;
        break;
    case OPEN_CFW_CASE_OTA_SWAP_AND_RESET:
        if (port->swap_and_reset == NULL ||
            port->swap_and_reset(port->context, ota->target_bank) == 0) {
            ota->state = OPEN_CFW_CASE_OTA_FAILED;
            break;
        }
        ota->state = OPEN_CFW_CASE_OTA_DONE;
        break;
    default:
        break;
    }
    return ota->state;
}
