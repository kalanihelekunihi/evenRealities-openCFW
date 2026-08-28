/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/apollo_main/core_overlay/pt_protocol_handlers_basic.h"

static struct open_cfw_pt_protocol fixture_protocol;
static uint8_t fixture_terminal_mode;
static int fixture_box_value = -1;
static unsigned int fixture_codec_calls;
static unsigned int fixture_input_calls;

static int fixture_set_box(int enabled, void *context)
{
    (void)context;
    fixture_box_value = enabled;
    return 0;
}

static int fixture_action_codec(void *context)
{
    (void)context;
    ++fixture_codec_calls;
    return 0;
}

static int fixture_store(uint8_t value, void *context)
{
    (void)context;
    fixture_terminal_mode = value;
    return 0;
}

static int fixture_load(uint8_t *value, void *context)
{
    (void)context;
    *value = fixture_terminal_mode;
    return 0;
}

static int fixture_action_input(void *context)
{
    (void)context;
    ++fixture_input_calls;
    return 0;
}

void fixture_pt_basic_initialize(void)
{
    static const struct open_cfw_pt_basic_providers providers = {
        fixture_set_box,
        fixture_action_codec,
        fixture_store,
        fixture_load,
        fixture_action_input,
        0
    };
    fixture_terminal_mode = 0U;
    fixture_box_value = -1;
    fixture_codec_calls = 0U;
    fixture_input_calls = 0U;
    open_cfw_pt_protocol_initialize(&fixture_protocol);
    (void)open_cfw_pt_bind_basic_handlers(&fixture_protocol, &providers);
}

int fixture_pt_basic_dispatch(
    const uint8_t *request, uint8_t request_length, uint8_t *response,
    unsigned long capacity, uint8_t *response_length)
{
    return open_cfw_pt_protocol_dispatch(
        &fixture_protocol, request, request_length, response,
        (size_t)capacity, response_length);
}

int fixture_pt_basic_box_value(void) { return fixture_box_value; }
unsigned int fixture_pt_basic_codec_calls(void) { return fixture_codec_calls; }
unsigned int fixture_pt_basic_input_calls(void) { return fixture_input_calls; }
