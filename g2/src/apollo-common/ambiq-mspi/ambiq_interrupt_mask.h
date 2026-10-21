/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AMBIQ_INTERRUPT_MASK_H
#define OPENCFW_AMBIQ_INTERRUPT_MASK_H
#include <stdint.h>
/* Available in the real-critical ARM simulator profile. Privileged caller:
 * return old PRIMASK (0/1), then mask configurable interrupts. Caller must
 * restore that saved mask at its matching exit; no scheduler lock, NMI masking
 * or wall-clock contract. */
uint32_t am_hal_interrupt_master_disable(void);
#endif
