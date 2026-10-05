/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AMBIQ_MSPI_INTERRUPTS_H
#define OPENCFW_AMBIQ_MSPI_INTERRUPTS_H
#include <stdbool.h>
#include <stdint.h>
/* Reused BSD-3-Clause upstream functions, not a complete HAL driver. Caller
 * supplies a readable aligned live HAL handle whose initial eight bytes are
 * prefix and module. Prefix bits0:23=0xbebebe, bit24=initialized; other bits
 * do not affect validation. Module must be0..2 with mapped powered registers.
 * Caller serializes handle/configuration and INTEN RMW against other writers.
 * Output status pointer must be writable/aligned for valid handles. Upstream
 * bodies do not validate module range or output pointers. Errors return2 and
 * do not touch MMIO; success returns0. INTCLR is a W1C write followed by an
 * INTSTAT volatile read; register timing/interrupt firing is unverified. */
uint32_t am_hal_mspi_interrupt_enable(void *handle,uint32_t mask);
uint32_t am_hal_mspi_interrupt_disable(void *handle,uint32_t mask);
uint32_t am_hal_mspi_interrupt_status_get(void *handle,uint32_t *status,bool enabled_only);
uint32_t am_hal_mspi_interrupt_clear(void *handle,uint32_t mask);
/* Lifecycle calls require the readable/writable sparse stock view through
 * offset+0x8cc and valid linked CQ/delay providers. Disable refuses pending HP
 * or CQ work when enabled, propagates CQ-disable failure, then clears enable.
 * Deinitialize preserves upstream behavior: it DISCARDS disable errors and
 * clears init/module. It is not a safe quiesce/drain guarantee. Callers must
 * serialize lifecycle and pending-count changes; no ownership reclamation is
 * authorized merely by its successful return. */
uint32_t am_hal_mspi_disable(void *handle);
uint32_t am_hal_mspi_deinitialize(void *handle);
#endif
