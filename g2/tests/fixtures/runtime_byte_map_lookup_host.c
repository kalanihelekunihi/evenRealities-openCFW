/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter for the source-owned G2 byte-keyed map lookup.
 */

static const unsigned char *
open_cfw_test_runtime_byte_map_pointer_to_bytes(unsigned int value);
static unsigned int
open_cfw_test_runtime_byte_map_load_word(const unsigned char *source);

#define OPEN_CFW_RUNTIME_BYTE_MAP_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_byte_map_pointer_to_bytes((value))
#define OPEN_CFW_RUNTIME_BYTE_MAP_LOAD_WORD(source) \
    open_cfw_test_runtime_byte_map_load_word((source))

#include "../../components/apollo_main/core_overlay/runtime_byte_map_lookup.c"

unsigned char open_cfw_test_runtime_byte_map_storage[4096];
struct open_cfw_runtime_byte_map open_cfw_test_runtime_byte_map;
unsigned int open_cfw_test_runtime_byte_map_output;
unsigned int open_cfw_test_runtime_byte_map_pointer_calls;

static const unsigned char *
open_cfw_test_runtime_byte_map_pointer_to_bytes(unsigned int value)
{
    open_cfw_test_runtime_byte_map_pointer_calls += 1U;
    return open_cfw_test_runtime_byte_map_storage + value;
}

static unsigned int
open_cfw_test_runtime_byte_map_load_word(const unsigned char *source)
{
    return (
        (unsigned int)source[0]
        | ((unsigned int)source[1] << 8U)
        | ((unsigned int)source[2] << 16U)
        | ((unsigned int)source[3] << 24U)
    );
}

void open_cfw_test_runtime_byte_map_reset(
    unsigned int table_offset,
    unsigned int count_or_sentinel,
    unsigned int output
)
{
    open_cfw_test_runtime_byte_map.table = table_offset;
    open_cfw_test_runtime_byte_map.reserved_04 = 0x04040404U;
    open_cfw_test_runtime_byte_map.count_or_sentinel =
        (unsigned char)count_or_sentinel;
    open_cfw_test_runtime_byte_map.reserved_09 = 0x09U;
    open_cfw_test_runtime_byte_map.reserved_0a = 0x0aU;
    open_cfw_test_runtime_byte_map.reserved_0b = 0x0bU;
    open_cfw_test_runtime_byte_map_output = output;
    open_cfw_test_runtime_byte_map_pointer_calls = 0U;
}

unsigned int open_cfw_test_runtime_byte_map_execute(unsigned int key)
{
    return open_cfw_runtime_byte_map_lookup(
        &open_cfw_test_runtime_byte_map,
        key,
        &open_cfw_test_runtime_byte_map_output
    );
}
