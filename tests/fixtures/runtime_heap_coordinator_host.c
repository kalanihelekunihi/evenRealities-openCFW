/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle for the source-owned generic heap coordinator.
 */

#include <setjmp.h>

enum {
    OPEN_CFW_TEST_HEAP_EVENT_TLSF_CREATE = 1,
    OPEN_CFW_TEST_HEAP_EVENT_MUTEX_CREATE = 2,
    OPEN_CFW_TEST_HEAP_EVENT_DIAGNOSTIC = 3,
    OPEN_CFW_TEST_HEAP_EVENT_FATAL = 4,
    OPEN_CFW_TEST_HEAP_EVENT_MUTEX_ACQUIRE = 5,
    OPEN_CFW_TEST_HEAP_EVENT_MUTEX_RELEASE = 6,
    OPEN_CFW_TEST_HEAP_EVENT_TLSF_ALLOCATE = 7,
    OPEN_CFW_TEST_HEAP_EVENT_TLSF_MEMALIGN = 8,
    OPEN_CFW_TEST_HEAP_EVENT_TLSF_BLOCK_SIZE = 9,
    OPEN_CFW_TEST_HEAP_EVENT_TLSF_REALLOCATE = 10,
    OPEN_CFW_TEST_HEAP_EVENT_TLSF_FREE = 11,
    OPEN_CFW_TEST_HEAP_EVENT_CAPACITY = 64,
    OPEN_CFW_TEST_HEAP_BLOCK_SIZE_CAPACITY = 16
};

unsigned int open_cfw_test_runtime_heap_coordinator_event_count;
unsigned int open_cfw_test_runtime_heap_coordinator_event_codes[
    OPEN_CFW_TEST_HEAP_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_heap_coordinator_event_argument0[
    OPEN_CFW_TEST_HEAP_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_heap_coordinator_event_argument1[
    OPEN_CFW_TEST_HEAP_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_heap_coordinator_event_argument2[
    OPEN_CFW_TEST_HEAP_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_heap_coordinator_event_argument3[
    OPEN_CFW_TEST_HEAP_EVENT_CAPACITY
];

unsigned int open_cfw_test_runtime_heap_coordinator_tlsf_create_result;
unsigned int open_cfw_test_runtime_heap_coordinator_mutex_create_result;
unsigned int open_cfw_test_runtime_heap_coordinator_mutex_acquire_result;
unsigned int open_cfw_test_runtime_heap_coordinator_allocate_result;
unsigned int open_cfw_test_runtime_heap_coordinator_memalign_result;
unsigned int open_cfw_test_runtime_heap_coordinator_reallocate_result;
unsigned int open_cfw_test_runtime_heap_coordinator_block_sizes[
    OPEN_CFW_TEST_HEAP_BLOCK_SIZE_CAPACITY
];
unsigned int open_cfw_test_runtime_heap_coordinator_block_size_count;
unsigned int open_cfw_test_runtime_heap_coordinator_block_size_index;
const char *open_cfw_test_runtime_heap_coordinator_diagnostic_message;

static jmp_buf open_cfw_test_runtime_heap_coordinator_fatal_jump;
static unsigned int open_cfw_test_runtime_heap_coordinator_fatal_armed;

static void open_cfw_test_runtime_heap_coordinator_log_event(
    unsigned int code,
    unsigned int argument0,
    unsigned int argument1,
    unsigned int argument2,
    unsigned int argument3
)
{
    unsigned int index =
        open_cfw_test_runtime_heap_coordinator_event_count;

    if (index < OPEN_CFW_TEST_HEAP_EVENT_CAPACITY) {
        open_cfw_test_runtime_heap_coordinator_event_codes[index] = code;
        open_cfw_test_runtime_heap_coordinator_event_argument0[index] =
            argument0;
        open_cfw_test_runtime_heap_coordinator_event_argument1[index] =
            argument1;
        open_cfw_test_runtime_heap_coordinator_event_argument2[index] =
            argument2;
        open_cfw_test_runtime_heap_coordinator_event_argument3[index] =
            argument3;
    }
    open_cfw_test_runtime_heap_coordinator_event_count = index + 1U;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_message_kind(
    const char *message
)
{
    /*
     * Both reviewed messages begin with "TLSF m"; the following byte
     * distinguishes "memory" from "mutex".
     */
    return message[6] == 'e' ? 1U : 2U;
}

static void open_cfw_test_runtime_heap_coordinator_diagnostic(
    const char *message
)
{
    unsigned int kind =
        open_cfw_test_runtime_heap_coordinator_message_kind(message);

    open_cfw_test_runtime_heap_coordinator_diagnostic_message = message;
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_DIAGNOSTIC,
        kind,
        0U,
        0U,
        0U
    );
}

static void open_cfw_test_runtime_heap_coordinator_fatal(void)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_FATAL,
        0U,
        0U,
        0U,
        0U
    );
    if (open_cfw_test_runtime_heap_coordinator_fatal_armed != 0U) {
        longjmp(open_cfw_test_runtime_heap_coordinator_fatal_jump, 1);
    }
    __builtin_trap();
}

static unsigned int
open_cfw_test_runtime_heap_coordinator_tlsf_create_with_pool(
    unsigned int arena,
    unsigned int arena_size
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_TLSF_CREATE,
        arena,
        arena_size,
        0U,
        0U
    );
    return open_cfw_test_runtime_heap_coordinator_tlsf_create_result;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_mutex_create(
    unsigned int mutex_type
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_MUTEX_CREATE,
        mutex_type,
        0U,
        0U,
        0U
    );
    return open_cfw_test_runtime_heap_coordinator_mutex_create_result;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_mutex_acquire(
    unsigned int mutex,
    unsigned int timeout
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_MUTEX_ACQUIRE,
        mutex,
        timeout,
        0U,
        0U
    );
    return open_cfw_test_runtime_heap_coordinator_mutex_acquire_result;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_mutex_release(
    unsigned int mutex,
    unsigned int argument1,
    unsigned int argument2,
    unsigned int argument3
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_MUTEX_RELEASE,
        mutex,
        argument1,
        argument2,
        argument3
    );
    return 0xA5A5A5A5U;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_tlsf_allocate(
    unsigned int allocator,
    unsigned int size
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_TLSF_ALLOCATE,
        allocator,
        size,
        0U,
        0U
    );
    return open_cfw_test_runtime_heap_coordinator_allocate_result;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_tlsf_memalign(
    unsigned int allocator,
    unsigned int alignment,
    unsigned int size
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_TLSF_MEMALIGN,
        allocator,
        alignment,
        size,
        0U
    );
    return open_cfw_test_runtime_heap_coordinator_memalign_result;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_tlsf_block_size(
    unsigned int allocation
)
{
    unsigned int index =
        open_cfw_test_runtime_heap_coordinator_block_size_index;
    unsigned int result = 0U;

    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_TLSF_BLOCK_SIZE,
        allocation,
        0U,
        0U,
        0U
    );
    if (
        index
        < open_cfw_test_runtime_heap_coordinator_block_size_count
    ) {
        result =
            open_cfw_test_runtime_heap_coordinator_block_sizes[index];
    }
    open_cfw_test_runtime_heap_coordinator_block_size_index = index + 1U;
    return result;
}

static unsigned int open_cfw_test_runtime_heap_coordinator_tlsf_reallocate(
    unsigned int allocator,
    unsigned int allocation,
    unsigned int size
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_TLSF_REALLOCATE,
        allocator,
        allocation,
        size,
        0U
    );
    return open_cfw_test_runtime_heap_coordinator_reallocate_result;
}

static void open_cfw_test_runtime_heap_coordinator_tlsf_free(
    unsigned int allocator,
    unsigned int allocation
)
{
    open_cfw_test_runtime_heap_coordinator_log_event(
        OPEN_CFW_TEST_HEAP_EVENT_TLSF_FREE,
        allocator,
        allocation,
        0U,
        0U
    );
}

#define OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC(message) \
    open_cfw_test_runtime_heap_coordinator_diagnostic((message))
#define OPEN_CFW_RUNTIME_HEAP_FATAL() \
    open_cfw_test_runtime_heap_coordinator_fatal()
#define OPEN_CFW_RUNTIME_HEAP_MUTEX_CREATE(mutex_type) \
    open_cfw_test_runtime_heap_coordinator_mutex_create((mutex_type))
#define OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(mutex, timeout) \
    open_cfw_test_runtime_heap_coordinator_mutex_acquire( \
        (mutex), \
        (timeout) \
    )
#define OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE( \
    mutex, \
    argument1, \
    argument2, \
    argument3 \
) \
    open_cfw_test_runtime_heap_coordinator_mutex_release( \
        (mutex), \
        (argument1), \
        (argument2), \
        (argument3) \
    )
#define OPEN_CFW_RUNTIME_HEAP_TLSF_CREATE_WITH_POOL(arena, arena_size) \
    open_cfw_test_runtime_heap_coordinator_tlsf_create_with_pool( \
        (arena), \
        (arena_size) \
    )
#define OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(allocation) \
    open_cfw_test_runtime_heap_coordinator_tlsf_block_size((allocation))
#define OPEN_CFW_RUNTIME_HEAP_TLSF_ALLOCATE(allocator, size) \
    open_cfw_test_runtime_heap_coordinator_tlsf_allocate( \
        (allocator), \
        (size) \
    )
#define OPEN_CFW_RUNTIME_HEAP_TLSF_MEMALIGN(allocator, alignment, size) \
    open_cfw_test_runtime_heap_coordinator_tlsf_memalign( \
        (allocator), \
        (alignment), \
        (size) \
    )
#define OPEN_CFW_RUNTIME_HEAP_TLSF_REALLOCATE( \
    allocator, \
    allocation, \
    size \
) \
    open_cfw_test_runtime_heap_coordinator_tlsf_reallocate( \
        (allocator), \
        (allocation), \
        (size) \
    )
#define OPEN_CFW_RUNTIME_HEAP_TLSF_FREE(allocator, allocation) \
    open_cfw_test_runtime_heap_coordinator_tlsf_free( \
        (allocator), \
        (allocation) \
    )

#include "../../components/apollo_main/core_overlay/runtime_heap_coordinator.c"

void open_cfw_test_runtime_heap_coordinator_reset(
    unsigned int tlsf_create_result,
    unsigned int mutex_create_result,
    unsigned int mutex_acquire_result,
    unsigned int allocate_result,
    unsigned int memalign_result,
    unsigned int reallocate_result
)
{
    unsigned int index;

    open_cfw_test_runtime_heap_coordinator_event_count = 0U;
    for (index = 0U; index < OPEN_CFW_TEST_HEAP_EVENT_CAPACITY; index++) {
        open_cfw_test_runtime_heap_coordinator_event_codes[index] = 0U;
        open_cfw_test_runtime_heap_coordinator_event_argument0[index] = 0U;
        open_cfw_test_runtime_heap_coordinator_event_argument1[index] = 0U;
        open_cfw_test_runtime_heap_coordinator_event_argument2[index] = 0U;
        open_cfw_test_runtime_heap_coordinator_event_argument3[index] = 0U;
    }
    open_cfw_test_runtime_heap_coordinator_tlsf_create_result =
        tlsf_create_result;
    open_cfw_test_runtime_heap_coordinator_mutex_create_result =
        mutex_create_result;
    open_cfw_test_runtime_heap_coordinator_mutex_acquire_result =
        mutex_acquire_result;
    open_cfw_test_runtime_heap_coordinator_allocate_result =
        allocate_result;
    open_cfw_test_runtime_heap_coordinator_memalign_result =
        memalign_result;
    open_cfw_test_runtime_heap_coordinator_reallocate_result =
        reallocate_result;
    open_cfw_test_runtime_heap_coordinator_block_size_count = 0U;
    open_cfw_test_runtime_heap_coordinator_block_size_index = 0U;
    for (
        index = 0U;
        index < OPEN_CFW_TEST_HEAP_BLOCK_SIZE_CAPACITY;
        index++
    ) {
        open_cfw_test_runtime_heap_coordinator_block_sizes[index] = 0U;
    }
    open_cfw_test_runtime_heap_coordinator_diagnostic_message =
        (const char *)0;
    open_cfw_test_runtime_heap_coordinator_fatal_armed = 0U;
}

void open_cfw_test_runtime_heap_coordinator_set_block_sizes(
    const unsigned int *sizes,
    unsigned int count
)
{
    unsigned int index;

    if (count > OPEN_CFW_TEST_HEAP_BLOCK_SIZE_CAPACITY) {
        count = OPEN_CFW_TEST_HEAP_BLOCK_SIZE_CAPACITY;
    }
    for (index = 0U; index < count; index++) {
        open_cfw_test_runtime_heap_coordinator_block_sizes[index] =
            sizes[index];
    }
    open_cfw_test_runtime_heap_coordinator_block_size_count = count;
    open_cfw_test_runtime_heap_coordinator_block_size_index = 0U;
}

int open_cfw_test_runtime_heap_coordinator_initialize(
    struct open_cfw_runtime_heap_descriptor *descriptor,
    unsigned int arena,
    unsigned int arena_size
)
{
    int fatal_result;

    open_cfw_test_runtime_heap_coordinator_fatal_armed = 1U;
    fatal_result =
        setjmp(open_cfw_test_runtime_heap_coordinator_fatal_jump);
    if (fatal_result == 0) {
        open_cfw_runtime_heap_generic_initialize(
            descriptor,
            arena,
            arena_size
        );
        open_cfw_test_runtime_heap_coordinator_fatal_armed = 0U;
        return 0;
    }
    open_cfw_test_runtime_heap_coordinator_fatal_armed = 0U;
    return 1;
}
