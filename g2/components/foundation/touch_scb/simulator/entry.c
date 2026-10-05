/* SPDX-License-Identifier: MIT */
#include "../touch_scb_mmio.h"
#include "../touch_scb_tx.h"
#include "../touch_scb_fifo.h"
#include <stdint.h>

/* Callable simulator module. No boot vectors, IRQs or board initialization. */
uint32_t touch_scb_sim_read(uintptr_t base, void *destination, uint32_t requested)
{
    return touch_scb_mmio_read_array(base, destination, requested);
}

typedef struct {
    uint32_t base, destination, requested, capacity, actual, result;
} touch_scb_sim_request_t;

void touch_scb_sim_checked(touch_scb_sim_request_t *request)
{
    request->result = (uint32_t)touch_scb_mmio_read_array_checked(
        (uintptr_t)request->base, (void *)(uintptr_t)request->destination,
        request->capacity, request->requested, &request->actual);
}

uint32_t touch_scb_sim_write(uintptr_t base, const void *source, uint32_t requested)
{
    return touch_scb_mmio_write_array(base, source, requested);
}

void touch_scb_sim_write_checked(touch_scb_sim_request_t *request)
{
    request->result = (uint32_t)touch_scb_mmio_write_array_checked(
        (uintptr_t)request->base, (const void *)(uintptr_t)request->destination,
        request->capacity, request->requested, &request->actual);
}

uint32_t touch_scb_sim_set_rx_level(uintptr_t base, uint32_t level)
{
    return (uint32_t)touch_scb_fifo_set_rx_level(base, level);
}
