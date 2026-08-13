/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 byte-map lookup adapter.
 */

static unsigned int open_cfw_test_runtime_byte_map_lookup(
    const void *map,
    unsigned int key,
    unsigned int *result
);

#define OPEN_CFW_RUNTIME_BYTE_MAP_LOOKUP(map, key, result) \
    open_cfw_test_runtime_byte_map_lookup((map), (key), (result))

#include "../../components/apollo_main/core_overlay/runtime_byte_map_lookup_u8.c"

unsigned int open_cfw_test_runtime_byte_map_lookup_calls;
unsigned int open_cfw_test_runtime_byte_map_lookup_key;
unsigned int open_cfw_test_runtime_byte_map_lookup_return;
unsigned int open_cfw_test_runtime_byte_map_lookup_value;
unsigned int open_cfw_test_runtime_byte_map_lookup_write;
const void *open_cfw_test_runtime_byte_map_lookup_map;
unsigned int *open_cfw_test_runtime_byte_map_lookup_result;

void open_cfw_test_runtime_byte_map_lookup_reset(
    unsigned int return_value,
    unsigned int output_value,
    unsigned int write_output
)
{
    open_cfw_test_runtime_byte_map_lookup_calls = 0U;
    open_cfw_test_runtime_byte_map_lookup_key = 0U;
    open_cfw_test_runtime_byte_map_lookup_return = return_value;
    open_cfw_test_runtime_byte_map_lookup_value = output_value;
    open_cfw_test_runtime_byte_map_lookup_write = write_output;
    open_cfw_test_runtime_byte_map_lookup_map = (const void *)0;
    open_cfw_test_runtime_byte_map_lookup_result = (unsigned int *)0;
}

static unsigned int open_cfw_test_runtime_byte_map_lookup(
    const void *map,
    unsigned int key,
    unsigned int *result
)
{
    open_cfw_test_runtime_byte_map_lookup_calls += 1U;
    open_cfw_test_runtime_byte_map_lookup_map = map;
    open_cfw_test_runtime_byte_map_lookup_key = key;
    open_cfw_test_runtime_byte_map_lookup_result = result;
    if (open_cfw_test_runtime_byte_map_lookup_write != 0U) {
        *result = open_cfw_test_runtime_byte_map_lookup_value;
    }
    return open_cfw_test_runtime_byte_map_lookup_return;
}
