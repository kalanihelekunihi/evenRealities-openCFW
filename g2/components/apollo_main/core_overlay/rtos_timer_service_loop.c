/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS timer-service task loop matched to stock entry 0x0047E878.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_service_loop_uintptr;

typedef unsigned int (
    *open_cfw_rtos_timer_service_loop_query_function
)(unsigned int *);
typedef void (*open_cfw_rtos_timer_service_loop_wait_function)(
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_rtos_timer_service_loop_commands_function)(void);

unsigned int open_cfw_rtos_timer_query(unsigned int *);
void open_cfw_rtos_timer_drain(void);

#ifndef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_QUERY
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_QUERY(empty) \
    open_cfw_rtos_timer_query(empty)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_WAIT
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_WAIT(expiry, empty) \
    (((open_cfw_rtos_timer_service_loop_wait_function) \
        (open_cfw_rtos_timer_service_loop_uintptr)0x0047E88DU)( \
            expiry, empty))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_COMMANDS
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_COMMANDS() \
    open_cfw_rtos_timer_drain()
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_CONTINUE
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_CONTINUE() 1U
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_service_loop(void *argument)
{
    (void)argument;

    for (;;) {
        unsigned int active_list_empty = 0U;
        unsigned int next_expiry =
            OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_QUERY(&active_list_empty);

        OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_WAIT(
            next_expiry,
            active_list_empty
        );
        OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_COMMANDS();
        if (OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_CONTINUE() == 0U) {
            return;
        }
    }
}

#undef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_CONTINUE
#undef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_COMMANDS
#undef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_WAIT
#undef OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_QUERY
