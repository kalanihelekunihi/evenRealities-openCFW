/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#include "touch_scb_mmio.h"

#include <stdint.h>

enum {
    RX_CTRL_OFFSET = 0x300u,
    RX_FIFO_STATUS_OFFSET = 0x308u,
    RX_FIFO_RD_OFFSET = 0x340u,
    RX_CTRL_WIDTH_MASK = 0x18u
};

typedef struct {
    uint8_t sampled_width;
} touch_scb_mmio_context_t;

static volatile uint32_t *register32(void *scb, uintptr_t offset)
{
    return (volatile uint32_t *)((uintptr_t)scb + offset);
}

static uint32_t mmio_read_rx_fifo_status(void *context, void *scb)
{
    (void)context;
    return *register32(scb, RX_FIFO_STATUS_OFFSET);
}

static uint8_t selected_width(void *scb)
{
    const uint32_t control = *register32(scb, RX_CTRL_OFFSET);
    return (control & RX_CTRL_WIDTH_MASK) != 0u ? 2u : 1u;
}

static void mmio_read_array_no_check(void *context, void *scb,
                                     void *destination, uint32_t count)
{
    touch_scb_mmio_context_t *state =
        (touch_scb_mmio_context_t *)context;
    volatile uint32_t *fifo = register32(scb, RX_FIFO_RD_OFFSET);
    uint8_t width = state != NULL ? state->sampled_width : 0u;
    uint32_t i;

    /* The stock callee reads RX_CTRL once before entering either loop. */
    if (width == 0u) {
        width = selected_width(scb);
    }
    if (width == 1u) {
        uint8_t *out = (uint8_t *)destination;
        for (i = 0; i < count; ++i) {
            out[i] = (uint8_t)*fifo;
        }
    } else {
        uint16_t *out = (uint16_t *)destination;
        for (i = 0; i < count; ++i) {
            out[i] = (uint16_t)*fifo;
        }
    }
}

touch_scb_result_t touch_scb_mmio_bind(touch_scb_io_t *io)
{
    if (io == NULL) {
        return TOUCH_SCB_INVALID_ARGUMENT;
    }
    io->context = NULL;
    io->read_rx_fifo_status = mmio_read_rx_fifo_status;
    io->read_array_no_check = mmio_read_array_no_check;
    return TOUCH_SCB_OK;
}

uint32_t touch_scb_mmio_read_array(uintptr_t scb_base, void *destination,
                                   uint32_t requested)
{
    touch_scb_io_t io;
    (void)touch_scb_mmio_bind(&io);
    return touch_scb_read_array(&io, (void *)scb_base, destination, requested);
}

static uint32_t checked_read_status(void *context, void *scb)
{
    (void)context;
    return mmio_read_rx_fifo_status(NULL, scb);
}

static void checked_read_array(void *context, void *scb,
                               void *destination, uint32_t count)
{
    mmio_read_array_no_check(context, scb, destination, count);
}

touch_scb_result_t touch_scb_mmio_read_array_checked(uintptr_t scb_base,
                                                     void *destination,
                                                     size_t capacity_bytes,
                                                     uint32_t requested,
                                                     uint32_t *actual_out)
{
    touch_scb_io_t io;
    touch_scb_mmio_context_t state;
    uint8_t width;

    if (scb_base == (uintptr_t)0 ||
        scb_base > UINTPTR_MAX - (uintptr_t)RX_FIFO_RD_OFFSET ||
        (scb_base & (uintptr_t)3u) != 0u ||
        destination == NULL || actual_out == NULL) {
        return TOUCH_SCB_INVALID_ARGUMENT;
    }
    width = selected_width((void *)scb_base);
    if (width == 2u && ((uintptr_t)destination & (uintptr_t)1u) != 0u) {
        return TOUCH_SCB_INVALID_ARGUMENT;
    }

    state.sampled_width = width;
    io.context = &state;
    io.read_rx_fifo_status = checked_read_status;
    io.read_array_no_check = checked_read_array;
    return touch_scb_read_array_checked(&io, (void *)scb_base, destination,
                                        capacity_bytes, width, requested,
                                        actual_out);
}
