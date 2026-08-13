/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 LVGL style-property flag lookup.
 */

unsigned char open_cfw_test_runtime_style_prop_custom_storage[256];
unsigned int open_cfw_test_runtime_style_prop_custom_size;
unsigned int open_cfw_test_runtime_style_prop_custom_pointer;
unsigned int open_cfw_test_runtime_style_prop_size_reads;
unsigned int open_cfw_test_runtime_style_prop_pointer_reads;
unsigned int open_cfw_test_runtime_style_prop_pointer_resolutions;

static unsigned int open_cfw_test_runtime_style_prop_read_size(void)
{
    open_cfw_test_runtime_style_prop_size_reads += 1U;
    return open_cfw_test_runtime_style_prop_custom_size;
}

static unsigned int open_cfw_test_runtime_style_prop_read_pointer(void)
{
    open_cfw_test_runtime_style_prop_pointer_reads += 1U;
    return open_cfw_test_runtime_style_prop_custom_pointer;
}

static const unsigned char *
open_cfw_test_runtime_style_prop_resolve_pointer(unsigned int value)
{
    open_cfw_test_runtime_style_prop_pointer_resolutions += 1U;
    return open_cfw_test_runtime_style_prop_custom_storage + value;
}

#define OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_SIZE() \
    open_cfw_test_runtime_style_prop_read_size()
#define OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_POINTER() \
    open_cfw_test_runtime_style_prop_read_pointer()
#define OPEN_CFW_RUNTIME_STYLE_PROP_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_style_prop_resolve_pointer(value)

#include "../../components/apollo_main/core_overlay/runtime_style_prop_lookup_flags.c"

void open_cfw_test_runtime_style_prop_reset(
    unsigned int pointer,
    unsigned int size
)
{
    unsigned int index;

    open_cfw_test_runtime_style_prop_custom_pointer = pointer;
    open_cfw_test_runtime_style_prop_custom_size = size;
    open_cfw_test_runtime_style_prop_size_reads = 0U;
    open_cfw_test_runtime_style_prop_pointer_reads = 0U;
    open_cfw_test_runtime_style_prop_pointer_resolutions = 0U;
    for (index = 0U; index < 256U; index += 1U) {
        open_cfw_test_runtime_style_prop_custom_storage[index] = 0xa5U;
    }
}

unsigned char open_cfw_test_runtime_style_prop_builtin_flag(
    unsigned int index
)
{
    return open_cfw_runtime_style_prop_builtin_flags[index];
}
