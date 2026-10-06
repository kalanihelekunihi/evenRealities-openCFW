/* SPDX-License-Identifier: MIT. Private platform mode-control entry points. */
#ifndef OPENCFW_BOOT_PLATFORM_CONTROL_RUNTIME_H
#define OPENCFW_BOOT_PLATFORM_CONTROL_RUNTIME_H

#include <stdint.h>

uint32_t opencfw_boot_control_mode_one(uint32_t mode);
uint32_t opencfw_boot_control_mode_two(uint32_t mode);
uint32_t opencfw_boot_control_cleanup(void);
uint32_t opencfw_boot_control_finish(void);
uint32_t opencfw_boot_control_power_apply(uint32_t *object,
                                          uint32_t operation,
                                          uint32_t enable);
uint32_t opencfw_boot_control_transition(uint32_t mode);

#endif
