/* SPDX-License-Identifier: MIT */
#include "pt_protocol_handlers_data.h"

static int open_cfw_pt_data_request_valid(
    const uint8_t *request, uint8_t length)
{
    return request != NULL && length >= 4U;
}

static void open_cfw_pt_data_copy(
    uint8_t *destination, const uint8_t *source, size_t length)
{
    size_t index;
    for (index = 0U; index < length; ++index) {
        destination[index] = source[index];
    }
}

static size_t open_cfw_pt_data_text_length(const char *text, size_t limit)
{
    size_t length = 0U;
    if (text == NULL) {
        return 0U;
    }
    while (length < limit && text[length] != '\0') {
        ++length;
    }
    return length;
}

static void open_cfw_pt_data_u32_le(uint8_t *output, uint32_t value)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8U);
    output[2] = (uint8_t)(value >> 16U);
    output[3] = (uint8_t)(value >> 24U);
}

static int open_cfw_pt_data_header(
    uint8_t response_command, uint8_t tag, uint8_t data_length,
    uint8_t *payload, uint8_t *payload_length)
{
    if (payload == NULL || payload_length == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    payload[0] = response_command;
    payload[1] = 1U;
    payload[2] = tag;
    payload[3] = data_length;
    *payload_length = (uint8_t)(4U + data_length);
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_data_fixed(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, const struct open_cfw_pt_data_providers *providers,
    open_cfw_pt_data_read_fixed_fn provider, uint8_t response_command,
    uint8_t length)
{
    if (!open_cfw_pt_data_request_valid(request, request_length) ||
        providers == NULL || provider == NULL ||
        open_cfw_pt_data_header(response_command, 3U, length, payload,
            payload_length) != 0) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    return provider(payload + 4U, length, providers->context) == 0 ?
        OPEN_CFW_PT_OK : OPEN_CFW_PT_HANDLER_FAILED;
}

static int open_cfw_pt_data_text(
    const uint8_t *request, uint8_t request_length, uint8_t *payload,
    uint8_t *payload_length, const struct open_cfw_pt_data_providers *providers,
    open_cfw_pt_data_read_text_fn provider, unsigned int index,
    uint8_t response_command, size_t maximum)
{
    const char *text;
    size_t length;

    if (!open_cfw_pt_data_request_valid(request, request_length) ||
        providers == NULL || provider == NULL ||
        provider(index, &text, providers->context) != 0 || text == NULL) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    length = open_cfw_pt_data_text_length(text, maximum);
    if (open_cfw_pt_data_header(response_command, 3U, (uint8_t)length,
            payload, payload_length) != 0) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    open_cfw_pt_data_copy(payload + 4U, (const uint8_t *)text, length);
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_data_05(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    return open_cfw_pt_data_fixed(
        r, n, p, l, providers,
        providers == NULL ? NULL : providers->read_identifier_6, 0x05U, 6U);
}

static int open_cfw_pt_data_25(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    return open_cfw_pt_data_text(
        r, n, p, l, providers,
        providers == NULL ? NULL : providers->read_system_text,
        1U, 0x2AU, 21U);
}

static int open_cfw_pt_data_35(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    if (!open_cfw_pt_data_request_valid(r, n) || providers == NULL ||
        providers->set_sync_ready == NULL ||
        providers->set_sync_ready(1, providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_make_status_payload(0x06U, 0U, 3U, p, l);
}

static int open_cfw_pt_data_39(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    return open_cfw_pt_data_text(
        r, n, p, l, providers,
        providers == NULL ? NULL : providers->read_system_text,
        0U, 0x22U, 14U);
}

static int open_cfw_pt_data_44(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    uint8_t value;
    if (!open_cfw_pt_data_request_valid(r, n) || providers == NULL ||
        providers->read_boolean_flag == NULL ||
        providers->read_boolean_flag(&value, providers->context) != 0 ||
        open_cfw_pt_data_header(0x46U, 2U, 1U, p, l) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    p[4] = value != 0U ? 1U : 0U;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_data_45(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    uint8_t first;
    uint8_t second;
    if (!open_cfw_pt_data_request_valid(r, n) || providers == NULL ||
        providers->read_pair_state == NULL ||
        providers->read_pair_state(&first, &second, providers->context) != 0 ||
        open_cfw_pt_data_header(0x39U, 3U, 4U, p, l) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    p[4] = 0U;
    p[5] = first;
    p[6] = 0U;
    p[7] = second;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_data_46(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    struct open_cfw_pt_session_status status;
    uint32_t first_elapsed;
    uint32_t second_elapsed;
    if (!open_cfw_pt_data_request_valid(r, n) || providers == NULL ||
        providers->read_session_status == NULL ||
        providers->read_session_status(&status, providers->context) != 0 ||
        open_cfw_pt_data_header(0x3DU, 3U, 12U, p, l) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    first_elapsed = open_cfw_pt_elapsed_seconds(
        &status.first, &status.reference, 86400U);
    second_elapsed = open_cfw_pt_elapsed_seconds(
        &status.second, &status.reference, 86400U);
    p[4] = status.state;
    open_cfw_pt_data_u32_le(p + 5U, first_elapsed);
    open_cfw_pt_data_u32_le(p + 9U, second_elapsed);
    p[13] = status.flag_a;
    p[14] = status.flag_b;
    p[15] = status.flag_c;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_data_67(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    (void)c;
    if (!open_cfw_pt_data_request_valid(r, n)) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    return open_cfw_pt_make_status_payload(0x66U, 0U, 3U, p, l);
}

static int open_cfw_pt_data_69(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    return open_cfw_pt_data_fixed(
        r, n, p, l, providers,
        providers == NULL ? NULL : providers->read_diagnostic_blob_36,
        0x67U, 36U);
}

static int open_cfw_pt_data_6b(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    const char *version;
    if (!open_cfw_pt_data_request_valid(r, n) || providers == NULL ||
        providers->read_font_version == NULL ||
        providers->read_font_version(0U, &version, providers->context) != 0 ||
        version == NULL || open_cfw_pt_data_text_length(version, 5U) < 5U ||
        open_cfw_pt_data_header(0x6AU, 3U, 3U, p, l) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    p[4] = (uint8_t)(version[0] - '0');
    p[5] = (uint8_t)(version[2] - '0');
    p[6] = (uint8_t)(version[4] - '0');
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_data_6c(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_data_providers *providers = c;
    uint8_t value;
    if (!open_cfw_pt_data_request_valid(r, n) || providers == NULL ||
        providers->read_display_value == NULL ||
        providers->read_display_value(&value, providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_make_status_payload(0x6BU, value, 3U, p, l);
}

static int open_cfw_pt_data_6d(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    (void)c;
    if (!open_cfw_pt_data_request_valid(r, n)) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    return open_cfw_pt_make_status_payload(0x6CU, 0U, 3U, p, l);
}

int open_cfw_pt_bind_data_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_data_providers *providers)
{
    static const struct { uint8_t command; open_cfw_pt_handler_fn handler; }
        bindings[] = {
            {0x05U, open_cfw_pt_data_05}, {0x25U, open_cfw_pt_data_25},
            {0x35U, open_cfw_pt_data_35}, {0x39U, open_cfw_pt_data_39},
            {0x44U, open_cfw_pt_data_44}, {0x45U, open_cfw_pt_data_45},
            {0x46U, open_cfw_pt_data_46}, {0x67U, open_cfw_pt_data_67},
            {0x69U, open_cfw_pt_data_69}, {0x6BU, open_cfw_pt_data_6b},
            {0x6CU, open_cfw_pt_data_6c}, {0x6DU, open_cfw_pt_data_6d},
        };
    size_t index;
    if (protocol == NULL || providers == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    for (index = 0U; index < sizeof(bindings) / sizeof(bindings[0]); ++index) {
        if (open_cfw_pt_protocol_bind(protocol, bindings[index].command,
                bindings[index].handler, (void *)providers) != 0) {
            return OPEN_CFW_PT_HANDLER_FAILED;
        }
    }
    return OPEN_CFW_PT_OK;
}
