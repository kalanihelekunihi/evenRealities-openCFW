/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/apollo_main/core_overlay/pt_protocol_procsr.h"

static struct open_cfw_pt_protocol fixture_protocol;

static int fixture_echo_handler(
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *payload,
    uint8_t *payload_length,
    void *context
)
{
    uint8_t marker = *(const uint8_t *)context;
    if (request_length < 2U) {
        return -1;
    }
    payload[0] = request[0];
    payload[1] = marker;
    payload[2] = request[1];
    *payload_length = 3U;
    return 0;
}

static int fixture_maximum_length_handler(
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *payload,
    uint8_t *payload_length,
    void *context
)
{
    size_t index;
    (void)request;
    (void)request_length;
    (void)context;
    for (index = 0U; index < 251U; ++index) {
        payload[index] = (uint8_t)index;
    }
    *payload_length = 251U;
    return 0;
}

void fixture_pt_initialize(void)
{
    static const uint8_t marker = 0xC7U;
    open_cfw_pt_protocol_initialize(&fixture_protocol);
    (void)open_cfw_pt_protocol_bind(
        &fixture_protocol, 0x01U, fixture_echo_handler, (void *)&marker);
    (void)open_cfw_pt_protocol_bind(
        &fixture_protocol, 0x05U, fixture_maximum_length_handler, NULL);
}

int fixture_pt_dispatch(
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *response,
    unsigned long response_capacity,
    uint8_t *response_length
)
{
    return open_cfw_pt_protocol_dispatch(
        &fixture_protocol, request, request_length, response,
        (size_t)response_capacity, response_length);
}
