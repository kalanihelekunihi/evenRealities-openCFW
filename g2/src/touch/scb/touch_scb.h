/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 *
 * Callback boundary for the recovered PSoC SCB receive-array wrapper.
 * This interface intentionally does not encode a target MMIO address.
 */
#ifndef OPENCFW_TOUCH_SCB_H
#define OPENCFW_TOUCH_SCB_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t (*touch_scb_read_status_fn)(void *context, void *scb);
typedef void (*touch_scb_read_fifo_fn)(void *context, void *scb,
                                       void *destination, uint32_t count);

typedef struct {
    void *context;
    touch_scb_read_status_fn read_rx_fifo_status;
    touch_scb_read_fifo_fn read_array_no_check;
} touch_scb_io_t;

/* Firmware-shaped behavior: available = status & 0x1ff; actual = min(requested,
 * available); invoke read_array_no_check exactly once, including actual == 0;
 * return actual. Callbacks are required and unchecked, like the target call
 * boundary. Use touch_scb_read_array_checked for host/adaptor validation.
 */
uint32_t touch_scb_read_array(const touch_scb_io_t *io, void *scb,
                              void *destination, uint32_t requested);

typedef enum {
    TOUCH_SCB_OK = 0,
    TOUCH_SCB_INVALID_ARGUMENT,
    TOUCH_SCB_INVALID_WIDTH,
    TOUCH_SCB_INSUFFICIENT_CAPACITY
} touch_scb_result_t;

/* Checked adapter. Validates callbacks and output/capacity, permits only the
 * PDL's byte/halfword widths (1 or 2), and reports the actual count on success.
 * Capacity is measured in bytes. These checks are adapter behavior; the
 * firmware wrapper does not receive a capacity argument.
 */
touch_scb_result_t touch_scb_read_array_checked(const touch_scb_io_t *io,
                                                void *scb,
                                                void *destination,
                                                size_t destination_capacity,
                                                uint8_t element_width,
                                                uint32_t requested,
                                                uint32_t *actual_out);

#ifdef __cplusplus
}
#endif

#endif
