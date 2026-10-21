/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DFU_CONTEXT_H
#define OPENCFW_BOOT_DFU_CONTEXT_H
#include "task.h"
void opencfw_boot_dfu_queue_init(void);
void opencfw_boot_dfu_thread_init(void);
void opencfw_boot_dfu_thread_deinit(void);
uint32_t opencfw_boot_dfu_send(const opencfw_boot_dfu_message *);
void opencfw_boot_dfu_dispatch(uint32_t);
void opencfw_boot_dfu_orchestrator(void);
#endif
