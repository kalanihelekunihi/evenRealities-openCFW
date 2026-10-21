/* SPDX-License-Identifier: MIT. Reconstructed locked ARM32 mutex ABI. */
#ifndef OPENCFW_BOOT_MUTEX_KERNEL_H
#define OPENCFW_BOOT_MUTEX_KERNEL_H
#include <stdint.h>
uint32_t opencfw_bl_kernel_mutex_take_plain(uint32_t *queue,uint32_t ticks);
uint32_t opencfw_bl_kernel_mutex_take_tagged(uint32_t *queue,uint32_t ticks);
uint32_t opencfw_bl_kernel_mutex_give_tagged(uint32_t *queue);
uint32_t opencfw_boot_current_task(void);
uint32_t opencfw_boot_mutex_claim_current(void);
uint32_t opencfw_boot_mutex_inherit(uint32_t *owner);
void opencfw_boot_mutex_disinherit_timeout(uint32_t *owner,uint32_t waiting_priority);
uint32_t opencfw_boot_mutex_waiter_priority(uint32_t *queue);
#endif
