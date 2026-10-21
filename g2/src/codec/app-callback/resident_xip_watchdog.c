/* SPDX-License-Identifier: MIT
 * Image-A XIP watchdog graph, native 0x10206704/20/ac/b8.
 * Register accesses are real device contracts; this source is not a host
 * simulation or evidence of physical watchdog behavior.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

static volatile uint32_t *const watchdog =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0780000);
static volatile uint32_t *const callback_slot =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b48);

uint32_t gx8002_xip_watchdog_interrupt_10206704(void)
{
    uint32_t callback = *callback_slot;
    uint32_t result = 0u;
    if (callback != 0u)
        result = ((uint32_t (*)(void))(uintptr_t)(callback & ~1u))();
    (void)watchdog[0x14u / 4u];
    return result;
}

void gx8002_xip_watchdog_initialize_10206720(
    uint32_t unused, uint32_t timeout_ms, void (*callback)(void),
    uint32_t context)
{
    (void)unused;
    if (timeout_ms < 1000u) {
        gx8002_xip_tws_publish_10206c24("level timout invalid\n");
        return;
    }
    gx8002_resident_platform_gate_25080(24u, 1u);
    uint32_t seconds = timeout_ms / 1000u;
    uint32_t exponent = 0u;
    for (uint32_t remaining = 16u; remaining != 0u; --remaining) {
        if (((UINT32_C(1) << (exponent + 16u)) / 1000000u) >= seconds)
            break;
        ++exponent;
    }
    if (exponent >= 16u) exponent = 15u;
    watchdog[1] = exponent | (exponent << 4u);
    watchdog[3] = 0x76u;
    *callback_slot = (uint32_t)(uintptr_t)callback;
    gx8002_resident_request_irq_2553c(
        11u, (uint32_t)(uintptr_t)gx8002_xip_watchdog_interrupt_10206704,
        context);
    watchdog[0] |= 1u;
}

void gx8002_xip_watchdog_stop_102067ac(void)
{
    watchdog[0] &= ~UINT32_C(1);
}

__attribute__((noreturn)) void gx8002_xip_reboot_102067b8(void)
{
    gx8002_resident_platform_gate_25080(24u, 1u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa001002c) = 1u;
    watchdog[0] = 0u;
    watchdog[1] = 0u;
    watchdog[3] = 0x76u;
    watchdog[0] = 1u;
    for (;;) __asm__ volatile ("" ::: "memory");
}
