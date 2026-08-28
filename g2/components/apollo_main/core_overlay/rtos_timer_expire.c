/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS expired-timer processor matched to stock entry 0x0047E83A.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_expire_uintptr;

typedef unsigned int (*open_cfw_rtos_timer_expire_remove_function)(void *);
typedef void (*open_cfw_rtos_timer_expire_callback_function)(void *);

void open_cfw_rtos_timer_reload(
    void *,
    unsigned int,
    unsigned int
);

#ifndef OPEN_CFW_RTOS_TIMER_EXPIRE_TIMER
static __attribute__((always_inline)) inline void *
open_cfw_rtos_timer_expire_timer(void)
{
    unsigned int timer_lists =
        *(volatile unsigned int *)
            (open_cfw_rtos_timer_expire_uintptr)0x20074AA8U;
    unsigned int active_list =
        *(volatile unsigned int *)
            (open_cfw_rtos_timer_expire_uintptr)(timer_lists + 0x0CU);
    unsigned int timer =
        *(volatile unsigned int *)
            (open_cfw_rtos_timer_expire_uintptr)(active_list + 0x0CU);

    return (void *)(open_cfw_rtos_timer_expire_uintptr)timer;
}

#define OPEN_CFW_RTOS_TIMER_EXPIRE_TIMER() \
    open_cfw_rtos_timer_expire_timer()
#endif

#ifndef OPEN_CFW_RTOS_TIMER_EXPIRE_REMOVE
#define OPEN_CFW_RTOS_TIMER_EXPIRE_REMOVE(item) \
    (((open_cfw_rtos_timer_expire_remove_function) \
        (open_cfw_rtos_timer_expire_uintptr)0x004560E9U)(item))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_EXPIRE_STATUS
#define OPEN_CFW_RTOS_TIMER_EXPIRE_STATUS(timer) \
    (*(volatile unsigned char *)( \
        (volatile unsigned char *)(timer) + 0x28U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_EXPIRE_WRITE_STATUS
#define OPEN_CFW_RTOS_TIMER_EXPIRE_WRITE_STATUS(timer, value) \
    do { \
        *(volatile unsigned char *)( \
            (volatile unsigned char *)(timer) + 0x28U) = \
                (unsigned char)(value); \
    } while (0)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_EXPIRE_RELOAD
#define OPEN_CFW_RTOS_TIMER_EXPIRE_RELOAD( \
    timer, expired_time, time_now \
) \
    open_cfw_rtos_timer_reload(timer, expired_time, time_now)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_EXPIRE_CALLBACK
#define OPEN_CFW_RTOS_TIMER_EXPIRE_CALLBACK(timer) \
    do { \
        unsigned int open_cfw_callback_address = \
            *(volatile unsigned int *)( \
                (volatile unsigned char *)(timer) + 0x20U); \
        ((open_cfw_rtos_timer_expire_callback_function) \
            (open_cfw_rtos_timer_expire_uintptr) \
            open_cfw_callback_address)(timer); \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_expire(
    unsigned int expired_time,
    unsigned int time_now
)
{
    void *timer = OPEN_CFW_RTOS_TIMER_EXPIRE_TIMER();

    (void)OPEN_CFW_RTOS_TIMER_EXPIRE_REMOVE(
        (unsigned char *)timer + 0x04U
    );
    if ((OPEN_CFW_RTOS_TIMER_EXPIRE_STATUS(timer) & 0x04U) != 0U) {
        OPEN_CFW_RTOS_TIMER_EXPIRE_RELOAD(
            timer,
            expired_time,
            time_now
        );
    } else {
        OPEN_CFW_RTOS_TIMER_EXPIRE_WRITE_STATUS(
            timer,
            OPEN_CFW_RTOS_TIMER_EXPIRE_STATUS(timer) & 0xFEU
        );
    }
    OPEN_CFW_RTOS_TIMER_EXPIRE_CALLBACK(timer);
}

#undef OPEN_CFW_RTOS_TIMER_EXPIRE_CALLBACK
#undef OPEN_CFW_RTOS_TIMER_EXPIRE_RELOAD
#undef OPEN_CFW_RTOS_TIMER_EXPIRE_WRITE_STATUS
#undef OPEN_CFW_RTOS_TIMER_EXPIRE_STATUS
#undef OPEN_CFW_RTOS_TIMER_EXPIRE_REMOVE
#undef OPEN_CFW_RTOS_TIMER_EXPIRE_TIMER
