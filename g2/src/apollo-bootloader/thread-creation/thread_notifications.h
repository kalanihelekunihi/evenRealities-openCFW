/* SPDX-License-Identifier: MIT. Exact single-slot kernel notification ABI. */
#ifndef OPENCFW_BOOT_THREAD_NOTIFICATIONS_H
#define OPENCFW_BOOT_THREAD_NOTIFICATIONS_H
#include <stdint.h>
uint32_t opencfw_boot_thread_notify_wait(uint32_t index,uint32_t clear_entry,uint32_t clear_exit,uint32_t *output,uint32_t ticks);
uint32_t opencfw_boot_thread_notify(uint32_t *thread,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous);
uint32_t opencfw_boot_thread_wait_result_take(void);
#endif
