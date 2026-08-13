/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the source-owned G2 style reset routine.
 */

static void open_cfw_test_runtime_style_reset_free(void *allocation);
static void *open_cfw_test_runtime_style_reset_memory_zero(
    void *destination,
    unsigned int size
);

#define OPEN_CFW_RUNTIME_STYLE_RESET_FREE(allocation) \
    open_cfw_test_runtime_style_reset_free((allocation))
#define OPEN_CFW_RUNTIME_STYLE_RESET_MEMORY_ZERO(destination, size) \
    open_cfw_test_runtime_style_reset_memory_zero((destination), (size))

#include "../../components/apollo_main/core_overlay/runtime_style_reset.c"

struct open_cfw_runtime_style_reset_descriptor
    open_cfw_test_runtime_style_reset_descriptor;
unsigned char open_cfw_test_runtime_style_reset_zero_before[12];
unsigned int open_cfw_test_runtime_style_reset_free_calls;
unsigned int open_cfw_test_runtime_style_reset_zero_calls;
unsigned int open_cfw_test_runtime_style_reset_zero_size;
unsigned int open_cfw_test_runtime_style_reset_sequence;
unsigned int open_cfw_test_runtime_style_reset_free_order;
unsigned int open_cfw_test_runtime_style_reset_zero_order;
void *open_cfw_test_runtime_style_reset_free_allocation;
void *open_cfw_test_runtime_style_reset_zero_destination;

static void open_cfw_test_runtime_style_reset_free(void *allocation)
{
    open_cfw_test_runtime_style_reset_free_calls += 1U;
    open_cfw_test_runtime_style_reset_free_allocation = allocation;
    open_cfw_test_runtime_style_reset_sequence += 1U;
    open_cfw_test_runtime_style_reset_free_order =
        open_cfw_test_runtime_style_reset_sequence;
}

static void *open_cfw_test_runtime_style_reset_memory_zero(
    void *destination,
    unsigned int size
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    open_cfw_test_runtime_style_reset_zero_calls += 1U;
    open_cfw_test_runtime_style_reset_zero_size = size;
    open_cfw_test_runtime_style_reset_zero_destination = destination;
    open_cfw_test_runtime_style_reset_sequence += 1U;
    open_cfw_test_runtime_style_reset_zero_order =
        open_cfw_test_runtime_style_reset_sequence;
    for (index = 0U; index < 12U; index += 1U) {
        open_cfw_test_runtime_style_reset_zero_before[index] = bytes[index];
    }
    for (index = 0U; index < size; index += 1U) {
        bytes[index] = 0U;
    }
    return destination;
}

void open_cfw_test_runtime_style_reset_install(
    unsigned int table,
    unsigned int property_groups,
    unsigned int count
)
{
    unsigned int index;

    open_cfw_test_runtime_style_reset_descriptor.table = table;
    open_cfw_test_runtime_style_reset_descriptor.property_groups =
        property_groups;
    open_cfw_test_runtime_style_reset_descriptor.count_or_static =
        (unsigned char)count;
    open_cfw_test_runtime_style_reset_descriptor.reserved_09 = 0x19U;
    open_cfw_test_runtime_style_reset_descriptor.reserved_0a = 0x2AU;
    open_cfw_test_runtime_style_reset_descriptor.reserved_0b = 0x3BU;
    for (index = 0U; index < 12U; index += 1U) {
        open_cfw_test_runtime_style_reset_zero_before[index] = 0U;
    }
    open_cfw_test_runtime_style_reset_free_calls = 0U;
    open_cfw_test_runtime_style_reset_zero_calls = 0U;
    open_cfw_test_runtime_style_reset_zero_size = 0U;
    open_cfw_test_runtime_style_reset_sequence = 0U;
    open_cfw_test_runtime_style_reset_free_order = 0U;
    open_cfw_test_runtime_style_reset_zero_order = 0U;
    open_cfw_test_runtime_style_reset_free_allocation = (void *)0;
    open_cfw_test_runtime_style_reset_zero_destination = (void *)0;
}

void open_cfw_test_runtime_style_reset_execute(void)
{
    open_cfw_runtime_style_reset(
        &open_cfw_test_runtime_style_reset_descriptor
    );
}
