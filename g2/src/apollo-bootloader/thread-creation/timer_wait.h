/* SPDX-License-Identifier: MIT. Private bootloader ARM32 scheduler interface. */
#ifndef OPENCFW_BOOT_TIMER_WAIT_H
#define OPENCFW_BOOT_TIMER_WAIT_H
#include <stdint.h>
void opencfw_boot_list_insert_sorted(uint32_t *list,uint32_t *item);
uint32_t opencfw_boot_list_unlink(uint32_t *item);
void opencfw_boot_task_block(uint32_t ticks,uint32_t suspend_indefinitely);
void opencfw_boot_wait_list_append(uint32_t *list,uint32_t ticks,uint32_t indefinite);
void opencfw_boot_timer_queue_unlock(uint32_t *queue);
void opencfw_boot_timer_queue_wait(uint32_t *queue,uint32_t ticks,uint32_t indefinite);
uint32_t opencfw_boot_tick_get(void);
uint32_t opencfw_boot_timer_next_expiry(uint32_t *empty);
uint32_t opencfw_boot_timer_sample_time(uint32_t *wrapped);
void opencfw_boot_timer_wait_expiry(uint32_t expiry,uint32_t empty);
void opencfw_boot_timer_task(void *argument);
#endif
