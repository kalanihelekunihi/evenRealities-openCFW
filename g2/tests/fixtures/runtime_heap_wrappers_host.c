/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the source-owned public heap wrappers.
 */

static unsigned int open_cfw_test_runtime_heap_allocate_adapter(
    unsigned int size
);
static void open_cfw_test_runtime_heap_free_adapter(
    unsigned int allocation
);

#define OPEN_CFW_RUNTIME_HEAP_ALLOCATE_ADAPTER(size) \
    open_cfw_test_runtime_heap_allocate_adapter((size))
#define OPEN_CFW_RUNTIME_HEAP_FREE_ADAPTER(allocation) \
    open_cfw_test_runtime_heap_free_adapter((allocation))

#include "../../components/apollo_main/core_overlay/runtime_heap_wrappers.c"

unsigned int open_cfw_test_runtime_heap_allocate_result;
unsigned int open_cfw_test_runtime_heap_allocate_calls;
unsigned int open_cfw_test_runtime_heap_allocate_size;
unsigned int open_cfw_test_runtime_heap_free_calls;
unsigned int open_cfw_test_runtime_heap_freed;

static unsigned int open_cfw_test_runtime_heap_allocate_adapter(
    unsigned int size
)
{
    open_cfw_test_runtime_heap_allocate_calls += 1U;
    open_cfw_test_runtime_heap_allocate_size = size;
    return open_cfw_test_runtime_heap_allocate_result;
}

static void open_cfw_test_runtime_heap_free_adapter(
    unsigned int allocation
)
{
    open_cfw_test_runtime_heap_free_calls += 1U;
    open_cfw_test_runtime_heap_freed = allocation;
}

void open_cfw_test_runtime_heap_reset(unsigned int allocation_result)
{
    open_cfw_test_runtime_heap_allocate_result = allocation_result;
    open_cfw_test_runtime_heap_allocate_calls = 0U;
    open_cfw_test_runtime_heap_allocate_size = 0U;
    open_cfw_test_runtime_heap_free_calls = 0U;
    open_cfw_test_runtime_heap_freed = 0U;
}
