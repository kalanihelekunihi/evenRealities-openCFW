/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room behavioral reconstruction of the complete
 * G2 Cordio/Ambiq FreeRTOS WSF OS module.  The restricted upstream source is
 * used only as an authenticated provenance/behavior oracle and is not copied.
 */

#include "runtime_cordio_wsf_os_candidate.h"

void open_cfw_cordio_wsf_cs_enter_candidate(void)
{
    if (open_cfw_cordio_wsf_cs_nesting_candidate == 0U) {
        open_cfw_cordio_wsf_interrupt_disable_candidate();
    }
    open_cfw_cordio_wsf_cs_nesting_candidate++;
}

void open_cfw_cordio_wsf_cs_exit_candidate(void)
{
    open_cfw_cordio_wsf_cs_nesting_candidate--;
    if (open_cfw_cordio_wsf_cs_nesting_candidate == 0U) {
        open_cfw_cordio_wsf_interrupt_enable_candidate();
    }
}

void open_cfw_cordio_wsf_task_lock_candidate(void)
{
    open_cfw_cordio_wsf_cs_enter_candidate();
}

void open_cfw_cordio_wsf_task_unlock_candidate(void)
{
    open_cfw_cordio_wsf_cs_exit_candidate();
}

void open_cfw_cordio_wsf_set_os_specific_event_candidate(void)
{
    int higher_priority_task_woken;
    int result;

    if (open_cfw_cordio_wsf_radio_event_group_candidate == NULL) {
        return;
    }

    if (open_cfw_cordio_wsf_port_is_inside_interrupt_candidate() == 1) {
        higher_priority_task_woken = 0;
        result = open_cfw_cordio_wsf_event_group_set_bits_from_isr_candidate(
            open_cfw_cordio_wsf_radio_event_group_candidate,
            1U,
            &higher_priority_task_woken
        );
        if ((result != 0) && (higher_priority_task_woken != 0)) {
            open_cfw_cordio_wsf_pend_pendsv_candidate();
        }
    } else {
        if (open_cfw_cordio_wsf_event_group_set_bits_candidate(
                open_cfw_cordio_wsf_radio_event_group_candidate,
                1U
            ) != 0U) {
            open_cfw_cordio_wsf_yield_candidate();
        }
    }
}

void open_cfw_cordio_wsf_set_event_candidate(
    uint8_t handler_id,
    uint8_t event_mask
)
{
    uint8_t index = handler_id & 0x0FU;

    open_cfw_cordio_wsf_cs_enter_candidate();
    open_cfw_cordio_wsf_os_task_candidate.handler_event_masks[index] |=
        event_mask;
    open_cfw_cordio_wsf_os_task_candidate.task_event_mask |=
        OPEN_CFW_CORDIO_WSF_HANDLER_EVENT;
    open_cfw_cordio_wsf_cs_exit_candidate();
    open_cfw_cordio_wsf_set_os_specific_event_candidate();
}

void open_cfw_cordio_wsf_task_set_ready_candidate(
    uint8_t handler_id,
    uint8_t task_event
)
{
    (void)handler_id;
    open_cfw_cordio_wsf_cs_enter_candidate();
    open_cfw_cordio_wsf_os_task_candidate.task_event_mask |= task_event;
    open_cfw_cordio_wsf_cs_exit_candidate();
    open_cfw_cordio_wsf_set_os_specific_event_candidate();
}

struct open_cfw_cordio_wsf_queue_candidate *
open_cfw_cordio_wsf_task_message_queue_candidate(uint8_t handler_id)
{
    (void)handler_id;
    return &open_cfw_cordio_wsf_os_task_candidate.message_queue;
}

uint8_t open_cfw_cordio_wsf_os_set_next_handler_candidate(
    open_cfw_cordio_wsf_event_handler_candidate_t handler
)
{
    uint8_t handler_id =
        open_cfw_cordio_wsf_os_task_candidate.number_of_handlers++;
    open_cfw_cordio_wsf_os_task_candidate.handlers[handler_id] = handler;
    return handler_id;
}

bool open_cfw_cordio_wsf_os_ready_to_sleep_candidate(void)
{
    return open_cfw_cordio_wsf_os_task_candidate.task_event_mask == 0U;
}

void open_cfw_cordio_wsf_os_init_candidate(void)
{
    size_t index;
    uint8_t *bytes = (uint8_t *)&open_cfw_cordio_wsf_os_task_candidate;

    for (index = 0; index < sizeof(open_cfw_cordio_wsf_os_task_candidate); ++index) {
        bytes[index] = 0U;
    }
    if (open_cfw_cordio_wsf_radio_event_group_candidate == NULL) {
        open_cfw_cordio_wsf_radio_event_group_candidate =
            open_cfw_cordio_wsf_event_group_create_candidate();
    }
}

void open_cfw_cordio_wsf_os_dispatcher_candidate(void)
{
    struct open_cfw_cordio_wsf_timer *timer;
    void *message;
    uint8_t event_mask;
    uint8_t task_event_mask;
    uint8_t handler_id;
    uint8_t index;

    open_cfw_cordio_wsf_timer_update_ticks_candidate();
    while (open_cfw_cordio_wsf_os_task_candidate.task_event_mask != 0U) {
        open_cfw_cordio_wsf_cs_enter_candidate();
        task_event_mask =
            open_cfw_cordio_wsf_os_task_candidate.task_event_mask;
        open_cfw_cordio_wsf_os_task_candidate.task_event_mask = 0U;
        open_cfw_cordio_wsf_cs_exit_candidate();

        if ((task_event_mask & OPEN_CFW_CORDIO_WSF_MSG_QUEUE_EVENT) != 0U) {
            while ((message = open_cfw_cordio_wsf_os_message_dequeue_candidate(
                        &open_cfw_cordio_wsf_os_task_candidate.message_queue,
                        &handler_id
                    )) != NULL) {
                open_cfw_cordio_wsf_os_task_candidate.handlers[handler_id](
                    0U,
                    (struct open_cfw_cordio_wsf_msg_header *)message
                );
                open_cfw_cordio_wsf_os_message_free_candidate(message);
            }
        }

        if ((task_event_mask & OPEN_CFW_CORDIO_WSF_TIMER_EVENT) != 0U) {
            while ((timer =
                        open_cfw_cordio_wsf_timer_service_expired_candidate(0U)
                    ) != NULL) {
                open_cfw_cordio_wsf_os_task_candidate.handlers[
                    timer->handler_id
                ](0U, &timer->msg);
            }
        }

        if ((task_event_mask & OPEN_CFW_CORDIO_WSF_HANDLER_EVENT) != 0U) {
            for (index = 0U; index < OPEN_CFW_CORDIO_WSF_MAX_HANDLERS; ++index) {
                if ((open_cfw_cordio_wsf_os_task_candidate
                         .handler_event_masks[index] != 0U)
                    && (open_cfw_cordio_wsf_os_task_candidate.handlers[index]
                        != NULL)) {
                    open_cfw_cordio_wsf_cs_enter_candidate();
                    event_mask = open_cfw_cordio_wsf_os_task_candidate
                        .handler_event_masks[index];
                    open_cfw_cordio_wsf_os_task_candidate
                        .handler_event_masks[index] = 0U;
                    open_cfw_cordio_wsf_cs_exit_candidate();
                    open_cfw_cordio_wsf_os_task_candidate.handlers[index](
                        event_mask,
                        NULL
                    );
                }
            }
        }
    }

    open_cfw_cordio_wsf_timer_update_ticks_candidate();
    if (open_cfw_cordio_wsf_os_ready_to_sleep_candidate()) {
        (void)open_cfw_cordio_wsf_event_group_wait_bits_candidate(
            open_cfw_cordio_wsf_radio_event_group_candidate,
            1U,
            true,
            false,
            UINT32_MAX
        );
    }
}
