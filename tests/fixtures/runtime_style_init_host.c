/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 style initializer.
 */

static void *open_cfw_test_runtime_style_init_memory_zero(
    void *destination,
    unsigned int size
);

#define OPEN_CFW_RUNTIME_STYLE_INIT_MEMORY_ZERO(destination, size) \
    open_cfw_test_runtime_style_init_memory_zero((destination), (size))

#include "../../components/apollo_main/core_overlay/runtime_style_init.c"

unsigned char open_cfw_test_runtime_style_init_storage[20];
unsigned char open_cfw_test_runtime_style_init_before[12];
unsigned int open_cfw_test_runtime_style_init_zero_calls;
unsigned int open_cfw_test_runtime_style_init_zero_size;
void *open_cfw_test_runtime_style_init_zero_destination;

static void *open_cfw_test_runtime_style_init_memory_zero(
    void *destination,
    unsigned int size
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    open_cfw_test_runtime_style_init_zero_calls += 1U;
    open_cfw_test_runtime_style_init_zero_size = size;
    open_cfw_test_runtime_style_init_zero_destination = destination;
    for (index = 0U; index < 12U; index += 1U) {
        open_cfw_test_runtime_style_init_before[index] = bytes[index];
    }
    for (index = 0U; index < size; index += 1U) {
        bytes[index] = 0U;
    }
    return destination;
}

void open_cfw_test_runtime_style_init_reset(unsigned int seed)
{
    unsigned int index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_runtime_style_init_storage);
        index += 1U
    ) {
        open_cfw_test_runtime_style_init_storage[index] =
            (unsigned char)(seed + index * 29U);
    }
    for (index = 0U; index < 12U; index += 1U) {
        open_cfw_test_runtime_style_init_before[index] = 0U;
    }
    open_cfw_test_runtime_style_init_zero_calls = 0U;
    open_cfw_test_runtime_style_init_zero_size = 0U;
    open_cfw_test_runtime_style_init_zero_destination = (void *)0;
}

void open_cfw_test_runtime_style_init_execute(void)
{
    open_cfw_runtime_style_init(open_cfw_test_runtime_style_init_storage);
}
