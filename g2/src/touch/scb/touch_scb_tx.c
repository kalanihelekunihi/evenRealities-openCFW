/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#include "touch_scb_tx.h"

enum {
    FIFO_CONFIG_OFFSET = 0x000u,
    TX_CTRL_OFFSET = 0x200u,
    TX_FIFO_STATUS_OFFSET = 0x208u,
    TX_FIFO_WR_OFFSET = 0x240u,
    FIFO_CONFIG_DEPTH_MASK = 0xc000u,
    TX_CTRL_WIDTH_MASK = 0x18u,
    FIFO_USED_MASK = 0x1ffu
};

static volatile uint32_t *register32(uintptr_t base, uintptr_t offset)
{
    return (volatile uint32_t *)(base + offset);
}

static uint32_t fifo_depth(uintptr_t base)
{
    const uint32_t config = *register32(base, FIFO_CONFIG_OFFSET);
    return (config & FIFO_CONFIG_DEPTH_MASK) == 0u ? 16u : 8u;
}

static uint32_t fifo_used(uintptr_t base)
{
    return *register32(base, TX_FIFO_STATUS_OFFSET) & FIFO_USED_MASK;
}

static uint8_t tx_width(uintptr_t base)
{
    const uint32_t control = *register32(base, TX_CTRL_OFFSET);
    return (control & TX_CTRL_WIDTH_MASK) == 0u ? 1u : 2u;
}

static void write_elements(uintptr_t base, const void *source,
                           uint32_t count, uint8_t width)
{
    volatile uint32_t *fifo = register32(base, TX_FIFO_WR_OFFSET);
    uint32_t i;

    if (width == 1u) {
        const uint8_t *in = (const uint8_t *)source;
        for (i = 0; i < count; ++i) {
            *fifo = (uint32_t)in[i];
        }
    } else {
        const uint16_t *in = (const uint16_t *)source;
        for (i = 0; i < count; ++i) {
            *fifo = (uint32_t)in[i];
        }
    }
}

uint32_t touch_scb_mmio_write_array(uintptr_t scb_base, const void *source,
                                    uint32_t requested)
{
    const uint32_t depth = fifo_depth(scb_base);
    const uint32_t used = fifo_used(scb_base);
    const uint32_t available = depth - used;
    const uint32_t actual = requested < available ? requested : available;
    const uint8_t width = tx_width(scb_base);

    write_elements(scb_base, source, actual, width);
    return actual;
}

touch_scb_tx_result_t touch_scb_mmio_write_array_checked(
    uintptr_t scb_base, const void *source, size_t capacity_bytes,
    uint32_t requested, uint32_t *actual_out)
{
    uint32_t depth;
    uint32_t used;
    uint32_t available;
    uint32_t actual;
    uint8_t width;
    size_t bytes_needed;

    if (scb_base == (uintptr_t)0 ||
        scb_base > UINTPTR_MAX - (uintptr_t)TX_FIFO_WR_OFFSET ||
        (scb_base & (uintptr_t)3u) != 0u ||
        source == NULL || actual_out == NULL) {
        return TOUCH_SCB_TX_INVALID_ARGUMENT;
    }

    /* Sample mode/depth/status once; caller serializes configuration changes. */
    depth = fifo_depth(scb_base);
    width = tx_width(scb_base);
    used = fifo_used(scb_base);
    if (used > depth) {
        return TOUCH_SCB_TX_INVALID_FIFO_STATUS;
    }
    if (width == 2u && ((uintptr_t)source & (uintptr_t)1u) != 0u) {
        return TOUCH_SCB_TX_INVALID_ALIGNMENT;
    }

    available = depth - used;
    actual = requested < available ? requested : available;
    bytes_needed = (size_t)actual * (size_t)width;
    if (bytes_needed > capacity_bytes) {
        return TOUCH_SCB_TX_INSUFFICIENT_CAPACITY;
    }

    write_elements(scb_base, source, actual, width);
    *actual_out = actual;
    return TOUCH_SCB_TX_OK;
}
