/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x102085f8, 0x10208d48, and 0x102067a0. Retained native
 * disassembly supplies literal addresses, callback offsets/order, and the
 * watchdog MMIO store.
 */
#include <stdint.h>

extern int32_t gx8002_xip_tws_dequeue_10206fb0(
    volatile void *queue, uint32_t *event);
extern uint32_t gx8002_xip_uart_async_tick_10208334(void);

void gx8002_xip_watchdog_ping_102067a0(void)
{
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa070000c) = 118u;
}

uint32_t gx8002_xip_mode_tick_102085f8(void)
{
    volatile uint32_t *const mode =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e6e4);
    volatile uint32_t *const modes =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x1020b1bc);
    uint32_t index = mode[1];
    uintptr_t object = (uintptr_t)modes[index];
    uintptr_t callback = *(volatile uint32_t *)(object + 12u);
    if (callback != 0u) ((void (*)(void))callback)();
    return mode[0];
}

uint32_t gx8002_xip_app_event_tick_10208d48(void)
{
    uint32_t event[2] = {0u, 0u};
    int32_t available = gx8002_xip_tws_dequeue_10206fb0(
        (volatile void *)(uintptr_t)UINT32_C(0x2002ecd8), event);
    volatile uintptr_t *const app =
        (volatile uintptr_t *)(uintptr_t)UINT32_C(0x20026d38);
    uintptr_t object = *app;
    if (available != 0 && object != 0u) {
        uintptr_t on_event = *(volatile uint32_t *)(object + 8u);
        if (on_event != 0u)
            (void)((uint32_t (*)(const uint32_t *))on_event)(event);
    }
    object = *app;
    if (object != 0u) {
        uintptr_t on_tick = *(volatile uint32_t *)(object + 12u);
        if (on_tick != 0u) (void)((uint32_t (*)(void))on_tick)();
    }
    (void)gx8002_xip_uart_async_tick_10208334();
    gx8002_xip_watchdog_ping_102067a0();
    return 0u;
}
