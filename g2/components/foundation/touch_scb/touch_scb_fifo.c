/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 openCFW contributors
 */
#include "touch_scb_fifo.h"

#include <stdint.h>

enum {
    FIFO_CONFIG_OFFSET = 0x000u,
    RX_FIFO_CTRL_OFFSET = 0x304u,
    FIFO_DEPTH_MASK = 0xc000u,
    RX_FIFO_TRIGGER_LEVEL_MASK = 0xffu
};

static volatile uint32_t *register32(uintptr_t base, uintptr_t offset)
{
    return (volatile uint32_t *)(base + offset);
}

touch_scb_fifo_result_t touch_scb_fifo_set_rx_level(uintptr_t scb_base,
                                                    uint32_t level)
{
    uint32_t depth;
    uint32_t control;

    if (scb_base == (uintptr_t)0 ||
        scb_base > UINTPTR_MAX - (uintptr_t)RX_FIFO_CTRL_OFFSET ||
        (scb_base & (uintptr_t)3u) != 0u) {
        return TOUCH_SCB_FIFO_INVALID_ARGUMENT;
    }

    depth = (*register32(scb_base, FIFO_CONFIG_OFFSET) & FIFO_DEPTH_MASK) == 0u
                ? 16u : 8u;
    if (level >= depth) {
        return TOUCH_SCB_FIFO_INVALID_LEVEL;
    }

    control = *register32(scb_base, RX_FIFO_CTRL_OFFSET);
    control = (control & ~RX_FIFO_TRIGGER_LEVEL_MASK) |
              (level & RX_FIFO_TRIGGER_LEVEL_MASK);
    *register32(scb_base, RX_FIFO_CTRL_OFFSET) = control;
    return TOUCH_SCB_FIFO_OK;
}
