/* SPDX-License-Identifier: MIT. Private Apollo bootloader queue-put ABI. */
#ifndef OPENCFW_BOOT_QUEUE_SEND_H
#define OPENCFW_BOOT_QUEUE_SEND_H
#include <stdint.h>

uint32_t opencfw_bl_kernel_queue_put_blocking(uint32_t *queue,
                                               const void *message,
                                               uint32_t timeout_ticks,
                                               uint32_t mode);
uint32_t opencfw_boot_queue_copy_in(uint32_t *queue, const void *message,
                                    uint32_t mode);

#endif
