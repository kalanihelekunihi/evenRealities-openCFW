/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE message-transmit queue and thread-flag dispatch matched to
 * stock 0x0047538C...0x00475523.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgtx_dispatch_uintptr;

#define OPEN_CFW_BLE_MSGTX_DISPATCH_STATE_ADDRESS 0x20004020U
#define OPEN_CFW_BLE_MSGTX_QUEUE_FLAG 0x00400000U
#define OPEN_CFW_BLE_MSGTX_WAIT_FLAG 0x00800000U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgtx_dispatch_state;

typedef struct {
    unsigned int command;
    unsigned int length;
    unsigned char enabled;
    unsigned char argument_1;
    unsigned char argument_2;
    unsigned char data[];
} open_cfw_ble_msgtx_message;

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_STATE
#define OPEN_CFW_BLE_MSGTX_DISPATCH_STATE \
    ((volatile open_cfw_ble_msgtx_dispatch_state *) \
        (open_cfw_ble_msgtx_dispatch_uintptr) \
            OPEN_CFW_BLE_MSGTX_DISPATCH_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_MSGTX_QUEUE_GET
typedef unsigned int (*open_cfw_ble_msgtx_queue_get_function)(
    void *,
    void *,
    unsigned char *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_QUEUE_GET(queue, message, priority, timeout) \
    (((open_cfw_ble_msgtx_queue_get_function)0x00449B3DU)( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_QUEUE_COUNT
typedef unsigned int (*open_cfw_ble_msgtx_queue_count_function)(void *);
#define OPEN_CFW_BLE_MSGTX_QUEUE_COUNT(queue) \
    (((open_cfw_ble_msgtx_queue_count_function)0x00449BC9U)((queue)))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_MESSAGE_FREE
void open_cfw_file_heap_free(void *pointer);
#define OPEN_CFW_BLE_MSGTX_MESSAGE_FREE(message) \
    open_cfw_file_heap_free((message))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_COMMAND_ONE
typedef void (*open_cfw_ble_msgtx_command_one_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_COMMAND_ONE( \
    channel, enabled, argument_1, argument_2, data, length \
) \
    (((open_cfw_ble_msgtx_command_one_function)0x004B9641U)( \
        (channel), \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (data), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_COMMAND_TWO_READY
typedef unsigned int (*open_cfw_ble_msgtx_command_two_ready_function)(
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_COMMAND_TWO_READY(value) \
    (((open_cfw_ble_msgtx_command_two_ready_function)0x004D0C2DU)( \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_COMMAND_TWO
typedef void (*open_cfw_ble_msgtx_command_two_function)(
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_COMMAND_TWO(data, length) \
    (((open_cfw_ble_msgtx_command_two_function)0x004BE2F7U)( \
        (data), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_COMMAND_FOUR
typedef void (*open_cfw_ble_msgtx_command_data_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_COMMAND_FOUR( \
    enabled, argument_1, argument_2, data, length \
) \
    (((open_cfw_ble_msgtx_command_data_function)0x004D12DFU)( \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (data), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_COMMAND_EIGHT
#define OPEN_CFW_BLE_MSGTX_COMMAND_EIGHT( \
    enabled, argument_1, argument_2, data, length \
) \
    (((open_cfw_ble_msgtx_command_data_function)0x0048DE41U)( \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (data), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL
typedef unsigned int (*open_cfw_ble_msgtx_dispatch_log_level_function)(void);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() \
    (((open_cfw_ble_msgtx_dispatch_log_level_function)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_LOG
typedef void (*open_cfw_ble_msgtx_dispatch_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG( \
    level, module, file, function, line, message \
) \
    (((open_cfw_ble_msgtx_dispatch_log_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_ONE
typedef void (*open_cfw_ble_msgtx_dispatch_log_one_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_ONE( \
    level, module, file, function, line, message, argument \
) \
    (((open_cfw_ble_msgtx_dispatch_log_one_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message), \
        (argument) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_TWO
typedef void (*open_cfw_ble_msgtx_dispatch_log_two_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_TWO( \
    level, module, file, function, line, message, argument_1, argument_2 \
) \
    (((open_cfw_ble_msgtx_dispatch_log_two_function)0x0043D575U)( \
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

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE
typedef void (*open_cfw_ble_msgtx_dispatch_trace_function)(
    unsigned int,
    const void *,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE(level, format, argument) \
    (((open_cfw_ble_msgtx_dispatch_trace_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_ONE
typedef void (*open_cfw_ble_msgtx_dispatch_trace_one_function)(
    unsigned int,
    const void *,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_ONE( \
    level, format, argument, value \
) \
    (((open_cfw_ble_msgtx_dispatch_trace_one_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_TWO
typedef void (*open_cfw_ble_msgtx_dispatch_trace_two_function)(
    unsigned int,
    const void *,
    const void *,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_TWO( \
    level, format, argument, value_1, value_2 \
) \
    (((open_cfw_ble_msgtx_dispatch_trace_two_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument), \
        (value_1), \
        (value_2) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_WAIT_STAGE
typedef void (*open_cfw_ble_msgtx_wait_stage_function)(unsigned int);
#define OPEN_CFW_BLE_MSGTX_WAIT_STAGE(index) \
    (((open_cfw_ble_msgtx_wait_stage_function)0x004C9C3DU)((index)))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_WAIT_BACKEND
typedef void (*open_cfw_ble_msgtx_wait_backend_function)(unsigned int);
#define OPEN_CFW_BLE_MSGTX_WAIT_BACKEND(timeout) \
    (((open_cfw_ble_msgtx_wait_backend_function)0x00449377U)((timeout)))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_WAIT_LOOP_CONTINUE
#define OPEN_CFW_BLE_MSGTX_WAIT_LOOP_CONTINUE() 1
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgtx_queue_drain(void)
{
    volatile open_cfw_ble_msgtx_dispatch_state *state =
        OPEN_CFW_BLE_MSGTX_DISPATCH_STATE;
    open_cfw_ble_msgtx_message *message = (open_cfw_ble_msgtx_message *)0;
    unsigned int status;
    unsigned int enabled;
    unsigned int length;
    unsigned int level;

    for (;;) {
        status = OPEN_CFW_BLE_MSGTX_QUEUE_GET(
            (void *)(open_cfw_ble_msgtx_dispatch_uintptr)state->queue,
            &message,
            (unsigned char *)0,
            0U
        );
        if (status != 0U || message == (open_cfw_ble_msgtx_message *)0) {
            return;
        }

        if (message->command == 1U) {
            enabled = message->enabled != 0U ? 1U : 0U;
            length = (unsigned short)(message->length - 3U);
            OPEN_CFW_BLE_MSGTX_COMMAND_ONE(
                0U,
                enabled,
                message->argument_1,
                message->argument_2,
                message->data,
                length
            );
        } else if (message->command == 2U) {
            if (OPEN_CFW_BLE_MSGTX_COMMAND_TWO_READY(50U) != 0U) {
                OPEN_CFW_BLE_MSGTX_COMMAND_TWO(
                    &message->enabled,
                    (unsigned short)message->length
                );
            } else {
                if ((OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
                    OPEN_CFW_BLE_MSGTX_DISPATCH_LOG(
                        2U,
                        (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                            0x0078C644U,
                        (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                            0x006FE2C4U,
                        (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                            0x007841E4U,
                        0xCEU,
                        (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                            0x00719F6CU
                    );
                }
                level = OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL();
                if (
                    (level & 1U) != 0U ||
                    (OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 4U) != 0U
                ) {
                    OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE(
                        0x08000000U,
                        (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                            0x006FE30CU,
                        (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                            0x006FE30CU
                    );
                }
            }
        } else if (message->command == 4U) {
            enabled = message->enabled != 0U ? 1U : 0U;
            length = (unsigned short)(message->length - 3U);
            OPEN_CFW_BLE_MSGTX_COMMAND_FOUR(
                enabled,
                message->argument_1,
                message->argument_2,
                message->data,
                length
            );
        } else if (message->command == 8U) {
            enabled = message->enabled != 0U ? 1U : 0U;
            length = (unsigned short)(message->length - 3U);
            OPEN_CFW_BLE_MSGTX_COMMAND_EIGHT(
                enabled,
                message->argument_1,
                message->argument_2,
                message->data,
                length
            );
        }

        OPEN_CFW_BLE_MSGTX_MESSAGE_FREE(message);
        message = (open_cfw_ble_msgtx_message *)0;
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_ble_msgtx_queue_clear(void)
{
    volatile open_cfw_ble_msgtx_dispatch_state *state =
        OPEN_CFW_BLE_MSGTX_DISPATCH_STATE;
    open_cfw_ble_msgtx_message *message = (open_cfw_ble_msgtx_message *)0;
    unsigned int freed = 0U;
    unsigned int initial_count;
    unsigned int remaining_count;
    unsigned int level;

    if (state->queue == 0U) {
        if ((OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_MSGTX_DISPATCH_LOG(
                2U,
                (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                    0x0078C644U,
                (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                    0x006FE2C4U,
                (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                    0x00773568U,
                0x10FU,
                (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                    0x007452D4U
            );
        }
        level = OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL();
        if (
            (level & 1U) != 0U ||
            (OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 4U) != 0U
        ) {
            OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE(
                0x08000000U,
                (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                    0x0072F058U,
                (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)
                    0x0072F058U
            );
        }
        return 0U;
    }

    initial_count = OPEN_CFW_BLE_MSGTX_QUEUE_COUNT(
        (void *)(open_cfw_ble_msgtx_dispatch_uintptr)state->queue
    );
    if ((OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_ONE(
            4U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x0078C644U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x006FE2C4U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x00773568U,
            0x114U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x00724848U,
            initial_count
        );
    }
    level = OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL();
    if (
        (level & 1U) != 0U ||
        (OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 4U) != 0U
    ) {
        OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_ONE(
            0x10400000U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x007071C8U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x007071C8U,
            initial_count
        );
    }

    for (;;) {
        if (
            OPEN_CFW_BLE_MSGTX_QUEUE_GET(
                (void *)(open_cfw_ble_msgtx_dispatch_uintptr)state->queue,
                &message,
                (unsigned char *)0,
                0U
            ) != 0U ||
            message == (open_cfw_ble_msgtx_message *)0
        ) {
            break;
        }
        OPEN_CFW_BLE_MSGTX_MESSAGE_FREE(message);
        message = (open_cfw_ble_msgtx_message *)0;
        ++freed;
    }

    remaining_count = OPEN_CFW_BLE_MSGTX_QUEUE_COUNT(
        (void *)(open_cfw_ble_msgtx_dispatch_uintptr)state->queue
    );
    if ((OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_TWO(
            4U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x0078C644U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x006FE2C4U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x00773568U,
            0x123U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x00710424U,
            freed,
            remaining_count
        );
    }
    level = OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL();
    if (
        (level & 1U) != 0U ||
        (OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 4U) != 0U
    ) {
        OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_TWO(
            0x10800000U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x006FE354U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x006FE354U,
            freed,
            remaining_count
        );
    }
    return freed;
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_wait_handler(void)
{
    unsigned int level;

    OPEN_CFW_BLE_MSGTX_WAIT_STAGE(8U);
    if ((OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MSGTX_DISPATCH_LOG(
            4U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x0078C644U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x006FE2C4U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x00789A80U,
            0xFDU,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x0077CB74U
        );
    }
    level = OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL();
    if (
        (level & 1U) != 0U ||
        (OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() & 4U) != 0U
    ) {
        OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE(
            0x10000000U,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x0075BA0CU,
            (const void *)(open_cfw_ble_msgtx_dispatch_uintptr)0x0075BA0CU
        );
    }

    for (;;) {
        OPEN_CFW_BLE_MSGTX_WAIT_BACKEND(0xFFFFFFFFU);
        if (!OPEN_CFW_BLE_MSGTX_WAIT_LOOP_CONTINUE()) {
            return;
        }
    }
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_dispatch_flags(unsigned int flags)
{
    if ((flags & OPEN_CFW_BLE_MSGTX_QUEUE_FLAG) != 0U) {
        open_cfw_ble_msgtx_queue_drain();
    }
    if ((flags & OPEN_CFW_BLE_MSGTX_WAIT_FLAG) != 0U) {
        open_cfw_ble_msgtx_wait_handler();
    }
}
