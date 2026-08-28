/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room product-test framing and dispatch core recovered from the
 * authenticated G2 2.2.6.10 pt_protocol_procsr.c object.  Hardware command
 * handlers are provider slots and remain fail-closed until individually
 * implemented and admitted.
 */

#include "pt_protocol_procsr.h"

static const uint8_t open_cfw_pt_commands[OPEN_CFW_PT_COMMAND_COUNT] = {
    0x01U, 0x05U, 0x06U, 0x07U, 0x08U, 0x0BU, 0x11U, 0x13U,
    0x17U, 0x18U, 0x19U, 0x1AU, 0x1BU, 0x1CU, 0x20U, 0x22U,
    0x24U, 0x25U, 0x26U, 0x29U, 0x2AU, 0x2DU, 0x2EU, 0x30U,
    0x31U, 0x35U, 0x38U, 0x39U, 0x3AU, 0x3DU, 0x3EU, 0x42U,
    0x43U, 0x44U, 0x45U, 0x46U, 0x47U, 0x48U, 0x49U, 0x52U,
    0x53U, 0x54U, 0x55U, 0x57U, 0x58U, 0x59U, 0x5AU, 0x5BU,
    0x60U, 0x61U, 0x62U, 0x63U, 0x64U, 0x65U, 0x66U, 0x67U,
    0x69U, 0x6AU, 0x6BU, 0x6CU, 0x6DU, 0x6EU, 0x74U, 0x75U,
    0x77U, 0xF3U
};

static int open_cfw_pt_command_index(uint8_t command)
{
    size_t index;

    for (index = 0U; index < OPEN_CFW_PT_COMMAND_COUNT; ++index) {
        if (open_cfw_pt_commands[index] == command) {
            return (int)index;
        }
    }
    return OPEN_CFW_PT_COMMAND_NOT_FOUND;
}

static void open_cfw_pt_copy(
    uint8_t *destination,
    const uint8_t *source,
    size_t length
)
{
    size_t index;

    for (index = 0U; index < length; ++index) {
        destination[index] = source[index];
    }
}

uint32_t open_cfw_pt_elapsed_seconds(
    const struct open_cfw_pt_time *current,
    const struct open_cfw_pt_time *previous,
    uint32_t wrap_seconds
)
{
    uint32_t current_seconds;
    uint32_t previous_seconds;

    if (current == NULL || previous == NULL) {
        return 0U;
    }
    current_seconds = current->second + current->minute * 60U +
        current->hour * 3600U;
    previous_seconds = previous->second + previous->minute * 60U +
        previous->hour * 3600U;
    if (current_seconds < previous_seconds) {
        current_seconds += wrap_seconds;
    }
    return current_seconds - previous_seconds;
}

int open_cfw_pt_file_size(void *file, const struct open_cfw_pt_file_ops *ops)
{
    int original;
    int size;

    if (file == NULL || ops == NULL || ops->tell == NULL || ops->seek == NULL) {
        return -1;
    }
    original = ops->tell(file, ops->context);
    if (original < 0 || ops->seek(file, 0, 2U, ops->context) != 0) {
        return -1;
    }
    size = ops->tell(file, ops->context);
    (void)ops->seek(file, original, 0U, ops->context);
    return size < 0 ? -1 : size;
}

int open_cfw_pt_response_prefix(
    uint8_t *response,
    uint8_t payload_length,
    uint8_t *response_length
)
{
    if (response == NULL || response_length == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    response[0] = 0x5AU;
    response[1] = 0xA5U;
    response[2] = 0xFFU;
    response[3] = payload_length;
    *response_length = OPEN_CFW_PT_HEADER_SIZE;
    return OPEN_CFW_PT_OK;
}

int open_cfw_pt_response_checksum(uint8_t *response, uint8_t *response_length)
{
    uint8_t checksum = 0U;
    uint8_t index;

    if (response == NULL || response_length == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    /* The public length is one byte, so a 255-byte prefix cannot grow. */
    if (*response_length == UINT8_MAX) {
        return OPEN_CFW_PT_FRAME_TOO_LARGE;
    }
    for (index = 0U; index < *response_length; ++index) {
        checksum = (uint8_t)(checksum + response[index]);
    }
    response[*response_length] = checksum;
    *response_length = (uint8_t)(*response_length + 1U);
    return OPEN_CFW_PT_OK;
}

int open_cfw_pt_make_status_payload(
    uint8_t command,
    uint8_t value,
    uint8_t status,
    uint8_t *payload,
    uint8_t *payload_length
)
{
    if (payload == NULL || payload_length == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    payload[0] = command;
    payload[1] = 1U;
    payload[2] = status;
    payload[3] = 1U;
    payload[4] = value;
    *payload_length = 5U;
    return OPEN_CFW_PT_OK;
}

void open_cfw_pt_protocol_initialize(struct open_cfw_pt_protocol *protocol)
{
    size_t index;

    if (protocol == NULL) {
        return;
    }
    for (index = 0U; index < OPEN_CFW_PT_COMMAND_COUNT; ++index) {
        protocol->handlers[index].function = NULL;
        protocol->handlers[index].context = NULL;
    }
}

size_t open_cfw_pt_command_count(void)
{
    return OPEN_CFW_PT_COMMAND_COUNT;
}

int open_cfw_pt_command_at(size_t index, uint8_t *command)
{
    if (index >= OPEN_CFW_PT_COMMAND_COUNT || command == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    *command = open_cfw_pt_commands[index];
    return OPEN_CFW_PT_OK;
}

int open_cfw_pt_protocol_bind(
    struct open_cfw_pt_protocol *protocol,
    uint8_t command,
    open_cfw_pt_handler_fn function,
    void *context
)
{
    int index;

    if (protocol == NULL || function == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    index = open_cfw_pt_command_index(command);
    if (index < 0) {
        return index;
    }
    protocol->handlers[index].function = function;
    protocol->handlers[index].context = context;
    return OPEN_CFW_PT_OK;
}

int open_cfw_pt_protocol_dispatch(
    const struct open_cfw_pt_protocol *protocol,
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *response,
    size_t response_capacity,
    uint8_t *response_length
)
{
    uint8_t payload[OPEN_CFW_PT_MAX_FRAME_SIZE];
    uint8_t payload_length = 0U;
    uint8_t prefix_length = 0U;
    int index;
    int result;

    if (response_length != NULL) {
        *response_length = 0U;
    }
    if (protocol == NULL || request == NULL || request_length == 0U ||
        response == NULL || response_length == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }

    index = open_cfw_pt_command_index(request[0]);
    if (index < 0 || protocol->handlers[index].function == NULL) {
        result = open_cfw_pt_make_status_payload(
            request[0], 2U, 3U, payload, &payload_length);
    } else {
        result = protocol->handlers[index].function(
            request,
            request_length,
            payload,
            &payload_length,
            protocol->handlers[index].context
        );
        if (result != OPEN_CFW_PT_OK) {
            return OPEN_CFW_PT_HANDLER_FAILED;
        }
    }
    if (result != OPEN_CFW_PT_OK) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    if ((size_t)payload_length + OPEN_CFW_PT_HEADER_SIZE +
        OPEN_CFW_PT_CHECKSUM_SIZE > response_capacity ||
        (size_t)payload_length + OPEN_CFW_PT_HEADER_SIZE +
        OPEN_CFW_PT_CHECKSUM_SIZE >= OPEN_CFW_PT_MAX_FRAME_SIZE) {
        return OPEN_CFW_PT_FRAME_TOO_LARGE;
    }
    if (open_cfw_pt_response_prefix(
            response, payload_length, &prefix_length) != OPEN_CFW_PT_OK) {
        return OPEN_CFW_PT_HEADER_FAILED;
    }
    open_cfw_pt_copy(response + prefix_length, payload, payload_length);
    *response_length = (uint8_t)(prefix_length + payload_length);
    if (open_cfw_pt_response_checksum(response, response_length) !=
        OPEN_CFW_PT_OK) {
        return OPEN_CFW_PT_CHECKSUM_FAILED;
    }
    return OPEN_CFW_PT_OK;
}
