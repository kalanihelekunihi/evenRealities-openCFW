/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer command-drain routine matched to stock entry 0x0047E97A.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_drain_uintptr;

struct open_cfw_rtos_timer_drain_message {
    int command_id;
    union {
        struct {
            unsigned int message_value;
            unsigned int timer;
        } timer;
        struct {
            unsigned int function;
            unsigned int parameter_one;
            unsigned int parameter_two;
        } callback;
    } payload;
};

typedef unsigned int (*open_cfw_rtos_timer_drain_receive_function)(
    void *,
    struct open_cfw_rtos_timer_drain_message *,
    unsigned int
);
typedef void (*open_cfw_rtos_timer_drain_pended_function)(
    void *,
    unsigned int
);
typedef unsigned int (*open_cfw_rtos_timer_drain_remove_function)(void *);
typedef void (*open_cfw_rtos_timer_drain_callback_function)(void *);
typedef void (*open_cfw_rtos_timer_drain_free_function)(void *);
typedef void (*open_cfw_rtos_timer_drain_fail_function)(void);

unsigned int open_cfw_rtos_timer_sample(unsigned int *);
unsigned int open_cfw_rtos_timer_insert(
    void *,
    unsigned int,
    unsigned int,
    unsigned int
);
void open_cfw_rtos_timer_reload(void *, unsigned int, unsigned int);

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_QUEUE
#define OPEN_CFW_RTOS_TIMER_DRAIN_QUEUE() \
    ((void *)(open_cfw_rtos_timer_drain_uintptr)( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_drain_uintptr)0x20074AB0U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_RECEIVE
#define OPEN_CFW_RTOS_TIMER_DRAIN_RECEIVE(queue, message, ticks) \
    (((open_cfw_rtos_timer_drain_receive_function) \
        (open_cfw_rtos_timer_drain_uintptr)0x00441B0BU)( \
            queue, message, ticks))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_PENDED_CALL
#define OPEN_CFW_RTOS_TIMER_DRAIN_PENDED_CALL( \
    function, parameter_one, parameter_two \
) \
    (((open_cfw_rtos_timer_drain_pended_function) \
        (open_cfw_rtos_timer_drain_uintptr)(function))( \
            (void *)(open_cfw_rtos_timer_drain_uintptr)(parameter_one), \
            parameter_two))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_TIMER
#define OPEN_CFW_RTOS_TIMER_DRAIN_TIMER(value) \
    ((void *)(open_cfw_rtos_timer_drain_uintptr)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_LIST_CONTAINER
#define OPEN_CFW_RTOS_TIMER_DRAIN_LIST_CONTAINER(timer) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x14U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_LIST_ITEM
#define OPEN_CFW_RTOS_TIMER_DRAIN_LIST_ITEM(timer) \
    ((void *)((unsigned char *)(timer) + 0x04U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_REMOVE
#define OPEN_CFW_RTOS_TIMER_DRAIN_REMOVE(item) \
    (((open_cfw_rtos_timer_drain_remove_function) \
        (open_cfw_rtos_timer_drain_uintptr)0x004560E9U)(item))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_SAMPLE
#define OPEN_CFW_RTOS_TIMER_DRAIN_SAMPLE(switched) \
    open_cfw_rtos_timer_sample(switched)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS
#define OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer) \
    (*(volatile unsigned char *)( \
        (volatile unsigned char *)(timer) + 0x28U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS
#define OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(timer, value) \
    (*(volatile unsigned char *)( \
        (volatile unsigned char *)(timer) + 0x28U) = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD
#define OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD(timer) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x18U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_PERIOD
#define OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_PERIOD(timer, value) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x18U) = (value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_INSERT
#define OPEN_CFW_RTOS_TIMER_DRAIN_INSERT( \
    timer, next_expiry, time_now, command_time \
) \
    open_cfw_rtos_timer_insert( \
        timer, next_expiry, time_now, command_time \
    )
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_RELOAD
#define OPEN_CFW_RTOS_TIMER_DRAIN_RELOAD( \
    timer, next_expiry, time_now \
) \
    open_cfw_rtos_timer_reload(timer, next_expiry, time_now)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_CALLBACK
#define OPEN_CFW_RTOS_TIMER_DRAIN_CALLBACK(timer) \
    do { \
        unsigned int open_cfw_callback_address = \
            *(volatile unsigned int *)( \
                (volatile unsigned char *)(timer) + 0x20U); \
        ((open_cfw_rtos_timer_drain_callback_function) \
            (open_cfw_rtos_timer_drain_uintptr) \
            open_cfw_callback_address)(timer); \
    } while (0)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_FREE
#define OPEN_CFW_RTOS_TIMER_DRAIN_FREE(timer) \
    (((open_cfw_rtos_timer_drain_free_function) \
        (open_cfw_rtos_timer_drain_uintptr)0x00456211U)(timer))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DRAIN_FAIL_STOP
#define OPEN_CFW_RTOS_TIMER_DRAIN_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_timer_drain_fail_function) \
            (open_cfw_rtos_timer_drain_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_timer_drain_uintptr) \
            (~(open_cfw_rtos_timer_drain_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_drain(void)
{
    for (;;) {
        struct open_cfw_rtos_timer_drain_message message;
        unsigned int lists_switched;
        unsigned int time_now;
        void *timer;

        if (
            OPEN_CFW_RTOS_TIMER_DRAIN_RECEIVE(
                OPEN_CFW_RTOS_TIMER_DRAIN_QUEUE(),
                &message,
                0U
            ) == 0U
        ) {
            return;
        }

        if (message.command_id < 0) {
            OPEN_CFW_RTOS_TIMER_DRAIN_PENDED_CALL(
                message.payload.callback.function,
                message.payload.callback.parameter_one,
                message.payload.callback.parameter_two
            );
            continue;
        }

        timer = OPEN_CFW_RTOS_TIMER_DRAIN_TIMER(
            message.payload.timer.timer
        );
        if (
            OPEN_CFW_RTOS_TIMER_DRAIN_LIST_CONTAINER(timer)
            != 0U
        ) {
            (void)OPEN_CFW_RTOS_TIMER_DRAIN_REMOVE(
                OPEN_CFW_RTOS_TIMER_DRAIN_LIST_ITEM(timer)
            );
        }

        time_now = OPEN_CFW_RTOS_TIMER_DRAIN_SAMPLE(&lists_switched);
        (void)lists_switched;

        switch (message.command_id) {
            case 1:
            case 2:
            case 6:
            case 7: {
                unsigned int period;
                unsigned int next_expiry;

                OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(
                    timer,
                    OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer) | 1U
                );
                period = OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD(timer);
                next_expiry =
                    message.payload.timer.message_value + period;
                if (
                    OPEN_CFW_RTOS_TIMER_DRAIN_INSERT(
                        timer,
                        next_expiry,
                        time_now,
                        message.payload.timer.message_value
                    ) != 0U
                ) {
                    if (
                        (
                            OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer)
                            & 4U
                        ) != 0U
                    ) {
                        period =
                            OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD(timer);
                        OPEN_CFW_RTOS_TIMER_DRAIN_RELOAD(
                            timer,
                            message.payload.timer.message_value + period,
                            time_now
                        );
                    } else {
                        OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(
                            timer,
                            OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer)
                                & 0xFEU
                        );
                    }
                    OPEN_CFW_RTOS_TIMER_DRAIN_CALLBACK(timer);
                }
                break;
            }

            case 3:
            case 8:
                OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(
                    timer,
                    OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer) & 0xFEU
                );
                break;

            case 4:
            case 9: {
                unsigned int period;

                OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(
                    timer,
                    OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer) | 1U
                );
                OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_PERIOD(
                    timer,
                    message.payload.timer.message_value
                );
                if (OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD(timer) == 0U) {
                    OPEN_CFW_RTOS_TIMER_DRAIN_FAIL_STOP();
                    return;
                }
                period = OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD(timer);
                (void)OPEN_CFW_RTOS_TIMER_DRAIN_INSERT(
                    timer,
                    time_now + period,
                    time_now,
                    time_now
                );
                break;
            }

            case 5:
                if (
                    (
                        OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer)
                        & 2U
                    ) == 0U
                ) {
                    OPEN_CFW_RTOS_TIMER_DRAIN_FREE(timer);
                } else {
                    OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(
                        timer,
                        OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer)
                            & 0xFEU
                    );
                }
                break;

            default:
                break;
        }
    }
}

#undef OPEN_CFW_RTOS_TIMER_DRAIN_FAIL_STOP
#undef OPEN_CFW_RTOS_TIMER_DRAIN_FREE
#undef OPEN_CFW_RTOS_TIMER_DRAIN_CALLBACK
#undef OPEN_CFW_RTOS_TIMER_DRAIN_RELOAD
#undef OPEN_CFW_RTOS_TIMER_DRAIN_INSERT
#undef OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_PERIOD
#undef OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD
#undef OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS
#undef OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS
#undef OPEN_CFW_RTOS_TIMER_DRAIN_SAMPLE
#undef OPEN_CFW_RTOS_TIMER_DRAIN_REMOVE
#undef OPEN_CFW_RTOS_TIMER_DRAIN_LIST_ITEM
#undef OPEN_CFW_RTOS_TIMER_DRAIN_LIST_CONTAINER
#undef OPEN_CFW_RTOS_TIMER_DRAIN_TIMER
#undef OPEN_CFW_RTOS_TIMER_DRAIN_PENDED_CALL
#undef OPEN_CFW_RTOS_TIMER_DRAIN_RECEIVE
#undef OPEN_CFW_RTOS_TIMER_DRAIN_QUEUE
