/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-routed clean-room ABI for the G2 Cordio/Ambiq FreeRTOS WSF
 * OS port.  The stock configuration has ten handlers and an 8-bit handler
 * event mask; it is not ABI-compatible with the selected public r20.05c
 * header configuration.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSF_OS_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSF_OS_CANDIDATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_wsf_queue_candidate.h"
#include "runtime_cordio_wsf_timer_candidate.h"

enum {
    OPEN_CFW_CORDIO_WSF_MAX_HANDLERS = 10U,
    OPEN_CFW_CORDIO_WSF_MSG_QUEUE_EVENT = 0x01U,
    OPEN_CFW_CORDIO_WSF_TIMER_EVENT = 0x02U,
    OPEN_CFW_CORDIO_WSF_HANDLER_EVENT = 0x04U
};

typedef void (*open_cfw_cordio_wsf_event_handler_candidate_t)(
    uint8_t event_mask,
    struct open_cfw_cordio_wsf_msg_header *message
);

struct open_cfw_cordio_wsf_os_task_candidate {
    open_cfw_cordio_wsf_event_handler_candidate_t
        handlers[OPEN_CFW_CORDIO_WSF_MAX_HANDLERS];
    uint8_t handler_event_masks[OPEN_CFW_CORDIO_WSF_MAX_HANDLERS];
    struct open_cfw_cordio_wsf_queue_candidate message_queue;
    uint8_t task_event_mask;
    uint8_t number_of_handlers;
};

extern uint8_t open_cfw_cordio_wsf_cs_nesting_candidate;
extern struct open_cfw_cordio_wsf_os_task_candidate
    open_cfw_cordio_wsf_os_task_candidate;
extern void *open_cfw_cordio_wsf_radio_event_group_candidate;

void open_cfw_cordio_wsf_interrupt_disable_candidate(void);
void open_cfw_cordio_wsf_interrupt_enable_candidate(void);
int open_cfw_cordio_wsf_port_is_inside_interrupt_candidate(void);
int open_cfw_cordio_wsf_event_group_set_bits_from_isr_candidate(
    void *event_group,
    uint32_t bits,
    int *higher_priority_task_woken
);
uint32_t open_cfw_cordio_wsf_event_group_set_bits_candidate(
    void *event_group,
    uint32_t bits
);
void open_cfw_cordio_wsf_pend_pendsv_candidate(void);
void open_cfw_cordio_wsf_yield_candidate(void);
void *open_cfw_cordio_wsf_event_group_create_candidate(void);
uint32_t open_cfw_cordio_wsf_event_group_wait_bits_candidate(
    void *event_group,
    uint32_t bits,
    bool clear_on_exit,
    bool wait_for_all,
    uint32_t wait_ticks
);
void *open_cfw_cordio_wsf_os_message_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
);
void open_cfw_cordio_wsf_os_message_free_candidate(void *message);

void open_cfw_cordio_wsf_cs_enter_candidate(void);
void open_cfw_cordio_wsf_cs_exit_candidate(void);
void open_cfw_cordio_wsf_set_os_specific_event_candidate(void);
void open_cfw_cordio_wsf_set_event_candidate(
    uint8_t handler_id,
    uint8_t event_mask
);
struct open_cfw_cordio_wsf_queue_candidate *
open_cfw_cordio_wsf_task_message_queue_candidate(uint8_t handler_id);
uint8_t open_cfw_cordio_wsf_os_set_next_handler_candidate(
    open_cfw_cordio_wsf_event_handler_candidate_t handler
);
bool open_cfw_cordio_wsf_os_ready_to_sleep_candidate(void);
void open_cfw_cordio_wsf_os_init_candidate(void);
void open_cfw_cordio_wsf_os_dispatcher_candidate(void);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    sizeof(open_cfw_cordio_wsf_event_handler_candidate_t) == 0x04U,
    "G2 WSF handler pointer size"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_os_task_candidate, handlers) == 0x00U,
    "G2 WSF OS handlers offset"
);
_Static_assert(
    sizeof(
        ((struct open_cfw_cordio_wsf_os_task_candidate *)0)
            ->handler_event_masks
    ) == 10U,
    "G2 WSF handler-event array size"
);
_Static_assert(
    offsetof(
        struct open_cfw_cordio_wsf_os_task_candidate,
        handler_event_masks
    ) == 0x28U,
    "G2 WSF OS handler-event offset"
);
_Static_assert(
    offsetof(
        struct open_cfw_cordio_wsf_os_task_candidate,
        message_queue
    ) == 0x34U,
    "G2 WSF OS message-queue offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_os_task_candidate, task_event_mask)
        == 0x3CU,
    "G2 WSF OS task-event offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_os_task_candidate, number_of_handlers)
        == 0x3DU,
    "G2 WSF OS handler-count offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_os_task_candidate) == 0x40U,
    "G2 WSF OS task size"
);
#endif

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSF_OS_CANDIDATE_H */
