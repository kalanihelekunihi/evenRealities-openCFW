/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitution fixture for runtime_memory_zero.c.
 */

#include <stddef.h>
#include <stdint.h>

unsigned int open_cfw_test_runtime_memory_zero_calls;
void *open_cfw_test_runtime_memory_zero_destination;
unsigned int open_cfw_test_runtime_memory_zero_size;

void open_cfw_test_runtime_memory_zero_reset(void)
{
    open_cfw_test_runtime_memory_zero_calls = 0U;
    open_cfw_test_runtime_memory_zero_destination = NULL;
    open_cfw_test_runtime_memory_zero_size = 0U;
}

static void open_cfw_test_runtime_memory_zero_fill(
    void *destination,
    unsigned int size
)
{
    unsigned char *cursor = (unsigned char *)destination;

    open_cfw_test_runtime_memory_zero_calls += 1U;
    open_cfw_test_runtime_memory_zero_destination = destination;
    open_cfw_test_runtime_memory_zero_size = size;
    while (size != 0U) {
        *cursor = 0U;
        cursor += 1;
        size -= 1U;
    }
}

#define OPEN_CFW_RUNTIME_MEMORY_ZERO_FILL(destination, size) \
    open_cfw_test_runtime_memory_zero_fill((destination), (size))
#include "../../components/apollo_main/core_overlay/runtime_memory_zero.c"
