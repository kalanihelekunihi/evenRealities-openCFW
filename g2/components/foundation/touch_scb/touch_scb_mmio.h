/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#ifndef OPENCFW_TOUCH_SCB_MMIO_H
#define OPENCFW_TOUCH_SCB_MMIO_H

#include "touch_scb.h"

/* Register contract transcribed from the authenticated decoded touch image:
 * Cy_SCB_ReadArrayNoCheck at runtime 0x9218, image [0x5f18,0x5f50), SHA-256
 * 07627776d2bc275029e974a40d0944d6b87502cfea118880b8d60d6c3fa97cc7.
 * The original instructions load RX_CTRL at +0x300 and TST mask 0x18; zero
 * selects byte stores, nonzero selects halfword stores. Both loops read a
 * 32-bit value at RX_FIFO_RD +0x340 once per element and store its low 8/16
 * bits. Cy_SCB_ReadArray separately reads RX_FIFO_STATUS +0x308 and masks
 * 0x1ff before calling the callee. Count units are FIFO elements; destination
 * byte advance is one or two per element. These facts describe the recovered
 * instruction sequence, not an independently measured electrical bus trace.
 */

#ifdef __cplusplus
extern "C" {
#endif

/* Bind volatile register callbacks. `scb_base` is supplied by the caller and
 * is passed as the SCB argument to the callback API; no peripheral address or
 * boot configuration is assumed. Returns TOUCH_SCB_INVALID_ARGUMENT for a
 * null io pointer, otherwise TOUCH_SCB_OK.
 */
touch_scb_result_t touch_scb_mmio_bind(touch_scb_io_t *io);

/* Raw callback-backed read. `scb_base` must be a nonzero, 4-byte-aligned SCB
 * live mapped register block base with non-overflowing offsets through +0x340, and
 * destination must satisfy the active width's alignment (1 or 2 bytes).
 * This keeps target-like behavior and has no capacity argument.
 */
uint32_t touch_scb_mmio_read_array(uintptr_t scb_base, void *destination,
                                   uint32_t requested);

/* Checked simulator/host adapter. Requires a live mapped SCB register block,
 * nonzero 4-byte-aligned base, and non-overflowing offsets through +0x340;
 * samples RX_CTRL to determine transfer width,
 * validates halfword alignment, then uses touch_scb_read_array_checked for
 * count/capacity validation before touching RX_FIFO_RD. Caller must serialize
 * SCB configuration so width is stable through this operation. */
touch_scb_result_t touch_scb_mmio_read_array_checked(uintptr_t scb_base,
                                                     void *destination,
                                                     size_t capacity_bytes,
                                                     uint32_t requested,
                                                     uint32_t *actual_out);

#ifdef __cplusplus
}
#endif

#endif
