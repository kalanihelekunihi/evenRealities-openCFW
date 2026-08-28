/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter for the source-owned G2 transition-descriptor initializer.
 */

static void *open_cfw_test_runtime_transition_memory_zero(
    void *destination,
    unsigned int size
);

#define OPEN_CFW_RUNTIME_TRANSITION_MEMORY_ZERO(destination, size) \
    open_cfw_test_runtime_transition_memory_zero((destination), (size))

#include "../../components/apollo_main/core_overlay/runtime_transition_descriptor_init.c"

struct open_cfw_runtime_transition_descriptor
    open_cfw_test_runtime_transition_descriptor;
unsigned int open_cfw_test_runtime_transition_memory_zero_calls;
unsigned int open_cfw_test_runtime_transition_memory_zero_size;
void *open_cfw_test_runtime_transition_memory_zero_destination;
unsigned char open_cfw_test_runtime_transition_memory_zero_before[20];

static void *open_cfw_test_runtime_transition_memory_zero(
    void *destination,
    unsigned int size
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    open_cfw_test_runtime_transition_memory_zero_calls += 1U;
    open_cfw_test_runtime_transition_memory_zero_size = size;
    open_cfw_test_runtime_transition_memory_zero_destination = destination;
    for (index = 0U; index < sizeof(
        open_cfw_test_runtime_transition_memory_zero_before
    ); index += 1U) {
        open_cfw_test_runtime_transition_memory_zero_before[index] =
            bytes[index];
    }
    for (index = 0U; index < size; index += 1U) {
        bytes[index] = 0U;
    }
    return destination;
}

void open_cfw_test_runtime_transition_reset(unsigned int seed)
{
    unsigned char *bytes =
        (unsigned char *)&open_cfw_test_runtime_transition_descriptor;
    unsigned int index;

    for (index = 0U; index < sizeof(
        open_cfw_test_runtime_transition_descriptor
    ); index += 1U) {
        bytes[index] = (unsigned char)(seed + index * 29U);
    }
    open_cfw_test_runtime_transition_memory_zero_calls = 0U;
    open_cfw_test_runtime_transition_memory_zero_size = 0U;
    open_cfw_test_runtime_transition_memory_zero_destination = (void *)0;
    for (index = 0U; index < sizeof(
        open_cfw_test_runtime_transition_memory_zero_before
    ); index += 1U) {
        open_cfw_test_runtime_transition_memory_zero_before[index] = 0U;
    }
}

unsigned int open_cfw_test_runtime_transition_execute(
    unsigned int properties,
    unsigned int path_callback,
    unsigned int duration,
    unsigned int delay,
    unsigned int user_data
)
{
    return open_cfw_runtime_transition_descriptor_init(
        &open_cfw_test_runtime_transition_descriptor,
        properties,
        path_callback,
        duration,
        delay,
        user_data
    );
}
