/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_MANAGER_TASK_H
#define OPENCFW_BOOTLOADER_MANAGER_TASK_H
#include <stdint.h>
/* MRAM word lies outside the locked bootloader artifact; its value is external. */
uint32_t opencfw_boot_manager_needs_update(void);
void opencfw_boot_manager_task(void *argument);
void opencfw_boot_manager_flags_noop(uint32_t flags);
void opencfw_boot_manager_setup_noop(void);
void opencfw_provider_42e254(void);
void opencfw_provider_42e278(void);
void opencfw_provider_42e2ea(void);
void opencfw_boot_manager_callback_dispatch(void);
void opencfw_boot_manager_signal_wait(uintptr_t thread,uint32_t bit);
#endif
