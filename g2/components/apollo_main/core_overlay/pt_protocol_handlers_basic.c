/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room translations of the small PT handlers at 0x00572A34,
 * 0x00572AF0, 0x00572BA0, 0x0057536C, 0x00576800, 0x00576D48, and
 * 0x00577AFC.  Provider absence and provider failure are fail-closed.
 */

#include "pt_protocol_handlers_basic.h"

static int open_cfw_pt_require_request(
    const uint8_t *request,
    uint8_t request_length,
    uint8_t minimum
)
{
    return request != NULL && request_length >= minimum ?
        OPEN_CFW_PT_OK : OPEN_CFW_PT_INVALID_ARGUMENT;
}

static int open_cfw_pt_box_handler(
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *payload,
    uint8_t *payload_length,
    void *context,
    int enabled,
    uint8_t response_command
)
{
    const struct open_cfw_pt_basic_providers *providers = context;

    if (open_cfw_pt_require_request(request, request_length, 4U) != 0 ||
        payload == NULL || payload_length == NULL || providers == NULL ||
        providers->set_box_detected == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    if (providers->set_box_detected(enabled, providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_make_status_payload(
        response_command, 0U, 3U, payload, payload_length);
}

static int open_cfw_pt_command_06(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    return open_cfw_pt_box_handler(
        request, request_length, payload, payload_length, context, 0, 0x07U);
}

static int open_cfw_pt_command_07(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    return open_cfw_pt_box_handler(
        request, request_length, payload, payload_length, context, 1, 0x08U);
}

static int open_cfw_pt_command_08(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    (void)context;
    if (open_cfw_pt_require_request(request, request_length, 4U) != 0) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    return open_cfw_pt_make_status_payload(
        0x0BU, 0U, 3U, payload, payload_length);
}

static int open_cfw_pt_command_57(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    const struct open_cfw_pt_basic_providers *providers = context;

    if (open_cfw_pt_require_request(request, request_length, 4U) != 0 ||
        providers == NULL || providers->codec_delay == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    if (providers->codec_delay(providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_make_status_payload(
        0x57U, 0U, 3U, payload, payload_length);
}

static int open_cfw_pt_command_61(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    const struct open_cfw_pt_basic_providers *providers = context;
    (void)payload;

    if (open_cfw_pt_require_request(request, request_length, 5U) != 0 ||
        payload_length == NULL || providers == NULL ||
        providers->store_terminal_mode == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    if (providers->store_terminal_mode(request[4], providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    *payload_length = 0U;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_command_65(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    const struct open_cfw_pt_basic_providers *providers = context;
    uint8_t value;
    (void)request;
    (void)request_length;

    if (providers == NULL || providers->load_terminal_mode == NULL ||
        providers->load_terminal_mode(&value, providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_make_status_payload(
        0x64U, value, 3U, payload, payload_length);
}

static int open_cfw_pt_command_f3(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, void *context)
{
    const struct open_cfw_pt_basic_providers *providers = context;
    (void)request;
    (void)request_length;

    if (providers == NULL || providers->post_input_message == NULL ||
        providers->post_input_message(providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_make_status_payload(
        0x77U, 0U, 3U, payload, payload_length);
}

int open_cfw_pt_bind_basic_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_basic_providers *providers
)
{
    static const struct {
        uint8_t command;
        open_cfw_pt_handler_fn handler;
    } bindings[] = {
        {0x06U, open_cfw_pt_command_06},
        {0x07U, open_cfw_pt_command_07},
        {0x08U, open_cfw_pt_command_08},
        {0x57U, open_cfw_pt_command_57},
        {0x61U, open_cfw_pt_command_61},
        {0x65U, open_cfw_pt_command_65},
        {0xF3U, open_cfw_pt_command_f3},
    };
    size_t index;

    if (protocol == NULL || providers == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    for (index = 0U; index < sizeof(bindings) / sizeof(bindings[0]); ++index) {
        if (open_cfw_pt_protocol_bind(
                protocol, bindings[index].command, bindings[index].handler,
                (void *)providers) != OPEN_CFW_PT_OK) {
            return OPEN_CFW_PT_HANDLER_FAILED;
        }
    }
    return OPEN_CFW_PT_OK;
}
