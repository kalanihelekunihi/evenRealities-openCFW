/* SPDX-License-Identifier: MIT. Reconstructed source for stock 0x41b954. */
#ifndef OPENCFW_BOOT_PLATFORM_CONTROL_RUNTIME_TRANSITION_H
#define OPENCFW_BOOT_PLATFORM_CONTROL_RUNTIME_TRANSITION_H

#include <stdint.h>

uint64_t opencfw_boot_control_transition(uint32_t mode);
uint64_t opencfw_boot_control_transition_core(uint32_t mode,
                                              uint32_t ambient_r1);

#endif
