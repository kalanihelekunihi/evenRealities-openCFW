/*
 * SPDX-License-Identifier: MIT
 *
 * Production-routed clean-room ABI for the recovered G2 Cordio/Ambiq
 * FreeRTOS timer helpers.  This intentionally does not include the public
 * Packetcraft wsf_timer.h: the stock G2 field order differs from r20.05c.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSF_TIMER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSF_TIMER_CANDIDATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_wsf_queue_candidate.h"

struct open_cfw_cordio_wsf_msg_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_cordio_wsf_timer {
    struct open_cfw_cordio_wsf_timer *next;
    uint32_t ticks;
    struct open_cfw_cordio_wsf_msg_header msg;
    uint8_t handler_id;
    uint8_t is_started;
};

extern struct open_cfw_cordio_wsf_queue_candidate
    open_cfw_cordio_wsf_timer_queue_candidate;
extern void *open_cfw_cordio_wsf_freertos_timer_candidate;
extern uint32_t open_cfw_cordio_wsf_last_tick_candidate;

void open_cfw_cordio_wsf_task_lock_candidate(void);
void open_cfw_cordio_wsf_task_unlock_candidate(void);
void open_cfw_cordio_wsf_task_set_ready_candidate(
    uint8_t handler_id,
    uint8_t event_mask
);
uint32_t open_cfw_cordio_wsf_tick_counter_get_candidate(void);
void *open_cfw_cordio_wsf_timer_create_candidate(
    const char *name,
    uint32_t period_ticks,
    bool auto_reload,
    void *timer_id,
    void (*callback)(void *timer)
);
int open_cfw_cordio_wsf_timer_command_candidate(
    void *timer,
    uint32_t command,
    uint32_t value,
    uint32_t reserved,
    uint32_t wait_ticks
);
void open_cfw_cordio_wsf_timer_command_failure_candidate(void);
void open_cfw_cordio_wsf_timer_fatal_candidate(void);

void open_cfw_cordio_wsf_timer_remove_candidate(
    struct open_cfw_cordio_wsf_timer *timer
);
void open_cfw_cordio_wsf_timer_insert_candidate(
    struct open_cfw_cordio_wsf_timer *timer,
    uint32_t ticks
);
void open_cfw_cordio_wsf_timer_callback_candidate(void *timer);
void open_cfw_cordio_wsf_timer_init_candidate(void);
void open_cfw_cordio_wsf_timer_start_sec_candidate(
    struct open_cfw_cordio_wsf_timer *timer,
    uint32_t seconds
);
void open_cfw_cordio_wsf_timer_start_ms_candidate(
    struct open_cfw_cordio_wsf_timer *timer,
    uint32_t milliseconds
);
void open_cfw_cordio_wsf_timer_stop_candidate(
    struct open_cfw_cordio_wsf_timer *timer
);
void open_cfw_cordio_wsf_timer_update_candidate(uint32_t ticks);
uint32_t open_cfw_cordio_wsf_timer_next_expiration_candidate(
    bool *timer_running
);
struct open_cfw_cordio_wsf_timer *
open_cfw_cordio_wsf_timer_service_expired_candidate(uint8_t task_id);
void open_cfw_cordio_wsf_timer_update_ticks_candidate(void);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_msg_header, param) == 0x00U,
    "G2 WSF message parameter offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_msg_header, event) == 0x02U,
    "G2 WSF message event offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_msg_header, status) == 0x03U,
    "G2 WSF message status offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_msg_header) == 0x04U,
    "G2 WSF message header size"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_timer, next) == 0x00U,
    "G2 WSF timer next offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_timer, ticks) == 0x04U,
    "G2 WSF timer ticks offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_timer, msg) == 0x08U,
    "G2 WSF timer message offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_timer, handler_id) == 0x0CU,
    "G2 WSF timer handler offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_timer, is_started) == 0x0DU,
    "G2 WSF timer started offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_timer) == 0x10U,
    "G2 WSF timer size"
);
#endif

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSF_TIMER_CANDIDATE_H */
