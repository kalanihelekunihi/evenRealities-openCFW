/* SPDX-License-Identifier: MIT. Private bootloader ARM32 receive/timeout ABI. */
#ifndef OPENCFW_BOOT_QUEUE_RECEIVE_H
#define OPENCFW_BOOT_QUEUE_RECEIVE_H
#include <stdint.h>
void opencfw_boot_timeout_capture(uint32_t state[2]);
uint32_t opencfw_boot_timeout_check(uint32_t state[2],uint32_t *remaining);
void opencfw_boot_wait_list_sorted(uint32_t *list,uint32_t ticks);
uint32_t opencfw_boot_queue_empty(uint32_t *queue);
void opencfw_boot_queue_copy_out(uint32_t *queue,void *message);
uint32_t opencfw_bl_kernel_queue_get_blocking(uint32_t *queue,void *message,uint32_t timeout);
uintptr_t opencfw_bl_kernel_queue_create_dynamic(uint32_t count,uint32_t item_size,uint32_t type);
#endif
