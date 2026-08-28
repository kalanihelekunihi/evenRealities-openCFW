/*
 * SPDX-License-Identifier: MIT
 *
 * Production-routed clean-room behavioral reconstruction of the complete
 * G2 Cordio/Ambiq FreeRTOS WSF OS module.  The restricted upstream source is
 * used only as an authenticated provenance/behavior oracle and is not copied.
 */

#include "runtime_cordio_wsf_os_candidate.h"

#ifdef OPEN_CFW_WSF_OS_PRODUCTION
#include "runtime_cordio_wsf_msg_candidate.h"
#define OPEN_CFW_WSF_OS_MESSAGE_DEQUEUE \
    open_cfw_cordio_wsf_message_dequeue_candidate
#define OPEN_CFW_WSF_OS_MESSAGE_FREE open_cfw_cordio_wsf_message_free_candidate
#else
#define OPEN_CFW_WSF_OS_MESSAGE_DEQUEUE \
    open_cfw_cordio_wsf_os_message_dequeue_candidate
#define OPEN_CFW_WSF_OS_MESSAGE_FREE \
    open_cfw_cordio_wsf_os_message_free_candidate
#endif

#if !defined(OPEN_CFW_WSF_OS_CS_ENTER_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_CS_EXIT_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_TASK_LOCK_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_TASK_UNLOCK_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_SET_OS_EVENT_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_SET_EVENT_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_TASK_READY_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_TASK_QUEUE_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_NEXT_HANDLER_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_READY_SLEEP_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_INIT_ONLY) && \
    !defined(OPEN_CFW_WSF_OS_DISPATCHER_ONLY)
#define OPEN_CFW_WSF_OS_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_WSF_OS_PRODUCTION
#define OPEN_CFW_WSF_CS_NESTING (*(uint8_t *)0x20075045U)
#define OPEN_CFW_WSF_RADIO_EVENT_GROUP (*(void **)0x20074EF0U)
#define OPEN_CFW_WSF_OS_TASK \
    (*(struct open_cfw_cordio_wsf_os_task_candidate *)0x20073230U)
#else
#define OPEN_CFW_WSF_CS_NESTING open_cfw_cordio_wsf_cs_nesting_candidate
#define OPEN_CFW_WSF_RADIO_EVENT_GROUP \
    open_cfw_cordio_wsf_radio_event_group_candidate
#define OPEN_CFW_WSF_OS_TASK open_cfw_cordio_wsf_os_task_candidate
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_CS_ENTER_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_cs_enter_candidate(void)
{
    if (OPEN_CFW_WSF_CS_NESTING == 0U) {
#ifdef OPEN_CFW_WSF_OS_PRODUCTION
        __asm__ volatile("cpsid i" ::: "memory");
#else
        open_cfw_cordio_wsf_interrupt_disable_candidate();
#endif
    }
    OPEN_CFW_WSF_CS_NESTING++;
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_CS_EXIT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_cs_exit_candidate(void)
{
    OPEN_CFW_WSF_CS_NESTING--;
    if (OPEN_CFW_WSF_CS_NESTING == 0U) {
#ifdef OPEN_CFW_WSF_OS_PRODUCTION
        __asm__ volatile("cpsie i" ::: "memory");
#else
        open_cfw_cordio_wsf_interrupt_enable_candidate();
#endif
    }
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_TASK_LOCK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_task_lock_candidate(void)
{
    open_cfw_cordio_wsf_cs_enter_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_TASK_UNLOCK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_task_unlock_candidate(void)
{
    open_cfw_cordio_wsf_cs_exit_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_SET_OS_EVENT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_set_os_specific_event_candidate(void)
{
    int higher_priority_task_woken;
    int result;

    if (OPEN_CFW_WSF_RADIO_EVENT_GROUP == NULL) {
        return;
    }

    if (open_cfw_cordio_wsf_port_is_inside_interrupt_candidate() == 1) {
        higher_priority_task_woken = 0;
        result = open_cfw_cordio_wsf_event_group_set_bits_from_isr_candidate(
            OPEN_CFW_WSF_RADIO_EVENT_GROUP,
            1U,
            &higher_priority_task_woken
        );
        if ((result != 0) && (higher_priority_task_woken != 0)) {
#ifdef OPEN_CFW_WSF_OS_PRODUCTION
            *(volatile uint32_t *)0xE000ED04U = 0x10000000U;
#else
            open_cfw_cordio_wsf_pend_pendsv_candidate();
#endif
        }
    } else {
        if (open_cfw_cordio_wsf_event_group_set_bits_candidate(
                OPEN_CFW_WSF_RADIO_EVENT_GROUP,
                1U
            ) != 0U) {
            open_cfw_cordio_wsf_yield_candidate();
        }
    }
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_SET_EVENT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_set_event_candidate(
    uint8_t handler_id,
    uint8_t event_mask
)
{
    uint8_t index = handler_id & 0x0FU;

    open_cfw_cordio_wsf_cs_enter_candidate();
    OPEN_CFW_WSF_OS_TASK.handler_event_masks[index] |=
        event_mask;
    OPEN_CFW_WSF_OS_TASK.task_event_mask |=
        OPEN_CFW_CORDIO_WSF_HANDLER_EVENT;
    open_cfw_cordio_wsf_cs_exit_candidate();
    open_cfw_cordio_wsf_set_os_specific_event_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_TASK_READY_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_task_set_ready_candidate(
    uint8_t handler_id,
    uint8_t task_event
)
{
    (void)handler_id;
    open_cfw_cordio_wsf_cs_enter_candidate();
    OPEN_CFW_WSF_OS_TASK.task_event_mask |= task_event;
    open_cfw_cordio_wsf_cs_exit_candidate();
    open_cfw_cordio_wsf_set_os_specific_event_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_TASK_QUEUE_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_wsf_queue_candidate *
open_cfw_cordio_wsf_task_message_queue_candidate(uint8_t handler_id)
{
    (void)handler_id;
    return &OPEN_CFW_WSF_OS_TASK.message_queue;
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_NEXT_HANDLER_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_wsf_os_set_next_handler_candidate(
    open_cfw_cordio_wsf_event_handler_candidate_t handler
)
{
    uint8_t handler_id =
        OPEN_CFW_WSF_OS_TASK.number_of_handlers++;
    OPEN_CFW_WSF_OS_TASK.handlers[handler_id] = handler;
    return handler_id;
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_READY_SLEEP_ONLY)
__attribute__((used, noinline))
bool open_cfw_cordio_wsf_os_ready_to_sleep_candidate(void)
{
    return OPEN_CFW_WSF_OS_TASK.task_event_mask == 0U;
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_INIT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_os_init_candidate(void)
{
    size_t index;
    uint8_t *bytes = (uint8_t *)&OPEN_CFW_WSF_OS_TASK;

    for (index = 0; index < sizeof(OPEN_CFW_WSF_OS_TASK); ++index) {
        bytes[index] = 0U;
    }
    if (OPEN_CFW_WSF_RADIO_EVENT_GROUP == NULL) {
        OPEN_CFW_WSF_RADIO_EVENT_GROUP =
            open_cfw_cordio_wsf_event_group_create_candidate();
    }
}
#endif

#if defined(OPEN_CFW_WSF_OS_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_OS_DISPATCHER_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_os_dispatcher_candidate(void)
{
    struct open_cfw_cordio_wsf_timer *timer;
    void *message;
    uint8_t event_mask;
    uint8_t task_event_mask;
    uint8_t handler_id;
    uint8_t index;

    open_cfw_cordio_wsf_timer_update_ticks_candidate();
    while (OPEN_CFW_WSF_OS_TASK.task_event_mask != 0U) {
        open_cfw_cordio_wsf_cs_enter_candidate();
        task_event_mask =
            OPEN_CFW_WSF_OS_TASK.task_event_mask;
        OPEN_CFW_WSF_OS_TASK.task_event_mask = 0U;
        open_cfw_cordio_wsf_cs_exit_candidate();

        if ((task_event_mask & OPEN_CFW_CORDIO_WSF_MSG_QUEUE_EVENT) != 0U) {
            while ((message = OPEN_CFW_WSF_OS_MESSAGE_DEQUEUE(
                        &OPEN_CFW_WSF_OS_TASK.message_queue,
                        &handler_id
                    )) != NULL) {
                OPEN_CFW_WSF_OS_TASK.handlers[handler_id](
                    0U,
                    (struct open_cfw_cordio_wsf_msg_header *)message
                );
                OPEN_CFW_WSF_OS_MESSAGE_FREE(message);
            }
        }

        if ((task_event_mask & OPEN_CFW_CORDIO_WSF_TIMER_EVENT) != 0U) {
            while ((timer =
                        open_cfw_cordio_wsf_timer_service_expired_candidate(0U)
                    ) != NULL) {
                OPEN_CFW_WSF_OS_TASK.handlers[
                    timer->handler_id
                ](0U, &timer->msg);
            }
        }

        if ((task_event_mask & OPEN_CFW_CORDIO_WSF_HANDLER_EVENT) != 0U) {
            for (index = 0U; index < OPEN_CFW_CORDIO_WSF_MAX_HANDLERS; ++index) {
                if ((OPEN_CFW_WSF_OS_TASK
                         .handler_event_masks[index] != 0U)
                    && (OPEN_CFW_WSF_OS_TASK.handlers[index]
                        != NULL)) {
                    open_cfw_cordio_wsf_cs_enter_candidate();
                    event_mask = OPEN_CFW_WSF_OS_TASK
                        .handler_event_masks[index];
                    OPEN_CFW_WSF_OS_TASK
                        .handler_event_masks[index] = 0U;
                    open_cfw_cordio_wsf_cs_exit_candidate();
                    OPEN_CFW_WSF_OS_TASK.handlers[index](
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
            OPEN_CFW_WSF_RADIO_EVENT_GROUP,
            1U,
            true,
            false,
            UINT32_MAX
        );
    }
}
#endif
