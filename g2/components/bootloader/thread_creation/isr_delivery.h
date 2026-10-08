/* SPDX-License-Identifier: MIT. Reconstructed ARM32 ISR/deferred ABI. */
#ifndef OPENCFW_BOOT_ISR_DELIVERY_H
#define OPENCFW_BOOT_ISR_DELIVERY_H
#include <stdint.h>
uint32_t opencfw_bl_kernel_queue_put_from_isr(uint32_t *queue,const void *message,uint32_t *woken,uint32_t mode);
uint32_t opencfw_bl_kernel_queue_get_from_isr(uint32_t *queue,void *message,uint32_t *woken);
uint32_t opencfw_boot_queue_isr_task_count(void);
uint32_t opencfw_boot_isr_thread_notify(uint32_t *thread,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous,uint32_t *woken);
uint32_t opencfw_boot_pend_callback_isr(void (*callback)(uint32_t,uint32_t),uint32_t argument,uint32_t value,uint32_t *woken);
void opencfw_boot_event_flags_deferred(uint32_t argument,uint32_t flags);
uint32_t opencfw_bl_event_flags_set_isr(uint32_t *event,uint32_t flags,uint32_t *woken);
uint32_t opencfw_boot_kernel_queue_reset(uint32_t *queue,uint32_t is_new);
#endif
