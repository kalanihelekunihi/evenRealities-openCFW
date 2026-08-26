/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-routed clean-room reconstruction of eleven functions in the G2
 * Cordio/Ambiq FreeRTOS WSF timer port.  Official AmbiqSuite 2.5.1 source
 * SHA-256 4d6641c8de197367a6c1561738b389afd164321b879264cd795796c80ab55dd7
 * is the selected exact implementation/source family.  It is proprietary
 * reference material and is not copied here; this GPL candidate is an
 * independently expressed behavioral reconstruction.  Packetcraft r19.02
 * commit 86372d84ef0386d8834ed036e613c8f2ded1ff16 remains a public semantic
 * oracle for the queue-service lineage.
 */

#include "runtime_cordio_wsf_timer_candidate.h"

#if !defined(OPEN_CFW_WSF_TIMER_REMOVE_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_INSERT_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_INIT_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_START_SEC_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_START_MS_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_STOP_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_UPDATE_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_NEXT_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_EXPIRED_ONLY) && \
    !defined(OPEN_CFW_WSF_TIMER_UPDATE_TICKS_ONLY)
#define OPEN_CFW_WSF_TIMER_BUILD_ALL 1
#endif

#if defined(__arm__) || defined(__thumb__)
__asm__(".type open_cfw_cordio_wsf_timer_callback_candidate,%function");
#endif

#ifdef OPEN_CFW_WSF_TIMER_PRODUCTION
#define OPEN_CFW_WSF_TIMER_NAME ((const char *)0x0078C95CU)
#define OPEN_CFW_WSF_TIMER_QUEUE \
    (*(struct open_cfw_cordio_wsf_queue_candidate *)0x200741B0U)
#define OPEN_CFW_WSF_TIMER_HANDLE (*(void **)0x20074EF4U)
#define OPEN_CFW_WSF_TIMER_LAST_TICK (*(uint32_t *)0x20074EF8U)
#else
#define OPEN_CFW_WSF_TIMER_NAME "WSF Timer"
#define OPEN_CFW_WSF_TIMER_QUEUE open_cfw_cordio_wsf_timer_queue_candidate
#define OPEN_CFW_WSF_TIMER_HANDLE open_cfw_cordio_wsf_freertos_timer_candidate
#define OPEN_CFW_WSF_TIMER_LAST_TICK open_cfw_cordio_wsf_last_tick_candidate
#endif

enum {
    OPEN_CFW_CORDIO_WSF_TICKS_PER_SECOND = 100U,
    OPEN_CFW_CORDIO_WSF_COUNTER_TICKS_PER_WSF_TICK = 10U,
    OPEN_CFW_CORDIO_WSF_INITIAL_PERIOD_TICKS = 10U,
    OPEN_CFW_CORDIO_WSF_TIMER_EVENT = 2U,
    OPEN_CFW_CORDIO_WSF_FREERTOS_PERIOD_NUMERATOR = 10000U,
    OPEN_CFW_CORDIO_WSF_FREERTOS_PERIOD_DENOMINATOR = 1000U,
    OPEN_CFW_CORDIO_WSF_TIMER_CHANGE_PERIOD_COMMAND = 4U,
    OPEN_CFW_CORDIO_WSF_TIMER_COMMAND_WAIT_TICKS = 100U,
    OPEN_CFW_CORDIO_WSF_TIMER_COMMAND_SUCCESS = 1
};

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_REMOVE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_remove_candidate(
    struct open_cfw_cordio_wsf_timer *timer
)
{
    struct open_cfw_cordio_wsf_timer *current;
    struct open_cfw_cordio_wsf_timer *previous = NULL;

    current = OPEN_CFW_WSF_TIMER_QUEUE.head;
    while ((current != NULL) && (current != timer)) {
        previous = current;
        current = current->next;
    }
    if (current != NULL) {
        open_cfw_cordio_wsf_queue_remove_candidate(
            &OPEN_CFW_WSF_TIMER_QUEUE,
            timer,
            previous
        );
        timer->is_started = 0U;
    }
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_INSERT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_insert_candidate(
    struct open_cfw_cordio_wsf_timer *timer,
    uint32_t ticks
)
{
    struct open_cfw_cordio_wsf_timer *current;
    struct open_cfw_cordio_wsf_timer *previous = NULL;

    open_cfw_cordio_wsf_task_lock_candidate();
    if (timer->is_started != 0U) {
        open_cfw_cordio_wsf_timer_remove_candidate(timer);
    }

    timer->is_started = 1U;
    timer->ticks = ticks;
    current = OPEN_CFW_WSF_TIMER_QUEUE.head;
    while ((current != NULL) && (timer->ticks >= current->ticks)) {
        previous = current;
        current = current->next;
    }
    open_cfw_cordio_wsf_queue_insert_candidate(
        &OPEN_CFW_WSF_TIMER_QUEUE,
        timer,
        previous
    );
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_callback_candidate(void *timer)
{
    (void)timer;
    open_cfw_cordio_wsf_task_set_ready_candidate(
        0U,
        OPEN_CFW_CORDIO_WSF_TIMER_EVENT
    );
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_INIT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_init_candidate(void)
{
    OPEN_CFW_WSF_TIMER_QUEUE.head = NULL;
    OPEN_CFW_WSF_TIMER_QUEUE.tail = NULL;

    if (OPEN_CFW_WSF_TIMER_HANDLE != NULL) {
        return;
    }

    OPEN_CFW_WSF_TIMER_HANDLE =
        open_cfw_cordio_wsf_timer_create_candidate(
            OPEN_CFW_WSF_TIMER_NAME,
            OPEN_CFW_CORDIO_WSF_INITIAL_PERIOD_TICKS,
            false,
            NULL,
            open_cfw_cordio_wsf_timer_callback_candidate
        );
    if (OPEN_CFW_WSF_TIMER_HANDLE == NULL) {
        /* The stock assertion path is terminal. */
        open_cfw_cordio_wsf_timer_fatal_candidate();
        return;
    }
    OPEN_CFW_WSF_TIMER_LAST_TICK =
        open_cfw_cordio_wsf_tick_counter_get_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_START_SEC_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_start_sec_candidate(
    struct open_cfw_cordio_wsf_timer *timer,
    uint32_t seconds
)
{
    open_cfw_cordio_wsf_timer_insert_candidate(
        timer,
        seconds * OPEN_CFW_CORDIO_WSF_TICKS_PER_SECOND
    );
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_START_MS_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_start_ms_candidate(
    struct open_cfw_cordio_wsf_timer *timer,
    uint32_t milliseconds
)
{
    open_cfw_cordio_wsf_timer_insert_candidate(
        timer,
        milliseconds / OPEN_CFW_CORDIO_WSF_COUNTER_TICKS_PER_WSF_TICK
    );
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_STOP_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_stop_candidate(
    struct open_cfw_cordio_wsf_timer *timer
)
{
    open_cfw_cordio_wsf_task_lock_candidate();
    open_cfw_cordio_wsf_timer_remove_candidate(timer);
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_UPDATE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_update_candidate(uint32_t ticks)
{
    struct open_cfw_cordio_wsf_timer *current;

    open_cfw_cordio_wsf_task_lock_candidate();
    current = OPEN_CFW_WSF_TIMER_QUEUE.head;
    while (current != NULL) {
        if (ticks < current->ticks) {
            current->ticks -= ticks;
        } else {
            current->ticks = 0U;
            open_cfw_cordio_wsf_task_set_ready_candidate(
                current->handler_id,
                OPEN_CFW_CORDIO_WSF_TIMER_EVENT
            );
        }
        current = current->next;
    }
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_NEXT_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_cordio_wsf_timer_next_expiration_candidate(
    bool *timer_running
)
{
    struct open_cfw_cordio_wsf_timer *head;
    uint32_t ticks;

    open_cfw_cordio_wsf_task_lock_candidate();
    head = OPEN_CFW_WSF_TIMER_QUEUE.head;
    if (head == NULL) {
        *timer_running = false;
        ticks = 0U;
    } else {
        *timer_running = true;
        ticks = head->ticks;
    }
    open_cfw_cordio_wsf_task_unlock_candidate();
    return ticks;
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_EXPIRED_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_wsf_timer *
open_cfw_cordio_wsf_timer_service_expired_candidate(uint8_t task_id)
{
    struct open_cfw_cordio_wsf_timer *head;

    (void)task_id;
    open_cfw_cordio_wsf_task_lock_candidate();
    head = OPEN_CFW_WSF_TIMER_QUEUE.head;
    if ((head != NULL) && (head->ticks == 0U)) {
        open_cfw_cordio_wsf_queue_remove_candidate(
            &OPEN_CFW_WSF_TIMER_QUEUE,
            head,
            NULL
        );
        head->is_started = 0U;
        open_cfw_cordio_wsf_task_unlock_candidate();
        return head;
    }
    open_cfw_cordio_wsf_task_unlock_candidate();
    return NULL;
}
#endif

#if defined(OPEN_CFW_WSF_TIMER_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_TIMER_UPDATE_TICKS_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_timer_update_ticks_candidate(void)
{
    bool timer_running;
    uint32_t current_tick;
    uint32_t elapsed_counter_ticks;
    uint32_t elapsed_wsf_ticks;
    uint32_t next_expiration;
    uint32_t period_ticks;
    int status;

    current_tick = open_cfw_cordio_wsf_tick_counter_get_candidate();
    elapsed_counter_ticks =
        current_tick - OPEN_CFW_WSF_TIMER_LAST_TICK;
    elapsed_wsf_ticks = elapsed_counter_ticks /
        OPEN_CFW_CORDIO_WSF_COUNTER_TICKS_PER_WSF_TICK;
    if (elapsed_wsf_ticks != 0U) {
        open_cfw_cordio_wsf_timer_update_candidate(elapsed_wsf_ticks);
        OPEN_CFW_WSF_TIMER_LAST_TICK = current_tick;
    }

    next_expiration =
        open_cfw_cordio_wsf_timer_next_expiration_candidate(&timer_running);
    (void)timer_running;
    if (next_expiration == 0U) {
        return;
    }

    period_ticks = (
        next_expiration * OPEN_CFW_CORDIO_WSF_FREERTOS_PERIOD_NUMERATOR
    ) / OPEN_CFW_CORDIO_WSF_FREERTOS_PERIOD_DENOMINATOR;
    status = open_cfw_cordio_wsf_timer_command_candidate(
        OPEN_CFW_WSF_TIMER_HANDLE,
        OPEN_CFW_CORDIO_WSF_TIMER_CHANGE_PERIOD_COMMAND,
        period_ticks,
        0U,
        OPEN_CFW_CORDIO_WSF_TIMER_COMMAND_WAIT_TICKS
    );
    if (status != OPEN_CFW_CORDIO_WSF_TIMER_COMMAND_SUCCESS) {
#ifndef OPEN_CFW_WSF_TIMER_PRODUCTION
        open_cfw_cordio_wsf_timer_command_failure_candidate();
#endif
        open_cfw_cordio_wsf_timer_fatal_candidate();
    }
}
#endif
