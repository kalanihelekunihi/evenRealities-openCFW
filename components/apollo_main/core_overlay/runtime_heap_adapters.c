/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of the primary-heap adapters at
 * 0x0048431E...0x00484343 in G2 firmware 2.2.6.10.
 *
 * These functions only bind the public allocation layer to the primary
 * heap descriptor.  The source-owned generic coordinator handles locking
 * and accounting while retaining the FreeRTOS and TLSF binary seams.
 */

typedef unsigned int open_cfw_runtime_heap_adapter_word;

struct open_cfw_runtime_heap_descriptor;

enum {
    OPEN_CFW_RUNTIME_HEAP_PRIMARY_DESCRIPTOR = 0x20000338U
};

#ifndef OPEN_CFW_RUNTIME_HEAP_ADAPTER_DESCRIPTOR
#define OPEN_CFW_RUNTIME_HEAP_ADAPTER_DESCRIPTOR \
    OPEN_CFW_RUNTIME_HEAP_PRIMARY_DESCRIPTOR
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_GENERIC_ALLOCATE
open_cfw_runtime_heap_adapter_word
open_cfw_runtime_heap_generic_allocate(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    unsigned int size
);
#define OPEN_CFW_RUNTIME_HEAP_GENERIC_ALLOCATE(descriptor, size) \
    open_cfw_runtime_heap_generic_allocate( \
        (struct open_cfw_runtime_heap_descriptor *) \
            (__UINTPTR_TYPE__)(descriptor), \
        (size) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_GENERIC_REALLOCATE
open_cfw_runtime_heap_adapter_word
open_cfw_runtime_heap_generic_reallocate(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    open_cfw_runtime_heap_adapter_word allocation,
    unsigned int size
);
#define OPEN_CFW_RUNTIME_HEAP_GENERIC_REALLOCATE( \
    descriptor, \
    allocation, \
    size \
) \
    open_cfw_runtime_heap_generic_reallocate( \
        (struct open_cfw_runtime_heap_descriptor *) \
            (__UINTPTR_TYPE__)(descriptor), \
        (allocation), \
        (size) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_GENERIC_FREE
void open_cfw_runtime_heap_generic_free(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    open_cfw_runtime_heap_adapter_word allocation
);
#define OPEN_CFW_RUNTIME_HEAP_GENERIC_FREE(descriptor, allocation) \
    open_cfw_runtime_heap_generic_free( \
        (struct open_cfw_runtime_heap_descriptor *) \
            (__UINTPTR_TYPE__)(descriptor), \
        (allocation) \
    )
#endif

__attribute__((used, noinline))
open_cfw_runtime_heap_adapter_word
open_cfw_runtime_heap_allocate_adapter(unsigned int size)
{
    return OPEN_CFW_RUNTIME_HEAP_GENERIC_ALLOCATE(
        OPEN_CFW_RUNTIME_HEAP_ADAPTER_DESCRIPTOR,
        size
    );
}

__attribute__((used, noinline))
open_cfw_runtime_heap_adapter_word
open_cfw_runtime_heap_reallocate_adapter(
    open_cfw_runtime_heap_adapter_word allocation,
    unsigned int size
)
{
    return OPEN_CFW_RUNTIME_HEAP_GENERIC_REALLOCATE(
        OPEN_CFW_RUNTIME_HEAP_ADAPTER_DESCRIPTOR,
        allocation,
        size
    );
}

__attribute__((used, noinline))
void open_cfw_runtime_heap_free_adapter(
    open_cfw_runtime_heap_adapter_word allocation
)
{
    OPEN_CFW_RUNTIME_HEAP_GENERIC_FREE(
        OPEN_CFW_RUNTIME_HEAP_ADAPTER_DESCRIPTOR,
        allocation
    );
}

#undef OPEN_CFW_RUNTIME_HEAP_ADAPTER_DESCRIPTOR
#undef OPEN_CFW_RUNTIME_HEAP_GENERIC_ALLOCATE
#undef OPEN_CFW_RUNTIME_HEAP_GENERIC_REALLOCATE
#undef OPEN_CFW_RUNTIME_HEAP_GENERIC_FREE
