/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle for the bounded primary-heap adapter recovery.
 */

unsigned int open_cfw_test_runtime_heap_adapter_allocate_calls;
unsigned int open_cfw_test_runtime_heap_adapter_allocate_descriptor;
unsigned int open_cfw_test_runtime_heap_adapter_allocate_size;
unsigned int open_cfw_test_runtime_heap_adapter_allocate_result;

unsigned int open_cfw_test_runtime_heap_adapter_reallocate_calls;
unsigned int open_cfw_test_runtime_heap_adapter_reallocate_descriptor;
unsigned int open_cfw_test_runtime_heap_adapter_reallocate_allocation;
unsigned int open_cfw_test_runtime_heap_adapter_reallocate_size;
unsigned int open_cfw_test_runtime_heap_adapter_reallocate_result;

unsigned int open_cfw_test_runtime_heap_adapter_free_calls;
unsigned int open_cfw_test_runtime_heap_adapter_free_descriptor;
unsigned int open_cfw_test_runtime_heap_adapter_free_allocation;

static unsigned int open_cfw_test_runtime_heap_generic_allocate(
    unsigned int descriptor,
    unsigned int size
)
{
    open_cfw_test_runtime_heap_adapter_allocate_calls++;
    open_cfw_test_runtime_heap_adapter_allocate_descriptor = descriptor;
    open_cfw_test_runtime_heap_adapter_allocate_size = size;
    return open_cfw_test_runtime_heap_adapter_allocate_result;
}

static unsigned int open_cfw_test_runtime_heap_generic_reallocate(
    unsigned int descriptor,
    unsigned int allocation,
    unsigned int size
)
{
    open_cfw_test_runtime_heap_adapter_reallocate_calls++;
    open_cfw_test_runtime_heap_adapter_reallocate_descriptor = descriptor;
    open_cfw_test_runtime_heap_adapter_reallocate_allocation = allocation;
    open_cfw_test_runtime_heap_adapter_reallocate_size = size;
    return open_cfw_test_runtime_heap_adapter_reallocate_result;
}

static void open_cfw_test_runtime_heap_generic_free(
    unsigned int descriptor,
    unsigned int allocation
)
{
    open_cfw_test_runtime_heap_adapter_free_calls++;
    open_cfw_test_runtime_heap_adapter_free_descriptor = descriptor;
    open_cfw_test_runtime_heap_adapter_free_allocation = allocation;
}

#define OPEN_CFW_RUNTIME_HEAP_GENERIC_ALLOCATE(descriptor, size) \
    open_cfw_test_runtime_heap_generic_allocate((descriptor), (size))
#define OPEN_CFW_RUNTIME_HEAP_GENERIC_REALLOCATE( \
    descriptor, \
    allocation, \
    size \
) \
    open_cfw_test_runtime_heap_generic_reallocate( \
        (descriptor), \
        (allocation), \
        (size) \
    )
#define OPEN_CFW_RUNTIME_HEAP_GENERIC_FREE(descriptor, allocation) \
    open_cfw_test_runtime_heap_generic_free((descriptor), (allocation))

#include "../../components/apollo_main/core_overlay/runtime_heap_adapters.c"

void open_cfw_test_runtime_heap_adapter_reset(
    unsigned int allocate_result,
    unsigned int reallocate_result
)
{
    open_cfw_test_runtime_heap_adapter_allocate_calls = 0;
    open_cfw_test_runtime_heap_adapter_allocate_descriptor = 0;
    open_cfw_test_runtime_heap_adapter_allocate_size = 0;
    open_cfw_test_runtime_heap_adapter_allocate_result = allocate_result;

    open_cfw_test_runtime_heap_adapter_reallocate_calls = 0;
    open_cfw_test_runtime_heap_adapter_reallocate_descriptor = 0;
    open_cfw_test_runtime_heap_adapter_reallocate_allocation = 0;
    open_cfw_test_runtime_heap_adapter_reallocate_size = 0;
    open_cfw_test_runtime_heap_adapter_reallocate_result =
        reallocate_result;

    open_cfw_test_runtime_heap_adapter_free_calls = 0;
    open_cfw_test_runtime_heap_adapter_free_descriptor = 0;
    open_cfw_test_runtime_heap_adapter_free_allocation = 0;
}
