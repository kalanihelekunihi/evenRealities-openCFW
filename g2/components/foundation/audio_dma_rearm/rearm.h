/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AUDIO_DMA_REARM_H
#define OPENCFW_AUDIO_DMA_REARM_H
#include <stdint.h>
/* Instruction reconstructions. Handles must be mapped/aligned and contain a
 * mapped peripheral instance. These routines establish no buffer lifetime. */
uint32_t opencfw_i2s_dma_error(const volatile void *handle, uint32_t direction);
uint32_t opencfw_i2s_ipb_service(const volatile void *handle);
uint32_t opencfw_i2s_interrupt_service(volatile void *handle, uint32_t status);
uint32_t opencfw_i2s_interrupt_status(const volatile void *handle, uint32_t *status, uint32_t enabled_only);
uint32_t opencfw_i2s_interrupt_clear(const volatile void *handle, uint32_t status);
/* Bounded ISR prefix through service, before actual notification. Returns the
 * captured enabled status; bit4 means stock would call 0x53c6b2 even if service
 * returned9. This is a new seam, not a full ISR/notification implementation. */
uint32_t opencfw_audio_i2s_irq_prefix(void);
#endif
