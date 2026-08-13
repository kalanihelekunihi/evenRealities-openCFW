/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native allocation, queue, stream, wakeup, and diagnostic fixture for the
 * BLE message-transmit enqueue core.
 */

#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_STREAM_READY 1U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_STREAM_RESET 2U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_ALLOCATE 3U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_COUNT 4U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_CAPACITY 5U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_PUT 6U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_FLAGS 7U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_FREE 8U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_LEVEL 9U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_LOG 10U
#define OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_TRACE 11U

struct open_cfw_test_ble_msgtx_enqueue_state_type {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
};

union open_cfw_test_ble_msgtx_enqueue_allocation_type {
    unsigned int alignment;
    unsigned char bytes[65552];
};

struct open_cfw_test_ble_msgtx_enqueue_state_type
    open_cfw_test_ble_msgtx_enqueue_state;
union open_cfw_test_ble_msgtx_enqueue_allocation_type
    open_cfw_test_ble_msgtx_enqueue_allocation;
unsigned int open_cfw_test_ble_msgtx_enqueue_events[128];
unsigned int open_cfw_test_ble_msgtx_enqueue_event_count;
unsigned int open_cfw_test_ble_msgtx_enqueue_allocation_available;
unsigned int open_cfw_test_ble_msgtx_enqueue_allocation_size;
unsigned int open_cfw_test_ble_msgtx_enqueue_allocation_calls;
unsigned int open_cfw_test_ble_msgtx_enqueue_stream_ready_result;
unsigned int open_cfw_test_ble_msgtx_enqueue_stream_ready_calls;
unsigned int open_cfw_test_ble_msgtx_enqueue_stream_reset_calls;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_count_result;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_count_calls;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_capacity_result;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_capacity_calls;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_status;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_calls;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_enqueue_queue_handle;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_enqueue_queued_message;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_priority;
unsigned int open_cfw_test_ble_msgtx_enqueue_queue_timeout;
unsigned int open_cfw_test_ble_msgtx_enqueue_flags_calls;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_enqueue_flags_thread;
unsigned int open_cfw_test_ble_msgtx_enqueue_flags_value;
unsigned int open_cfw_test_ble_msgtx_enqueue_free_calls;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_enqueue_freed_pointer;
unsigned int open_cfw_test_ble_msgtx_enqueue_level_values[32];
unsigned int open_cfw_test_ble_msgtx_enqueue_level_count;
unsigned int open_cfw_test_ble_msgtx_enqueue_level_index;
unsigned int open_cfw_test_ble_msgtx_enqueue_log_arguments[6];
unsigned int open_cfw_test_ble_msgtx_enqueue_log_extra_arguments[2];
unsigned int open_cfw_test_ble_msgtx_enqueue_trace_arguments[3];
unsigned int open_cfw_test_ble_msgtx_enqueue_trace_extra_arguments[2];

static void open_cfw_test_ble_msgtx_enqueue_record(unsigned int event)
{
    open_cfw_test_ble_msgtx_enqueue_events[
        open_cfw_test_ble_msgtx_enqueue_event_count++
    ] = event;
}

void open_cfw_test_ble_msgtx_enqueue_reset(void)
{
    unsigned int index;

    open_cfw_test_ble_msgtx_enqueue_state.reserved_0 = 0x11111111U;
    open_cfw_test_ble_msgtx_enqueue_state.reserved_4 = 0x22222222U;
    open_cfw_test_ble_msgtx_enqueue_state.thread = 0x33333333U;
    open_cfw_test_ble_msgtx_enqueue_state.queue = 0x44444444U;
    open_cfw_test_ble_msgtx_enqueue_event_count = 0U;
    open_cfw_test_ble_msgtx_enqueue_allocation_available = 1U;
    open_cfw_test_ble_msgtx_enqueue_allocation_size = 0U;
    open_cfw_test_ble_msgtx_enqueue_allocation_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_stream_ready_result = 1U;
    open_cfw_test_ble_msgtx_enqueue_stream_ready_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_stream_reset_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_count_result = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_count_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_capacity_result = 150U;
    open_cfw_test_ble_msgtx_enqueue_queue_capacity_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_status = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_handle = 0U;
    open_cfw_test_ble_msgtx_enqueue_queued_message = 0U;
    open_cfw_test_ble_msgtx_enqueue_queue_priority = 0xFFU;
    open_cfw_test_ble_msgtx_enqueue_queue_timeout = 0U;
    open_cfw_test_ble_msgtx_enqueue_flags_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_flags_thread = 0U;
    open_cfw_test_ble_msgtx_enqueue_flags_value = 0U;
    open_cfw_test_ble_msgtx_enqueue_free_calls = 0U;
    open_cfw_test_ble_msgtx_enqueue_freed_pointer = 0U;
    open_cfw_test_ble_msgtx_enqueue_level_count = 0U;
    open_cfw_test_ble_msgtx_enqueue_level_index = 0U;

    for (index = 0U; index < 65552U; ++index) {
        open_cfw_test_ble_msgtx_enqueue_allocation.bytes[index] = 0xA5U;
    }
    for (index = 0U; index < 128U; ++index) {
        open_cfw_test_ble_msgtx_enqueue_events[index] = 0U;
    }
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_ble_msgtx_enqueue_level_values[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_ble_msgtx_enqueue_log_arguments[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_ble_msgtx_enqueue_trace_arguments[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_ble_msgtx_enqueue_log_extra_arguments[index] = 0U;
        open_cfw_test_ble_msgtx_enqueue_trace_extra_arguments[index] = 0U;
    }
}

void *open_cfw_test_ble_msgtx_enqueue_allocate(unsigned int size)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_ALLOCATE
    );
    open_cfw_test_ble_msgtx_enqueue_allocation_size = size;
    ++open_cfw_test_ble_msgtx_enqueue_allocation_calls;
    if (open_cfw_test_ble_msgtx_enqueue_allocation_available == 0U) {
        return (void *)0;
    }
    return open_cfw_test_ble_msgtx_enqueue_allocation.bytes;
}

void open_cfw_test_ble_msgtx_enqueue_free(void *pointer)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_FREE
    );
    ++open_cfw_test_ble_msgtx_enqueue_free_calls;
    open_cfw_test_ble_msgtx_enqueue_freed_pointer =
        (__UINTPTR_TYPE__)pointer;
}

unsigned int open_cfw_test_ble_msgtx_enqueue_stream_ready(void)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_STREAM_READY
    );
    ++open_cfw_test_ble_msgtx_enqueue_stream_ready_calls;
    return open_cfw_test_ble_msgtx_enqueue_stream_ready_result;
}

void open_cfw_test_ble_msgtx_enqueue_stream_reset(void)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_STREAM_RESET
    );
    ++open_cfw_test_ble_msgtx_enqueue_stream_reset_calls;
}

unsigned int open_cfw_test_ble_msgtx_enqueue_queue_count(void *queue)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_COUNT
    );
    open_cfw_test_ble_msgtx_enqueue_queue_handle =
        (__UINTPTR_TYPE__)queue;
    ++open_cfw_test_ble_msgtx_enqueue_queue_count_calls;
    return open_cfw_test_ble_msgtx_enqueue_queue_count_result;
}

unsigned int open_cfw_test_ble_msgtx_enqueue_queue_capacity(void *queue)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_CAPACITY
    );
    open_cfw_test_ble_msgtx_enqueue_queue_handle =
        (__UINTPTR_TYPE__)queue;
    ++open_cfw_test_ble_msgtx_enqueue_queue_capacity_calls;
    return open_cfw_test_ble_msgtx_enqueue_queue_capacity_result;
}

unsigned int open_cfw_test_ble_msgtx_enqueue_queue_put(
    void *queue,
    const void *message,
    unsigned char priority,
    unsigned int timeout
)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_PUT
    );
    open_cfw_test_ble_msgtx_enqueue_queue_handle =
        (__UINTPTR_TYPE__)queue;
    open_cfw_test_ble_msgtx_enqueue_queued_message =
        (__UINTPTR_TYPE__)(*(void *const *)message);
    open_cfw_test_ble_msgtx_enqueue_queue_priority = priority;
    open_cfw_test_ble_msgtx_enqueue_queue_timeout = timeout;
    ++open_cfw_test_ble_msgtx_enqueue_queue_calls;
    return open_cfw_test_ble_msgtx_enqueue_queue_status;
}

unsigned int open_cfw_test_ble_msgtx_enqueue_thread_flags(
    void *thread,
    unsigned int flags
)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_FLAGS
    );
    open_cfw_test_ble_msgtx_enqueue_flags_thread =
        (__UINTPTR_TYPE__)thread;
    open_cfw_test_ble_msgtx_enqueue_flags_value = flags;
    ++open_cfw_test_ble_msgtx_enqueue_flags_calls;
    return 0x87654321U;
}

unsigned int open_cfw_test_ble_msgtx_enqueue_log_level(void)
{
    unsigned int index = open_cfw_test_ble_msgtx_enqueue_level_index++;
    unsigned int value = 0U;

    if (index < open_cfw_test_ble_msgtx_enqueue_level_count) {
        value = open_cfw_test_ble_msgtx_enqueue_level_values[index];
    }
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_LEVEL
    );
    return value;
}

void open_cfw_test_ble_msgtx_enqueue_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message
)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_LOG
    );
    open_cfw_test_ble_msgtx_enqueue_log_arguments[0] = level;
    open_cfw_test_ble_msgtx_enqueue_log_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)module;
    open_cfw_test_ble_msgtx_enqueue_log_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)file;
    open_cfw_test_ble_msgtx_enqueue_log_arguments[3] =
        (unsigned int)(__UINTPTR_TYPE__)function;
    open_cfw_test_ble_msgtx_enqueue_log_arguments[4] = line;
    open_cfw_test_ble_msgtx_enqueue_log_arguments[5] =
        (unsigned int)(__UINTPTR_TYPE__)message;
}

void open_cfw_test_ble_msgtx_enqueue_log_one(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int argument
)
{
    open_cfw_test_ble_msgtx_enqueue_log(
        level,
        module,
        file,
        function,
        line,
        message
    );
    open_cfw_test_ble_msgtx_enqueue_log_extra_arguments[0] = argument;
}

void open_cfw_test_ble_msgtx_enqueue_log_two(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int argument_1,
    unsigned int argument_2
)
{
    open_cfw_test_ble_msgtx_enqueue_log(
        level,
        module,
        file,
        function,
        line,
        message
    );
    open_cfw_test_ble_msgtx_enqueue_log_extra_arguments[0] = argument_1;
    open_cfw_test_ble_msgtx_enqueue_log_extra_arguments[1] = argument_2;
}

void open_cfw_test_ble_msgtx_enqueue_trace(
    unsigned int level,
    const void *format,
    const void *argument
)
{
    open_cfw_test_ble_msgtx_enqueue_record(
        OPEN_CFW_TEST_BLE_MSGTX_ENQUEUE_TRACE
    );
    open_cfw_test_ble_msgtx_enqueue_trace_arguments[0] = level;
    open_cfw_test_ble_msgtx_enqueue_trace_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)format;
    open_cfw_test_ble_msgtx_enqueue_trace_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)argument;
}

void open_cfw_test_ble_msgtx_enqueue_trace_one(
    unsigned int level,
    const void *format,
    const void *argument,
    unsigned int value
)
{
    open_cfw_test_ble_msgtx_enqueue_trace(level, format, argument);
    open_cfw_test_ble_msgtx_enqueue_trace_extra_arguments[0] = value;
}

void open_cfw_test_ble_msgtx_enqueue_trace_two(
    unsigned int level,
    const void *format,
    const void *argument,
    unsigned int value_1,
    unsigned int value_2
)
{
    open_cfw_test_ble_msgtx_enqueue_trace(level, format, argument);
    open_cfw_test_ble_msgtx_enqueue_trace_extra_arguments[0] = value_1;
    open_cfw_test_ble_msgtx_enqueue_trace_extra_arguments[1] = value_2;
}

#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STATE \
    ((volatile open_cfw_ble_msgtx_enqueue_state *) \
        &open_cfw_test_ble_msgtx_enqueue_state)
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_ALLOCATE(size) \
    open_cfw_test_ble_msgtx_enqueue_allocate((size))
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_FREE(pointer) \
    open_cfw_test_ble_msgtx_enqueue_free((pointer))
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_READY() \
    open_cfw_test_ble_msgtx_enqueue_stream_ready()
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_RESET() \
    open_cfw_test_ble_msgtx_enqueue_stream_reset()
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_COUNT(queue) \
    open_cfw_test_ble_msgtx_enqueue_queue_count((queue))
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_CAPACITY(queue) \
    open_cfw_test_ble_msgtx_enqueue_queue_capacity((queue))
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_PUT( \
    queue, message, priority, timeout \
) \
    open_cfw_test_ble_msgtx_enqueue_queue_put( \
        (queue), (message), (priority), (timeout) \
    )
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_THREAD_FLAGS_SET(thread, flags) \
    open_cfw_test_ble_msgtx_enqueue_thread_flags((thread), (flags))
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_LEVEL() \
    open_cfw_test_ble_msgtx_enqueue_log_level()
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG( \
    level, module, file, function, line, message \
) \
    open_cfw_test_ble_msgtx_enqueue_log( \
        (level), (module), (file), (function), (line), (message) \
    )
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_ONE( \
    level, module, file, function, line, message, argument \
) \
    open_cfw_test_ble_msgtx_enqueue_log_one( \
        (level), (module), (file), (function), (line), (message), \
        (argument) \
    )
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_TWO( \
    level, module, file, function, line, message, argument_1, argument_2 \
) \
    open_cfw_test_ble_msgtx_enqueue_log_two( \
        (level), (module), (file), (function), (line), (message), \
        (argument_1), (argument_2) \
    )
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE(level, format, argument) \
    open_cfw_test_ble_msgtx_enqueue_trace( \
        (level), (format), (argument) \
    )
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_ONE( \
    level, format, argument, value \
) \
    open_cfw_test_ble_msgtx_enqueue_trace_one( \
        (level), (format), (argument), (value) \
    )
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_TWO( \
    level, format, argument, value_1, value_2 \
) \
    open_cfw_test_ble_msgtx_enqueue_trace_two( \
        (level), (format), (argument), (value_1), (value_2) \
    )

#include "../../components/apollo_main/core_overlay/ble_msgtx_enqueue.c"
