/* SPDX-License-Identifier: MIT
 * Three-argument private-ABI adapter for the source provider at 0x426808.
 * Stock sibling-call dependencies stay explicit instead of being silently
 * replaced with success stubs. MMIO accesses are volatile target accesses.
 */
#include "power_control_adapter.h"
#include "power_control.h"
#include "../clock_manager/clock_manager.h"
#include <stdint.h>

#define MSPI0_BASE 0x40060000u
#define MODULE_STRIDE 0x1000u

/* Bounded sibling providers; these names are intended to be bound by the
 * integration linker to reviewed source providers or stock-address cuts. */
extern uint32_t opencfw_bl_mspi_mode_enter(uint32_t user_id); /* 0x41bf84 */
extern uint32_t opencfw_bl_mspi_mode_leave(uint32_t user_id); /* 0x41c17a */
extern uint32_t opencfw_bl_clock_release_all(uint32_t user_id); /* 0x4223d8 */
extern uint32_t opencfw_bl_mspi_clockgen_control(uint32_t module,
    uint32_t enable, uint32_t configure, uint32_t source); /* 0x4249a0 */
extern uint32_t opencfw_hal_mspi_cq_disable(uint32_t handle); /* 0x423fac */
extern void opencfw_bl_mspi_cq_enable(uint32_t handle); /* 0x423f8e */
extern void opencfw_hal_delay_us(uint32_t duration); /* 0x41d1c0 */

static uint32_t mode_enter(uint8_t user)
{
    return opencfw_bl_mspi_mode_enter(user);
}

static uint32_t mode_leave(uint8_t user)
{
    return opencfw_bl_mspi_mode_leave(user);
}

static uint32_t request_clock(uint8_t clock_id, uint8_t user)
{
    return clock_request(clock_id, user);
}

static uint32_t release_all(uint8_t user)
{
    return opencfw_bl_clock_release_all(user);
}

static void clockgen(uint32_t module, uint8_t enable, uint8_t configure,
                     uint8_t source)
{
    (void)opencfw_bl_mspi_clockgen_control(module, enable, configure, source);
}

static uint32_t cq_disable(uint32_t *handle)
{
    return opencfw_hal_mspi_cq_disable((uint32_t)(uintptr_t)handle);
}

static void cq_enable(uint32_t *handle)
{
    opencfw_bl_mspi_cq_enable((uint32_t)(uintptr_t)handle);
}

static uint32_t interrupt_disable(uint32_t *handle, uint32_t mask)
{
    const uint32_t module = handle[1];
    volatile uint32_t *const inten = (volatile uint32_t *)(uintptr_t)
        (MSPI0_BASE + module * MODULE_STRIDE + 0x200u);
    *inten &= ~mask;
    return 0u;
}

static void delay_us(uint32_t duration)
{
    opencfw_hal_delay_us(duration);
}

static uint32_t mmio_read(uint32_t module, uint16_t offset)
{
    return *(volatile uint32_t *)(uintptr_t)
        (MSPI0_BASE + module * MODULE_STRIDE + offset);
}

static void mmio_write(uint32_t module, uint16_t offset, uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)
        (MSPI0_BASE + module * MODULE_STRIDE + offset) = value;
}

static const opencfw_mspi_power_ops_t native_ops = {
    .mode_enter = mode_enter,
    .mode_leave = mode_leave,
    .clock_request = request_clock,
    .clock_release_all = release_all,
    .clockgen = clockgen,
    .cq_disable = cq_disable,
    .cq_enable = cq_enable,
    .interrupt_disable = interrupt_disable,
    .delay_us = delay_us,
    .mmio_read = mmio_read,
    .mmio_write = mmio_write,
};

uint32_t opencfw_bl_power_control(uint32_t handle, uint32_t operation,
                                  uint32_t retain_state)
{
    return opencfw_hal_mspi_power_control(
        (uint32_t *)(uintptr_t)handle, operation, retain_state, &native_ops);
}
