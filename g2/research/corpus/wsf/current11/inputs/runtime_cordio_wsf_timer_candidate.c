/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room reconstruction of eleven functions in the G2
 * Cordio/Ambiq FreeRTOS WSF timer port.  Packetcraft r19.02 commit
 * 86372d84ef0386d8834ed036e613c8f2ded1ff16 is a semantic oracle for the
 * first two routines; the stock translation unit and ABI remain a vendor
 * fork and are not attributed to that commit.
 */

#include "runtime_cordio_wsf_timer_candidate.h"

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

void open_cfw_cordio_wsf_timer_remove_candidate(
    struct open_cfw_cordio_wsf_timer *timer
)
{
    struct open_cfw_cordio_wsf_timer *current;
    struct open_cfw_cordio_wsf_timer *previous = NULL;

    current = open_cfw_cordio_wsf_timer_queue_candidate.head;
    while ((current != NULL) && (current != timer)) {
        previous = current;
        current = current->next;
    }
    if (current != NULL) {
        open_cfw_cordio_wsf_queue_remove_candidate(
            &open_cfw_cordio_wsf_timer_queue_candidate,
            timer,
            previous
        );
        timer->is_started = 0U;
    }
}

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
    current = open_cfw_cordio_wsf_timer_queue_candidate.head;
    while ((current != NULL) && (timer->ticks >= current->ticks)) {
        previous = current;
        current = current->next;
    }
    open_cfw_cordio_wsf_queue_insert_candidate(
        &open_cfw_cordio_wsf_timer_queue_candidate,
        timer,
        previous
    );
    open_cfw_cordio_wsf_task_unlock_candidate();
}

void open_cfw_cordio_wsf_timer_callback_candidate(void *timer)
{
    (void)timer;
    open_cfw_cordio_wsf_task_set_ready_candidate(
        0U,
        OPEN_CFW_CORDIO_WSF_TIMER_EVENT
    );
}

void open_cfw_cordio_wsf_timer_init_candidate(void)
{
    open_cfw_cordio_wsf_timer_queue_candidate.head = NULL;
    open_cfw_cordio_wsf_timer_queue_candidate.tail = NULL;

    if (open_cfw_cordio_wsf_freertos_timer_candidate != NULL) {
        return;
    }

    open_cfw_cordio_wsf_freertos_timer_candidate =
        open_cfw_cordio_wsf_timer_create_candidate(
            "WSF Timer",
            OPEN_CFW_CORDIO_WSF_INITIAL_PERIOD_TICKS,
            false,
            NULL,
            open_cfw_cordio_wsf_timer_callback_candidate
        );
    if (open_cfw_cordio_wsf_freertos_timer_candidate == NULL) {
        /* The stock assertion path is terminal. */
        open_cfw_cordio_wsf_timer_fatal_candidate();
        return;
    }
    open_cfw_cordio_wsf_last_tick_candidate =
        open_cfw_cordio_wsf_tick_counter_get_candidate();
}

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

void open_cfw_cordio_wsf_timer_stop_candidate(
    struct open_cfw_cordio_wsf_timer *timer
)
{
    open_cfw_cordio_wsf_task_lock_candidate();
    open_cfw_cordio_wsf_timer_remove_candidate(timer);
    open_cfw_cordio_wsf_task_unlock_candidate();
}

void open_cfw_cordio_wsf_timer_update_candidate(uint32_t ticks)
{
    struct open_cfw_cordio_wsf_timer *current;

    open_cfw_cordio_wsf_task_lock_candidate();
    current = open_cfw_cordio_wsf_timer_queue_candidate.head;
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

uint32_t open_cfw_cordio_wsf_timer_next_expiration_candidate(
    bool *timer_running
)
{
    struct open_cfw_cordio_wsf_timer *head;
    uint32_t ticks;

    open_cfw_cordio_wsf_task_lock_candidate();
    head = open_cfw_cordio_wsf_timer_queue_candidate.head;
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

struct open_cfw_cordio_wsf_timer *
open_cfw_cordio_wsf_timer_service_expired_candidate(uint8_t task_id)
{
    struct open_cfw_cordio_wsf_timer *head;

    (void)task_id;
    open_cfw_cordio_wsf_task_lock_candidate();
    head = open_cfw_cordio_wsf_timer_queue_candidate.head;
    if ((head != NULL) && (head->ticks == 0U)) {
        open_cfw_cordio_wsf_queue_remove_candidate(
            &open_cfw_cordio_wsf_timer_queue_candidate,
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
        current_tick - open_cfw_cordio_wsf_last_tick_candidate;
    elapsed_wsf_ticks = elapsed_counter_ticks /
        OPEN_CFW_CORDIO_WSF_COUNTER_TICKS_PER_WSF_TICK;
    if (elapsed_wsf_ticks != 0U) {
        open_cfw_cordio_wsf_timer_update_candidate(elapsed_wsf_ticks);
        open_cfw_cordio_wsf_last_tick_candidate = current_tick;
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
        open_cfw_cordio_wsf_freertos_timer_candidate,
        OPEN_CFW_CORDIO_WSF_TIMER_CHANGE_PERIOD_COMMAND,
        period_ticks,
        0U,
        OPEN_CFW_CORDIO_WSF_TIMER_COMMAND_WAIT_TICKS
    );
    if (status != OPEN_CFW_CORDIO_WSF_TIMER_COMMAND_SUCCESS) {
        open_cfw_cordio_wsf_timer_command_failure_candidate();
        open_cfw_cordio_wsf_timer_fatal_candidate();
    }
}
