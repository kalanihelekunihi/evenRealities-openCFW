/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of the generic heap coordinator at
 * 0x0048413C...0x004842E5 in G2 firmware 2.2.6.10.
 *
 * The coordinator owns descriptor initialization, RTOS serialization, and
 * allocation accounting.  The FreeRTOS queue primitives and TLSF allocator
 * remain explicit retained dependencies.
 */

typedef unsigned int open_cfw_runtime_heap_word;

struct open_cfw_runtime_heap_descriptor {
    open_cfw_runtime_heap_word mutex;
    open_cfw_runtime_heap_word allocator;
    unsigned int current_bytes;
    unsigned int peak_bytes;
    unsigned int arena_size;
    open_cfw_runtime_heap_word arena;
    unsigned char policy;
    unsigned char reserved[3];
};

_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_heap_descriptor, mutex) == 0U,
    "heap mutex offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_heap_descriptor,
        allocator
    ) == 4U,
    "heap allocator offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_heap_descriptor,
        current_bytes
    ) == 8U,
    "heap current-byte offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_heap_descriptor,
        peak_bytes
    ) == 12U,
    "heap peak-byte offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_heap_descriptor,
        arena_size
    ) == 16U,
    "heap arena-size offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_heap_descriptor, arena) == 20U,
    "heap arena offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_heap_descriptor, policy) == 24U,
    "heap policy offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_heap_descriptor) == 28U,
    "heap descriptor ABI changed"
);

enum {
    OPEN_CFW_RUNTIME_HEAP_WAIT_FOREVER = 0xFFFFFFFFU,
    OPEN_CFW_RUNTIME_HEAP_MUTEX_TYPE = 1U,
    OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRED = 1U
};

#ifndef OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC
unsigned int open_cfw_log_format_dispatch(const char *format, ...);
#define OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC(message) \
    ((void)open_cfw_log_format_dispatch((message)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_FATAL
#define OPEN_CFW_RUNTIME_HEAP_FATAL() \
    do { \
        for (;;) { \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_MUTEX_CREATE
typedef open_cfw_runtime_heap_word
(*open_cfw_runtime_heap_mutex_create_fn)(unsigned int mutex_type);
#define OPEN_CFW_RUNTIME_HEAP_MUTEX_CREATE(mutex_type) \
    (((open_cfw_runtime_heap_mutex_create_fn) \
        (__UINTPTR_TYPE__)0x004416D7U)((mutex_type)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE
typedef unsigned int (*open_cfw_runtime_heap_mutex_acquire_fn)(
    open_cfw_runtime_heap_word mutex,
    unsigned int timeout
);
#define OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(mutex, timeout) \
    (((open_cfw_runtime_heap_mutex_acquire_fn) \
        (__UINTPTR_TYPE__)0x00441C45U)((mutex), (timeout)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE
typedef unsigned int (*open_cfw_runtime_heap_mutex_release_fn)(
    open_cfw_runtime_heap_word mutex,
    open_cfw_runtime_heap_word argument1,
    unsigned int argument2,
    unsigned int argument3
);
#define OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE( \
    mutex, \
    argument1, \
    argument2, \
    argument3 \
) \
    ((void)((open_cfw_runtime_heap_mutex_release_fn) \
        (__UINTPTR_TYPE__)0x004417EFU)( \
            (mutex), \
            (argument1), \
            (argument2), \
            (argument3) \
        ))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_TLSF_CREATE_WITH_POOL
typedef open_cfw_runtime_heap_word
(*open_cfw_runtime_heap_tlsf_create_with_pool_fn)(
    open_cfw_runtime_heap_word arena,
    unsigned int arena_size
);
#define OPEN_CFW_RUNTIME_HEAP_TLSF_CREATE_WITH_POOL(arena, arena_size) \
    (((open_cfw_runtime_heap_tlsf_create_with_pool_fn) \
        (__UINTPTR_TYPE__)0x004D06EDU)((arena), (arena_size)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE
typedef unsigned int (*open_cfw_runtime_heap_tlsf_block_size_fn)(
    open_cfw_runtime_heap_word allocation
);
#define OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(allocation) \
    (((open_cfw_runtime_heap_tlsf_block_size_fn) \
        (__UINTPTR_TYPE__)0x004D05E5U)((allocation)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_TLSF_ALLOCATE
typedef open_cfw_runtime_heap_word
(*open_cfw_runtime_heap_tlsf_allocate_fn)(
    open_cfw_runtime_heap_word allocator,
    unsigned int size
);
#define OPEN_CFW_RUNTIME_HEAP_TLSF_ALLOCATE(allocator, size) \
    (((open_cfw_runtime_heap_tlsf_allocate_fn) \
        (__UINTPTR_TYPE__)0x004D0723U)((allocator), (size)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_TLSF_MEMALIGN
typedef open_cfw_runtime_heap_word
(*open_cfw_runtime_heap_tlsf_memalign_fn)(
    open_cfw_runtime_heap_word allocator,
    unsigned int alignment,
    unsigned int size
);
#define OPEN_CFW_RUNTIME_HEAP_TLSF_MEMALIGN(allocator, alignment, size) \
    (((open_cfw_runtime_heap_tlsf_memalign_fn) \
        (__UINTPTR_TYPE__)0x004D0745U)((allocator), (alignment), (size)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_TLSF_REALLOCATE
typedef open_cfw_runtime_heap_word
(*open_cfw_runtime_heap_tlsf_reallocate_fn)(
    open_cfw_runtime_heap_word allocator,
    open_cfw_runtime_heap_word allocation,
    unsigned int size
);
#define OPEN_CFW_RUNTIME_HEAP_TLSF_REALLOCATE(allocator, allocation, size) \
    (((open_cfw_runtime_heap_tlsf_reallocate_fn) \
        (__UINTPTR_TYPE__)0x004D0869U)((allocator), (allocation), (size)))
#endif

#ifndef OPEN_CFW_RUNTIME_HEAP_TLSF_FREE
typedef void (*open_cfw_runtime_heap_tlsf_free_fn)(
    open_cfw_runtime_heap_word allocator,
    open_cfw_runtime_heap_word allocation
);
#define OPEN_CFW_RUNTIME_HEAP_TLSF_FREE(allocator, allocation) \
    (((open_cfw_runtime_heap_tlsf_free_fn) \
        (__UINTPTR_TYPE__)0x004D0809U)((allocator), (allocation)))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_heap_generic_initialize(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    open_cfw_runtime_heap_word arena,
    unsigned int arena_size
)
{
    descriptor->allocator =
        OPEN_CFW_RUNTIME_HEAP_TLSF_CREATE_WITH_POOL(arena, arena_size);
    if (descriptor->allocator == 0U) {
        OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC(
            "TLSF memory pool creation failed!\n"
        );
        OPEN_CFW_RUNTIME_HEAP_FATAL();
        return;
    }

    descriptor->mutex =
        OPEN_CFW_RUNTIME_HEAP_MUTEX_CREATE(
            OPEN_CFW_RUNTIME_HEAP_MUTEX_TYPE
        );
    if (descriptor->mutex == 0U) {
        OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC(
            "TLSF mutex creation failed!\n"
        );
        OPEN_CFW_RUNTIME_HEAP_FATAL();
        return;
    }

    descriptor->current_bytes = 0U;
    descriptor->peak_bytes = 0U;
    descriptor->arena_size = arena_size;
    descriptor->arena = arena;
}

__attribute__((used, noinline))
open_cfw_runtime_heap_word open_cfw_runtime_heap_generic_allocate(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    unsigned int size
)
{
    open_cfw_runtime_heap_word allocation = 0U;

    if (size == 0U) {
        return 0U;
    }

    if (
        OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(
            descriptor->mutex,
            OPEN_CFW_RUNTIME_HEAP_WAIT_FOREVER
        ) == OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRED
    ) {
        allocation = OPEN_CFW_RUNTIME_HEAP_TLSF_ALLOCATE(
            descriptor->allocator,
            size
        );
        if (allocation != 0U) {
            descriptor->current_bytes +=
                OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(allocation);
            if (descriptor->peak_bytes < descriptor->current_bytes) {
                descriptor->peak_bytes = descriptor->current_bytes;
            }
        }
        OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE(
            descriptor->mutex,
            0U,
            0U,
            0U
        );
    }

    return allocation;
}

__attribute__((used, noinline))
open_cfw_runtime_heap_word open_cfw_runtime_heap_generic_memalign(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    unsigned int size,
    unsigned int alignment
)
{
    open_cfw_runtime_heap_word allocation = 0U;

    if (size == 0U) {
        return 0U;
    }

    if (
        OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(
            descriptor->mutex,
            OPEN_CFW_RUNTIME_HEAP_WAIT_FOREVER
        ) == OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRED
    ) {
        allocation = OPEN_CFW_RUNTIME_HEAP_TLSF_MEMALIGN(
            descriptor->allocator,
            alignment,
            size
        );
        if (allocation != 0U) {
            descriptor->current_bytes +=
                OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(allocation);
            if (descriptor->peak_bytes < descriptor->current_bytes) {
                descriptor->peak_bytes = descriptor->current_bytes;
            }
        }
        OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE(
            descriptor->mutex,
            0U,
            0U,
            0U
        );
    }

    return allocation;
}

__attribute__((used, noinline))
open_cfw_runtime_heap_word open_cfw_runtime_heap_generic_reallocate(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    open_cfw_runtime_heap_word allocation,
    unsigned int size
)
{
    open_cfw_runtime_heap_word resized = 0U;

    if (
        OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(
            descriptor->mutex,
            OPEN_CFW_RUNTIME_HEAP_WAIT_FOREVER
        ) == OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRED
    ) {
        unsigned int old_size =
            OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(allocation);

        resized = OPEN_CFW_RUNTIME_HEAP_TLSF_REALLOCATE(
            descriptor->allocator,
            allocation,
            size
        );
        if (resized != 0U) {
            descriptor->current_bytes -= old_size;
            descriptor->current_bytes +=
                OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(resized);
            if (descriptor->peak_bytes < descriptor->current_bytes) {
                descriptor->peak_bytes = descriptor->current_bytes;
            }
        }
        OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE(
            descriptor->mutex,
            0U,
            0U,
            0U
        );
    }

    return resized;
}

__attribute__((used, noinline))
void open_cfw_runtime_heap_generic_free(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    open_cfw_runtime_heap_word allocation
)
{
    unsigned int allocation_size;

    if (allocation == 0U) {
        return;
    }

    if (
        OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(
            descriptor->mutex,
            OPEN_CFW_RUNTIME_HEAP_WAIT_FOREVER
        ) != OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRED
    ) {
        return;
    }

    allocation_size =
        OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(allocation);
    OPEN_CFW_RUNTIME_HEAP_TLSF_FREE(
        descriptor->allocator,
        allocation
    );
    if (allocation_size < descriptor->current_bytes) {
        descriptor->current_bytes -= allocation_size;
    }
    else {
        descriptor->current_bytes = 0U;
    }
    OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE(
        descriptor->mutex,
        0U,
        0U,
        0U
    );
}

#undef OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC
#undef OPEN_CFW_RUNTIME_HEAP_FATAL
#undef OPEN_CFW_RUNTIME_HEAP_MUTEX_CREATE
#undef OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE
#undef OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE
#undef OPEN_CFW_RUNTIME_HEAP_TLSF_CREATE_WITH_POOL
#undef OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE
#undef OPEN_CFW_RUNTIME_HEAP_TLSF_ALLOCATE
#undef OPEN_CFW_RUNTIME_HEAP_TLSF_MEMALIGN
#undef OPEN_CFW_RUNTIME_HEAP_TLSF_REALLOCATE
#undef OPEN_CFW_RUNTIME_HEAP_TLSF_FREE
