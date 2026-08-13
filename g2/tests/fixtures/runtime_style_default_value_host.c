/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 style-default dispatcher.
 */

static unsigned int open_cfw_test_runtime_style_default_load(
    unsigned int address
);

#define OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(address) \
    open_cfw_test_runtime_style_default_load((address))

#include "../../components/apollo_main/core_overlay/runtime_style_default_value.c"

unsigned int open_cfw_test_runtime_style_default_values[9];
unsigned int open_cfw_test_runtime_style_default_load_count;
unsigned int open_cfw_test_runtime_style_default_load_addresses[16];

static unsigned int open_cfw_test_runtime_style_default_load(
    unsigned int address
)
{
    unsigned int index;

    if (open_cfw_test_runtime_style_default_load_count < 16U) {
        open_cfw_test_runtime_style_default_load_addresses[
            open_cfw_test_runtime_style_default_load_count
        ] = address;
    }
    open_cfw_test_runtime_style_default_load_count += 1U;

    for (index = 0U; index < 9U; index += 1U) {
        if (
            address
            == OPEN_CFW_RUNTIME_STYLE_DEFAULT_COLOR_ADDRESS + index * 4U
        ) {
            return open_cfw_test_runtime_style_default_values[index];
        }
    }
    return 0xBAD0ADD0U;
}

void open_cfw_test_runtime_style_default_reset(void)
{
    unsigned int index;

    open_cfw_test_runtime_style_default_load_count = 0U;
    for (index = 0U; index < 16U; index += 1U) {
        open_cfw_test_runtime_style_default_load_addresses[index] = 0U;
    }
}

unsigned int open_cfw_test_runtime_style_default_execute(
    unsigned int property,
    unsigned int incoming_r1
)
{
    return open_cfw_runtime_style_default_value(property, incoming_r1);
}
