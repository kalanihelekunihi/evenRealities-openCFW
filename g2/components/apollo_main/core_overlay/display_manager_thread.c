/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 display-driver manager thread at
 * 0x00473C44...0x00473E2D.
 */

typedef int (*open_cfw_display_manager_queue_get_fn)(
    void *queue,
    void *message,
    unsigned int priority,
    unsigned int timeout
);
typedef void (*open_cfw_display_manager_void_fn)(void);
typedef int (*open_cfw_display_manager_gate_fn)(void);
typedef void (*open_cfw_display_manager_words_fn)(
    unsigned int word1,
    unsigned int word2,
    unsigned int word3,
    unsigned int word4,
    unsigned int word5,
    unsigned int word6
);
typedef void (*open_cfw_display_manager_query_fn)(
    unsigned int value,
    unsigned int *first,
    unsigned int *second
);
typedef void (*open_cfw_display_manager_query_result_fn)(
    unsigned int value,
    unsigned int second,
    unsigned int first
);
typedef unsigned int (*open_cfw_display_manager_one_fn)(unsigned int value);
typedef void (*open_cfw_display_manager_byte_fn)(unsigned int value);
typedef unsigned int (*open_cfw_display_manager_log_flags_fn)(void);
typedef void (*open_cfw_display_manager_log_fn)(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_display_manager_backend_log_fn)(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
);

void open_cfw_display_queue_initialize(void);
void open_cfw_display_resource_acquire(void);
void open_cfw_display_resource_release(void);
void open_cfw_display_timer_initialize(void);
void open_cfw_display_timer_start(void);
void open_cfw_display_timer_stop(void);
void open_cfw_lv_display_unlock(void);

#ifndef OPEN_CFW_DISPLAY_MANAGER_QUEUE_HANDLE
#define OPEN_CFW_DISPLAY_MANAGER_QUEUE_HANDLE \
    (*(void * volatile *)(void *)0x20000664U)
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_ACTIVE
#define OPEN_CFW_DISPLAY_MANAGER_ACTIVE \
    (*(volatile unsigned int *)(void *)0x200744ECU)
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_QUEUE_INITIALIZE
#define OPEN_CFW_DISPLAY_MANAGER_QUEUE_INITIALIZE() \
    open_cfw_display_queue_initialize()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_RESOURCE_ACQUIRE
#define OPEN_CFW_DISPLAY_MANAGER_RESOURCE_ACQUIRE() \
    open_cfw_display_resource_acquire()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_INTERFACE_INITIALIZE
#define OPEN_CFW_DISPLAY_MANAGER_INTERFACE_INITIALIZE() \
    (((open_cfw_display_manager_void_fn)0x004C9F33U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_RESOURCE_RELEASE
#define OPEN_CFW_DISPLAY_MANAGER_RESOURCE_RELEASE() \
    open_cfw_display_resource_release()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_TIMER_INITIALIZE
#define OPEN_CFW_DISPLAY_MANAGER_TIMER_INITIALIZE() \
    open_cfw_display_timer_initialize()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_QUEUE_GET
#define OPEN_CFW_DISPLAY_MANAGER_QUEUE_GET( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    (((open_cfw_display_manager_queue_get_fn)0x00449B3DU)( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_ENTER
#define OPEN_CFW_DISPLAY_MANAGER_ENTER() \
    (((open_cfw_display_manager_void_fn)0x0046D817U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_PREPARE
#define OPEN_CFW_DISPLAY_MANAGER_PREPARE() \
    (((open_cfw_display_manager_void_fn)0x0046CA15U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_DISPLAY_UNLOCK
#define OPEN_CFW_DISPLAY_MANAGER_DISPLAY_UNLOCK() \
    open_cfw_lv_display_unlock()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_GATE
#define OPEN_CFW_DISPLAY_MANAGER_GATE() \
    (((open_cfw_display_manager_gate_fn)0x0046B239U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_LEAVE
#define OPEN_CFW_DISPLAY_MANAGER_LEAVE() \
    (((open_cfw_display_manager_void_fn)0x0046D827U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND0
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND0() \
    (((open_cfw_display_manager_void_fn)0x004CA18BU)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND1
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND1() \
    (((open_cfw_display_manager_void_fn)0x004CA011U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_TIMER_START
#define OPEN_CFW_DISPLAY_MANAGER_TIMER_START() open_cfw_display_timer_start()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND2
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND2() \
    (((open_cfw_display_manager_void_fn)0x004C9FB5U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND3
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND3( \
    word1, \
    word2, \
    word3, \
    word4, \
    word5, \
    word6 \
) \
    (((open_cfw_display_manager_words_fn)0x004CA565U)( \
        (word1), \
        (word2), \
        (word3), \
        (word4), \
        (word5), \
        (word6) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_QUERY
#define OPEN_CFW_DISPLAY_MANAGER_QUERY(value, first, second) \
    (((open_cfw_display_manager_query_fn)0x0046C411U)( \
        (value), \
        (first), \
        (second) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_QUERY_RESULT
#define OPEN_CFW_DISPLAY_MANAGER_QUERY_RESULT(value, second, first) \
    (((open_cfw_display_manager_query_result_fn)0x004CA1EFU)( \
        (value), \
        (second), \
        (first) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_TIMER_STOP
#define OPEN_CFW_DISPLAY_MANAGER_TIMER_STOP() open_cfw_display_timer_stop()
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND5
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND5() \
    (((open_cfw_display_manager_void_fn)0x004CA127U)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND6_GATE
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND6_GATE(value) \
    (((open_cfw_display_manager_one_fn)0x004CA5BFU)(value))
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_COMMAND8
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND8(value) \
    (((open_cfw_display_manager_byte_fn)0x004CA60FU)(value))
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS
#define OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS() \
    (((open_cfw_display_manager_log_flags_fn)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_LOG
#define OPEN_CFW_DISPLAY_MANAGER_LOG \
    ((open_cfw_display_manager_log_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_BACKEND_LOG
#define OPEN_CFW_DISPLAY_MANAGER_BACKEND_LOG \
    ((open_cfw_display_manager_backend_log_fn)0x0043CE9FU)
#endif

#ifndef OPEN_CFW_DISPLAY_MANAGER_LOOP_CONTINUES
#define OPEN_CFW_DISPLAY_MANAGER_LOOP_CONTINUES() 1
#endif

#define OPEN_CFW_DISPLAY_MANAGER_TAG ((const void *)0x0077EDC0U)
#define OPEN_CFW_DISPLAY_MANAGER_FILE ((const void *)0x006ECB68U)
#define OPEN_CFW_DISPLAY_MANAGER_FUNCTION ((const void *)0x007769F4U)
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND6_FORMAT ((const void *)0x0075F410U)
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND6_BACKEND ((const void *)0x00728AC8U)
#define OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_FORMAT ((const void *)0x007537D4U)
#define OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_BACKEND ((const void *)0x0071DED8U)

static __attribute__((always_inline)) inline int
open_cfw_display_manager_backend_log_enabled(void)
{
    if ((OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS() & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_display_manager_clear_message(unsigned int message[9])
{
    unsigned int index;

    for (index = 0U; index < 9U; index += 1U) {
        message[index] = 0U;
    }
}

static __attribute__((always_inline)) inline void
open_cfw_display_manager_command3(const unsigned int message[9])
{
    OPEN_CFW_DISPLAY_MANAGER_COMMAND3(
        message[1],
        message[2],
        message[3],
        message[4],
        message[5],
        message[6]
    );
}

static __attribute__((always_inline)) inline void
open_cfw_display_manager_log_command6(void)
{
    if ((OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_MANAGER_LOG(
            3U,
            OPEN_CFW_DISPLAY_MANAGER_TAG,
            OPEN_CFW_DISPLAY_MANAGER_FILE,
            OPEN_CFW_DISPLAY_MANAGER_FUNCTION,
            0x10DU,
            OPEN_CFW_DISPLAY_MANAGER_COMMAND6_FORMAT
        );
    }
    if (open_cfw_display_manager_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_MANAGER_BACKEND_LOG(
            0x0C000000U,
            OPEN_CFW_DISPLAY_MANAGER_COMMAND6_BACKEND,
            OPEN_CFW_DISPLAY_MANAGER_COMMAND6_BACKEND
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_display_manager_log_unknown(unsigned int command)
{
    if ((OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_MANAGER_LOG(
            2U,
            OPEN_CFW_DISPLAY_MANAGER_TAG,
            OPEN_CFW_DISPLAY_MANAGER_FILE,
            OPEN_CFW_DISPLAY_MANAGER_FUNCTION,
            0x117U,
            OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_FORMAT,
            command
        );
    }
    if (open_cfw_display_manager_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_MANAGER_BACKEND_LOG(
            0x08400000U,
            OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_BACKEND,
            OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_BACKEND,
            command
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_manager_thread(void *argument)
{
    unsigned int message[9];
    unsigned int first;
    unsigned int second;

    (void)argument;
    OPEN_CFW_DISPLAY_MANAGER_QUEUE_INITIALIZE();
    OPEN_CFW_DISPLAY_MANAGER_RESOURCE_ACQUIRE();
    OPEN_CFW_DISPLAY_MANAGER_INTERFACE_INITIALIZE();
    OPEN_CFW_DISPLAY_MANAGER_RESOURCE_RELEASE();
    OPEN_CFW_DISPLAY_MANAGER_TIMER_INITIALIZE();

    do {
        do {
            open_cfw_display_manager_clear_message(message);
        } while (
            OPEN_CFW_DISPLAY_MANAGER_QUEUE_GET(
                OPEN_CFW_DISPLAY_MANAGER_QUEUE_HANDLE,
                message,
                0U,
                0xFFFFFFFFU
            ) != 0
        );

        OPEN_CFW_DISPLAY_MANAGER_ENTER();
        if (message[0] == 3U) {
            OPEN_CFW_DISPLAY_MANAGER_PREPARE();
            OPEN_CFW_DISPLAY_MANAGER_DISPLAY_UNLOCK();
        }

        if ((OPEN_CFW_DISPLAY_MANAGER_GATE() != 0) || (message[8] != 0U)) {
            switch (message[0]) {
            case 0U:
                OPEN_CFW_DISPLAY_MANAGER_COMMAND0();
                break;
            case 1U:
                OPEN_CFW_DISPLAY_MANAGER_COMMAND1();
                OPEN_CFW_DISPLAY_MANAGER_TIMER_START();
                OPEN_CFW_DISPLAY_MANAGER_ACTIVE = 1U;
                break;
            case 2U:
                if (OPEN_CFW_DISPLAY_MANAGER_ACTIVE == 1U) {
                    OPEN_CFW_DISPLAY_MANAGER_COMMAND2();
                }
                break;
            case 3U:
                if (OPEN_CFW_DISPLAY_MANAGER_ACTIVE == 1U) {
                    open_cfw_display_manager_command3(message);
                }
                break;
            case 4U:
                if (OPEN_CFW_DISPLAY_MANAGER_ACTIVE == 1U) {
                    first = 0U;
                    second = 0U;
                    OPEN_CFW_DISPLAY_MANAGER_QUERY(
                        message[7],
                        &first,
                        &second
                    );
                    OPEN_CFW_DISPLAY_MANAGER_QUERY_RESULT(
                        message[7],
                        second,
                        first
                    );
                }
                break;
            case 5U:
                if (OPEN_CFW_DISPLAY_MANAGER_ACTIVE == 1U) {
                    OPEN_CFW_DISPLAY_MANAGER_TIMER_STOP();
                    OPEN_CFW_DISPLAY_MANAGER_COMMAND5();
                    OPEN_CFW_DISPLAY_MANAGER_ACTIVE = 0U;
                }
                break;
            case 6U:
                if (
                    (OPEN_CFW_DISPLAY_MANAGER_ACTIVE == 1U)
                    && (
                        (
                            OPEN_CFW_DISPLAY_MANAGER_COMMAND6_GATE(1U)
                            & 0xFFU
                        ) == 0U
                    )
                ) {
                    OPEN_CFW_DISPLAY_MANAGER_PREPARE();
                    OPEN_CFW_DISPLAY_MANAGER_DISPLAY_UNLOCK();
                    open_cfw_display_manager_command3(message);
                    open_cfw_display_manager_log_command6();
                }
                break;
            case 8U:
                if (OPEN_CFW_DISPLAY_MANAGER_ACTIVE == 1U) {
                    OPEN_CFW_DISPLAY_MANAGER_COMMAND8(
                        message[7] & 0xFFU
                    );
                }
                break;
            default:
                open_cfw_display_manager_log_unknown(message[0]);
                break;
            }
        }

        OPEN_CFW_DISPLAY_MANAGER_LEAVE();
    } while (OPEN_CFW_DISPLAY_MANAGER_LOOP_CONTINUES());
}

#undef OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_BACKEND
#undef OPEN_CFW_DISPLAY_MANAGER_UNKNOWN_FORMAT
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND6_BACKEND
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND6_FORMAT
#undef OPEN_CFW_DISPLAY_MANAGER_FUNCTION
#undef OPEN_CFW_DISPLAY_MANAGER_FILE
#undef OPEN_CFW_DISPLAY_MANAGER_TAG
#undef OPEN_CFW_DISPLAY_MANAGER_LOOP_CONTINUES
#undef OPEN_CFW_DISPLAY_MANAGER_BACKEND_LOG
#undef OPEN_CFW_DISPLAY_MANAGER_LOG
#undef OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND8
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND6_GATE
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND5
#undef OPEN_CFW_DISPLAY_MANAGER_TIMER_STOP
#undef OPEN_CFW_DISPLAY_MANAGER_QUERY_RESULT
#undef OPEN_CFW_DISPLAY_MANAGER_QUERY
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND3
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND2
#undef OPEN_CFW_DISPLAY_MANAGER_TIMER_START
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND1
#undef OPEN_CFW_DISPLAY_MANAGER_COMMAND0
#undef OPEN_CFW_DISPLAY_MANAGER_LEAVE
#undef OPEN_CFW_DISPLAY_MANAGER_GATE
#undef OPEN_CFW_DISPLAY_MANAGER_DISPLAY_UNLOCK
#undef OPEN_CFW_DISPLAY_MANAGER_PREPARE
#undef OPEN_CFW_DISPLAY_MANAGER_ENTER
#undef OPEN_CFW_DISPLAY_MANAGER_QUEUE_GET
#undef OPEN_CFW_DISPLAY_MANAGER_TIMER_INITIALIZE
#undef OPEN_CFW_DISPLAY_MANAGER_RESOURCE_RELEASE
#undef OPEN_CFW_DISPLAY_MANAGER_INTERFACE_INITIALIZE
#undef OPEN_CFW_DISPLAY_MANAGER_RESOURCE_ACQUIRE
#undef OPEN_CFW_DISPLAY_MANAGER_QUEUE_INITIALIZE
#undef OPEN_CFW_DISPLAY_MANAGER_ACTIVE
#undef OPEN_CFW_DISPLAY_MANAGER_QUEUE_HANDLE
