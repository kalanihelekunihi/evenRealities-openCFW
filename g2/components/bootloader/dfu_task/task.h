/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DFU_TASK_H
#define OPENCFW_BOOT_DFU_TASK_H
#include <stdint.h>
#define OPENCFW_BOOT_APPLICATION_BASE 0x00438000u
#define OPENCFW_BOOT_IMAGE_INSTALL_FLAG (1u<<26)
/* queue message is 40 bytes; first word is dispatch command/address. */
typedef struct { uint32_t command; uint32_t remaining[9]; } opencfw_boot_dfu_message;
void opencfw_boot_dfu_task(void);
uint32_t opencfw_boot_dfu_queue_get(uint32_t,void *,uint32_t,uint32_t);
void opencfw_boot_dfu_runtime_enable(void);
void opencfw_boot_dfu_error_transaction(void);
void opencfw_boot_dfu_log(uint32_t,uint32_t);
#endif
