/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#ifndef OPENCFW_TOUCH_SCB_TX_H
#define OPENCFW_TOUCH_SCB_TX_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Contract transcribed from authenticated touch bytes:
 * Cy_SCB_WriteArrayNoCheck at runtime 0x926e, decoded image [0x5f6e,0x5fa6),
 * SHA-256 ba8eabab79e5f3cf46e4b9b7bd76456a262ed1ff7d3780885a747f9eb6e1b434;
 * Cy_SCB_WriteArray at runtime 0x92a6, decoded image [0x5fa6,0x5fd6),
 * SHA-256 e3bd934582667c74ed28fa5a43ce49d2a70802d22b01b6f01ff19994fa474ce9.
 * FIFO depth is 16 when *(base+0)&0xc000 is zero, else 8; TX_FIFO_STATUS
 * at +0x208 uses low 9 bits as used count. Raw source behavior subtracts
 * `used` from depth with 32-bit wraparound. TX_CTRL at +0x200 mask 0x18
 * selects byte source elements when zero and halfword elements otherwise;
 * each is written as a 32-bit store to TX_FIFO_WR at +0x240. Counts are FIFO
 * elements, not bytes. This is instruction-derived register behavior, not a
 * physical bus trace.
 */

typedef enum {
    TOUCH_SCB_TX_OK = 0,
    TOUCH_SCB_TX_INVALID_ARGUMENT,
    TOUCH_SCB_TX_INSUFFICIENT_CAPACITY,
    TOUCH_SCB_TX_INVALID_ALIGNMENT,
    TOUCH_SCB_TX_INVALID_FIFO_STATUS
} touch_scb_tx_result_t;

/* Caller supplies a live mapped, nonzero 4-byte-aligned SCB register base.
 * Raw behavior
 * matches the wrapper's unsigned depth-used arithmetic, including underflow
 * when the used field exceeds the configured depth. Halfword mode requires
 * naturally aligned source memory. */
uint32_t touch_scb_mmio_write_array(uintptr_t scb_base, const void *source,
                                    uint32_t requested);

/* Checked adapter. Requires a live mapped base and checks that +0x240 cannot
 * overflow uintptr_t. Rejects used>depth before writing any FIFO entries, checks
 * source capacity and halfword alignment, and reports actual count on success.
 * The caller must serialize SCB reconfiguration during the operation. */
touch_scb_tx_result_t touch_scb_mmio_write_array_checked(
    uintptr_t scb_base, const void *source, size_t capacity_bytes,
    uint32_t requested, uint32_t *actual_out);

#ifdef __cplusplus
}
#endif

#endif
