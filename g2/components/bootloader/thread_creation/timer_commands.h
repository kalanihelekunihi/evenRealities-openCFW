/* SPDX-License-Identifier: MIT. Private bootloader timer service ABI. */
#ifndef OPENCFW_BOOT_TIMER_COMMANDS_H
#define OPENCFW_BOOT_TIMER_COMMANDS_H

#include <stdint.h>

void opencfw_bl_timer_process_commands(void);
uint32_t opencfw_boot_timer_insert(uint32_t *timer, uint32_t deadline,
                                   uint32_t now, uint32_t delta);
void opencfw_boot_timer_reload(uint32_t *timer, uint32_t deadline,
                              uint32_t now);

#endif
