/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of the public heap allocation wrapper at
 * 0x0044F718...0x0044F72F and public heap free wrapper at
 * 0x0044F758...0x0044F769 in G2 firmware 2.2.6.10.
 *
 * The retained adapters preserve the stock heap descriptor, RTOS locking,
 * allocation accounting, and underlying allocator implementation.
 */

typedef unsigned int open_cfw_runtime_heap_pointer;

enum {
    OPEN_CFW_RUNTIME_HEAP_EMPTY_POINTER = 0x2006F5ACU
};

#ifndef OPEN_CFW_RUNTIME_HEAP_ALLOCATE_ADAPTER
open_cfw_runtime_heap_pointer
open_cfw_runtime_heap_allocate_adapter(unsigned int size);
#define OPEN_CFW_RUNTIME_HEAP_ALLOCATE_ADAPTER(size) \
    open_cfw_runtime_heap_allocate_adapter((size))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_FREE_ADAPTER
void open_cfw_runtime_heap_free_adapter(
    open_cfw_runtime_heap_pointer allocation
);
#define OPEN_CFW_RUNTIME_HEAP_FREE_ADAPTER(allocation) \
    open_cfw_runtime_heap_free_adapter((allocation))
#endif

__attribute__((used, noinline))
open_cfw_runtime_heap_pointer open_cfw_runtime_heap_allocate(
    unsigned int size
)
{
    if (size == 0U) {
        return OPEN_CFW_RUNTIME_HEAP_EMPTY_POINTER;
    }
    return OPEN_CFW_RUNTIME_HEAP_ALLOCATE_ADAPTER(size);
}

__attribute__((used, noinline))
void open_cfw_runtime_heap_free(open_cfw_runtime_heap_pointer allocation)
{
    if (
        allocation == 0U
        || allocation == OPEN_CFW_RUNTIME_HEAP_EMPTY_POINTER
    ) {
        return;
    }
    OPEN_CFW_RUNTIME_HEAP_FREE_ADAPTER(allocation);
}

#undef OPEN_CFW_RUNTIME_HEAP_ALLOCATE_ADAPTER
#undef OPEN_CFW_RUNTIME_HEAP_FREE_ADAPTER
