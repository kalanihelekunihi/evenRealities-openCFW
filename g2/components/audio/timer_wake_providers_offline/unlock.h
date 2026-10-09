/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TIMER_UNLOCK_H
#define OPENCFW_TIMER_UNLOCK_H
#include "../../foundation/freertos_queue/queue.h"
#include "../../foundation/freertos_ready/ready.h"
void audio_public_queue_unlock(Queue_t * const);
void audio_public_list_insert(List_t *,ListItem_t *);
uint32_t audio_port_mask_set(void);
void audio_port_mask_restore(uint32_t);
void stock_enter_critical(void);
void stock_exit_critical(void);
void stock_missed_yield(void);
#endif
