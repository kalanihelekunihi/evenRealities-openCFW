/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_IOM_POWER_PREPARE_H
#define OPENCFW_IOM_POWER_PREPARE_H
#include <stdint.h>
/* Reconstruction of fixed power-operation2 path through55ca72 only.
 * Return0 means prepared for external power callbacks, not powered down.
 * Fields through0x89f must be mapped; retention is byte-truncated. */
uint32_t opencfw_iom_powerdown_prepare(void *,uint32_t retention);
uint32_t opencfw_iom_cq_pause(void *);
/* Release ordering only; ends before dynamic physical-power providers. */
uint32_t opencfw_iom_disable_then_prepare(void *,uint32_t retention);
#endif
