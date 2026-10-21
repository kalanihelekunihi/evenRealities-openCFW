/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#ifndef OPENCFW_TOUCH_SCB_FIFO_H
#define OPENCFW_TOUCH_SCB_FIFO_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Reconstructed checked form of Cy_SCB_SetRxFifoLevel, original runtime
 * 0x9316, decoded image [0x6016,0x6042), SHA-256
 * 1fdc6e20657ebf1efbbf7423c354904526f55af9f31d09ad5cd700d69ecdb993.
 * The original validates against the configured 8/16-element FIFO depth,
 * executes BKPT #1 for level >= depth, then changes only RX_FIFO_CTRL[7:0]
 * (the recovered trigger-level field). The association between that field
 * and IRQ firing semantics comes from upstream documentation; device-level
 * threshold/interrupt behavior has not been measured in this reconstruction.
 * This checked helper returns INVALID_LEVEL instead of executing BKPT.
 */
typedef enum {
    TOUCH_SCB_FIFO_OK = 0,
    TOUCH_SCB_FIFO_INVALID_ARGUMENT,
    TOUCH_SCB_FIFO_INVALID_LEVEL
} touch_scb_fifo_result_t;

/* Caller supplies a live, mapped, nonzero 4-byte-aligned SCB register base.
 * Level is measured in FIFO elements. No FIFO data is read or written.
 * Caller must serialize FIFO_CONFIG and RX_FIFO_CTRL changes across the
 * depth check and read-modify-write to avoid invalid validation/lost updates. */
touch_scb_fifo_result_t touch_scb_fifo_set_rx_level(uintptr_t scb_base,
                                                    uint32_t level);

#ifdef __cplusplus
}
#endif

#endif
