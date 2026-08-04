/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer list/queue initialization matched to stock entry 0x0047EAB8.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_runtime_init_uintptr;

typedef void (*open_cfw_rtos_timer_runtime_init_void_function)(void);
typedef void (*open_cfw_rtos_timer_runtime_init_list_function)(void *);
typedef void *(*open_cfw_rtos_timer_runtime_init_queue_function)(
    unsigned int,
    unsigned int,
    void *,
    void *,
    unsigned int
);

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_ENTER_CRITICAL
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_ENTER_CRITICAL() \
    (((open_cfw_rtos_timer_runtime_init_void_function) \
        (open_cfw_rtos_timer_runtime_init_uintptr)0x004420D1U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_EXIT_CRITICAL
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_EXIT_CRITICAL() \
    (((open_cfw_rtos_timer_runtime_init_void_function) \
        (open_cfw_rtos_timer_runtime_init_uintptr)0x004420E9U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_READ_QUEUE
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_READ_QUEUE() \
    ((void *)(open_cfw_rtos_timer_runtime_init_uintptr)( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_runtime_init_uintptr)0x20074AB0U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_QUEUE
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_QUEUE(value) \
    (*(volatile unsigned int *)( \
        open_cfw_rtos_timer_runtime_init_uintptr)0x20074AB0U = \
            (unsigned int)( \
                open_cfw_rtos_timer_runtime_init_uintptr)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CURRENT_LIST
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CURRENT_LIST() \
    ((void *)(open_cfw_rtos_timer_runtime_init_uintptr)0x20073D60U)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_OVERFLOW_LIST
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_OVERFLOW_LIST() \
    ((void *)(open_cfw_rtos_timer_runtime_init_uintptr)0x20073D74U)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_CURRENT
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_CURRENT(value) \
    (*(volatile unsigned int *)( \
        open_cfw_rtos_timer_runtime_init_uintptr)0x20074AA8U = \
            (unsigned int)( \
                open_cfw_rtos_timer_runtime_init_uintptr)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_OVERFLOW
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_OVERFLOW(value) \
    (*(volatile unsigned int *)( \
        open_cfw_rtos_timer_runtime_init_uintptr)0x20074AACU = \
            (unsigned int)( \
                open_cfw_rtos_timer_runtime_init_uintptr)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_LIST
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_LIST(list) \
    (((open_cfw_rtos_timer_runtime_init_list_function) \
        (open_cfw_rtos_timer_runtime_init_uintptr)0x0045607DU)(list))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_STORAGE
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_STORAGE() \
    ((void *)(open_cfw_rtos_timer_runtime_init_uintptr)0x2006D7B4U)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_CONTROL
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_CONTROL() \
    ((void *)(open_cfw_rtos_timer_runtime_init_uintptr)0x20072EE8U)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CREATE_QUEUE
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CREATE_QUEUE(...) \
    (((open_cfw_rtos_timer_runtime_init_queue_function) \
        (open_cfw_rtos_timer_runtime_init_uintptr)0x004415CBU)(__VA_ARGS__))
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_runtime_initialize(void)
{
    void *current_list;
    void *overflow_list;
    void *queue;

    OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_ENTER_CRITICAL();
    queue = OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_READ_QUEUE();
    if (queue == (void *)0) {
        current_list = OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CURRENT_LIST();
        OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_LIST(current_list);
        overflow_list = OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_OVERFLOW_LIST();
        OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_LIST(overflow_list);
        OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_CURRENT(current_list);
        OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_OVERFLOW(overflow_list);
        queue = OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CREATE_QUEUE(
            0x32U,
            0x10U,
            OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_STORAGE(),
            OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_CONTROL(),
            0U
        );
        OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_QUEUE(queue);
    }
    OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_EXIT_CRITICAL();
}

#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CREATE_QUEUE
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_CONTROL
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_STORAGE
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_LIST
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_OVERFLOW
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_CURRENT
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_OVERFLOW_LIST
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CURRENT_LIST
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_QUEUE
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_READ_QUEUE
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_EXIT_CRITICAL
#undef OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_ENTER_CRITICAL
