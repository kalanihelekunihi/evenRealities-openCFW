/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AUDIO_CACHE_HANDOFF_H
#define OPENCFW_AUDIO_CACHE_HANDOFF_H
#include <stdint.h>
#include "../cache_maintenance/cache_maintenance.h"
/* Stock-like methods assume mapped aligned handle/output words; no validation. */
uint32_t opencfw_i2s_selected_buffer(const volatile void *handle, uint32_t selector);
uint32_t opencfw_audio_rx_buffer_get(uint32_t *buffer, uint32_t *length);
/* New capacity policy, not an original firmware function. Missing/invalid
 * allocation information returns6 with no cache-register/barrier operation.
 * Supplied bounds do not prove allocation liveness or exclusive DMA ownership.
 * operation0=invalidate,1=clean+invalidate,2=clean. */
uint32_t opencfw_cache_checked(const volatile opencfw_cache_range_t *range,
                             uint32_t allocation_base, uint32_t allocation_size,
                             uint32_t operation);
/* New checked handoff: failure leaves outputs unchanged; success returns0. */
uint32_t opencfw_audio_rx_buffer_get_checked(uint32_t *buffer, uint32_t *length,
                                          uint32_t allocation_base, uint32_t allocation_size);
#endif
