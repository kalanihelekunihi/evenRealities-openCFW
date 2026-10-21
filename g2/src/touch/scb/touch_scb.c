/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#include "touch_scb.h"

uint32_t touch_scb_read_array(const touch_scb_io_t *io, void *scb,
                              void *destination, uint32_t requested)
{
    const uint32_t available = io->read_rx_fifo_status(io->context, scb) & 0x1ffu;
    const uint32_t actual = requested < available ? requested : available;

    io->read_array_no_check(io->context, scb, destination, actual);
    return actual;
}

touch_scb_result_t touch_scb_read_array_checked(const touch_scb_io_t *io,
                                                void *scb,
                                                void *destination,
                                                size_t destination_capacity,
                                                uint8_t element_width,
                                                uint32_t requested,
                                                uint32_t *actual_out)
{
    uint32_t actual;
    size_t bytes_needed;

    if (io == NULL || io->read_rx_fifo_status == NULL ||
        io->read_array_no_check == NULL || scb == NULL || destination == NULL ||
        actual_out == NULL) {
        return TOUCH_SCB_INVALID_ARGUMENT;
    }
    if (element_width != 1u && element_width != 2u) {
        return TOUCH_SCB_INVALID_WIDTH;
    }

    /* The recovered wrapper clamps actual to at most 511 before multiplying. */
    {
        const uint32_t available =
            io->read_rx_fifo_status(io->context, scb) & 0x1ffu;
        actual = requested < available ? requested : available;
    }
    bytes_needed = (size_t)actual * (size_t)element_width;
    if (bytes_needed > destination_capacity) {
        return TOUCH_SCB_INSUFFICIENT_CAPACITY;
    }

    io->read_array_no_check(io->context, scb, destination, actual);
    *actual_out = actual;
    return TOUCH_SCB_OK;
}
