/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded BLE message-transmit allocation and enqueue core matched to stock
 * 0x0047564E...0x00475A37.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgtx_enqueue_uintptr;

#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STATE_ADDRESS 0x20004020U
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_THREAD_FLAG 0x00400000U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgtx_enqueue_state;

typedef struct {
    unsigned int command;
    unsigned int length;
    unsigned char enabled;
    unsigned char argument_1;
    unsigned char argument_2;
    unsigned char data[];
} open_cfw_ble_msgtx_enqueue_message;

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_STATE
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STATE \
    ((volatile open_cfw_ble_msgtx_enqueue_state *) \
        (open_cfw_ble_msgtx_enqueue_uintptr) \
            OPEN_CFW_BLE_MSGTX_ENQUEUE_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_ALLOCATE
void *open_cfw_file_heap_allocate(unsigned int size);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_ALLOCATE(size) \
    open_cfw_file_heap_allocate((size))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_FREE
void open_cfw_file_heap_free(void *pointer);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_FREE(pointer) \
    open_cfw_file_heap_free((pointer))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_PUT
typedef unsigned int (*open_cfw_ble_msgtx_enqueue_queue_put_function)(
    void *,
    const void *,
    unsigned char,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_PUT( \
    queue, message, priority, timeout \
) \
    (((open_cfw_ble_msgtx_enqueue_queue_put_function)0x00449ABFU)( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_COUNT
typedef unsigned int (*open_cfw_ble_msgtx_enqueue_queue_count_function)(
    void *
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_COUNT(queue) \
    (((open_cfw_ble_msgtx_enqueue_queue_count_function)0x00449BC9U)( \
        (queue) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_CAPACITY
typedef unsigned int (*open_cfw_ble_msgtx_enqueue_queue_capacity_function)(
    void *
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_CAPACITY(queue) \
    (((open_cfw_ble_msgtx_enqueue_queue_capacity_function)0x00449BBDU)( \
        (queue) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_THREAD_FLAGS_SET
typedef unsigned int (*open_cfw_ble_msgtx_enqueue_thread_flags_function)(
    void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_THREAD_FLAGS_SET(thread, flags) \
    (((open_cfw_ble_msgtx_enqueue_thread_flags_function)0x00449239U)( \
        (thread), \
        (flags) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_READY
typedef unsigned int (*open_cfw_ble_msgtx_enqueue_stream_ready_function)(
    void
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_READY() \
    (((open_cfw_ble_msgtx_enqueue_stream_ready_function)0x004780F9U)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_RESET
typedef void (*open_cfw_ble_msgtx_enqueue_stream_reset_function)(void);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_RESET() \
    (((open_cfw_ble_msgtx_enqueue_stream_reset_function)0x00478161U)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_LEVEL
typedef unsigned int (*open_cfw_ble_msgtx_enqueue_log_level_function)(void);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_LEVEL() \
    (((open_cfw_ble_msgtx_enqueue_log_level_function)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG
typedef void (*open_cfw_ble_msgtx_enqueue_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG( \
    level, module, file, function, line, message \
) \
    (((open_cfw_ble_msgtx_enqueue_log_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_ONE
typedef void (*open_cfw_ble_msgtx_enqueue_log_one_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_ONE( \
    level, module, file, function, line, message, argument \
) \
    (((open_cfw_ble_msgtx_enqueue_log_one_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message), \
        (argument) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_TWO
typedef void (*open_cfw_ble_msgtx_enqueue_log_two_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_TWO( \
    level, module, file, function, line, message, argument_1, argument_2 \
) \
    (((open_cfw_ble_msgtx_enqueue_log_two_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message), \
        (argument_1), \
        (argument_2) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE
typedef void (*open_cfw_ble_msgtx_enqueue_trace_function)(
    unsigned int,
    const void *,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE(level, format, argument) \
    (((open_cfw_ble_msgtx_enqueue_trace_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_ONE
typedef void (*open_cfw_ble_msgtx_enqueue_trace_one_function)(
    unsigned int,
    const void *,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_ONE( \
    level, format, argument, value \
) \
    (((open_cfw_ble_msgtx_enqueue_trace_one_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_TWO
typedef void (*open_cfw_ble_msgtx_enqueue_trace_two_function)(
    unsigned int,
    const void *,
    const void *,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_TWO( \
    level, format, argument, value_1, value_2 \
) \
    (((open_cfw_ble_msgtx_enqueue_trace_two_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument), \
        (value_1), \
        (value_2) \
    ))
#endif

static __attribute__((always_inline)) inline void
open_cfw_ble_msgtx_enqueue_diagnostic(
    unsigned int structured_level,
    unsigned int line,
    const void *message,
    unsigned int trace_level,
    const void *trace_format,
    unsigned int argument_count,
    unsigned int argument_1,
    unsigned int argument_2
)
{
    unsigned int level;
    const void *module =
        (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x0078C644U;
    const void *file =
        (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x006FE2C4U;
    const void *function =
        (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x007841F8U;

    if ((OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG(
                structured_level,
                module,
                file,
                function,
                line,
                message
            );
        } else if (argument_count == 1U) {
            OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_ONE(
                structured_level,
                module,
                file,
                function,
                line,
                message,
                argument_1
            );
        } else {
            OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_TWO(
                structured_level,
                module,
                file,
                function,
                line,
                message,
                argument_1,
                argument_2
            );
        }
    }

    level = OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_LEVEL();
    if (
        (level & 1U) != 0U ||
        (OPEN_CFW_BLE_MSGTX_ENQUEUE_LOG_LEVEL() & 4U) != 0U
    ) {
        if (argument_count == 0U) {
            OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE(
                trace_level,
                trace_format,
                trace_format
            );
        } else if (argument_count == 1U) {
            OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_ONE(
                trace_level,
                trace_format,
                trace_format,
                argument_1
            );
        } else {
            OPEN_CFW_BLE_MSGTX_ENQUEUE_TRACE_TWO(
                trace_level,
                trace_format,
                trace_format,
                argument_1,
                argument_2
            );
        }
    }
}

static __attribute__((always_inline)) inline void
open_cfw_ble_msgtx_enqueue_copy(
    unsigned char *destination,
    const unsigned char *source,
    unsigned int length
)
{
    unsigned int index;

    for (index = 0U; index < length; ++index) {
        destination[index] = source[index];
    }
}

__attribute__((used, noinline))
int open_cfw_ble_msgtx_enqueue(
    unsigned char transport,
    unsigned char enabled,
    unsigned char argument_1,
    unsigned char argument_2,
    const void *payload,
    unsigned short length
)
{
    volatile open_cfw_ble_msgtx_enqueue_state *state =
        OPEN_CFW_BLE_MSGTX_ENQUEUE_STATE;
    open_cfw_ble_msgtx_enqueue_message *message;
    unsigned int allocation_size;
    unsigned int queue_count;
    unsigned int queue_capacity;
    unsigned int queue_status;

    if (payload == (const void *)0) {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            1U,
            0x131U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00766890U,
            0x04000000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00745300U,
            0U,
            0U,
            0U
        );
        return -1;
    }

    if (state->queue == 0U) {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            1U,
            0x136U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x007668B0U,
            0x04000000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x0074532CU,
            0U,
            0U,
            0U
        );
        return -1;
    }

    if (
        transport == 1U &&
        OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_READY() == 0U
    ) {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            2U,
            0x13BU,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00719FA8U,
            0x08000000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x0070720CU,
            0U,
            0U,
            0U
        );
        OPEN_CFW_BLE_MSGTX_ENQUEUE_STREAM_RESET();
    }

    allocation_size = ((unsigned int)length + 14U) & ~3U;
    message = (open_cfw_ble_msgtx_enqueue_message *)
        OPEN_CFW_BLE_MSGTX_ENQUEUE_ALLOCATE(allocation_size);
    if (message == (open_cfw_ble_msgtx_enqueue_message *)0) {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            1U,
            0x144U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x007668D0U,
            0x04000000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00745358U,
            0U,
            0U,
            0U
        );
        return -1;
    }

    if (transport == 0U || transport == 2U || transport == 3U) {
        message->command = transport == 0U ? 1U :
            (transport == 2U ? 4U : 8U);
        message->length = (unsigned int)length + 3U;
        message->enabled = enabled;
        message->argument_1 = argument_1;
        message->argument_2 = argument_2;
        open_cfw_ble_msgtx_enqueue_copy(
            message->data,
            (const unsigned char *)payload,
            length
        );
    } else if (transport == 1U) {
        message->command = 2U;
        message->length = length;
        open_cfw_ble_msgtx_enqueue_copy(
            &message->enabled,
            (const unsigned char *)payload,
            length
        );
    } else {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            1U,
            0x173U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x0077CB8CU,
            0x04400000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x0075BA30U,
            1U,
            transport,
            0U
        );
    }

    queue_count = OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_COUNT(
        (void *)(open_cfw_ble_msgtx_enqueue_uintptr)state->queue
    );
    queue_capacity = OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_CAPACITY(
        (void *)(open_cfw_ble_msgtx_enqueue_uintptr)state->queue
    );

    if (transport != 1U) {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            4U,
            0x17BU,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x0074FBF4U,
            0x10800000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00739C74U,
            2U,
            queue_count,
            queue_capacity
        );
    }

    if (transport == 1U && queue_count >= (queue_capacity >> 1U)) {
        open_cfw_ble_msgtx_enqueue_diagnostic(
            2U,
            0x181U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x006F0678U,
            0x08800000U,
            (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x006E1C74U,
            2U,
            queue_count,
            queue_capacity
        );
        OPEN_CFW_BLE_MSGTX_ENQUEUE_FREE(message);
        return 0;
    }

    queue_status = OPEN_CFW_BLE_MSGTX_ENQUEUE_QUEUE_PUT(
        (void *)(open_cfw_ble_msgtx_enqueue_uintptr)state->queue,
        &message,
        0U,
        500U
    );
    if (queue_status == 0U) {
        (void)OPEN_CFW_BLE_MSGTX_ENQUEUE_THREAD_FLAGS_SET(
            (void *)(open_cfw_ble_msgtx_enqueue_uintptr)state->thread,
            OPEN_CFW_BLE_MSGTX_ENQUEUE_THREAD_FLAG
        );
        return 0;
    }

    open_cfw_ble_msgtx_enqueue_diagnostic(
        1U,
        0x189U,
        (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00745384U,
        0x04400000U,
        (const void *)(open_cfw_ble_msgtx_enqueue_uintptr)0x00724880U,
        1U,
        queue_status,
        0U
    );
    OPEN_CFW_BLE_MSGTX_ENQUEUE_FREE(message);
    return -1;
}
