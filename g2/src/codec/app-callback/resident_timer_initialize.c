/* SPDX-License-Identifier: MIT
 * Image-A SRAM timer initializers 0x100257b8 and 0x100257e8. Native
 * instruction order preserves the write-one control pulses and frequencies.
 * Frequency, zeroing, and timer IRQ bodies remain real typed lower imports.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t module);
extern void gx8002_resident_platform_gate_25080(uint32_t module,
                                                 uint32_t enabled);
extern void gx8002_resident_request_irq_2553c(
    uint32_t number, uint32_t raw_handler_entry, uint32_t context);
extern void gx8002_xip_memset_102099cc(void *dst, uint32_t value,
                                        uint32_t size);
extern uint32_t gx8002_resident_timer_dispatch_258c4(void);

/* Stock 0x100257B8 (gx8002_timer_channel_initialize) */
void gx8002_resident_timer_channel_initialize_257b8(void)
{
    volatile uint32_t *const timer =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400000);
    timer[0x50u / 4u] = 1u;
    timer[0x50u / 4u] = 0u;
    timer[0x60u / 4u] = 1u;
    uint32_t clock = gx8002_resident_clock_frequency_25210(23u);
    timer[0x64u / 4u] = clock / UINT32_C(1000000) - 1u;
    timer[0x68u / 4u] = 0u;
    timer[0x50u / 4u] = 2u;
}

/* Stock 0x100257E8 (gx8002_timer_initialize) */
void gx8002_resident_timer_initialize_257e8(void)
{
    gx8002_resident_platform_gate_25080(23u, 1u);
    volatile uint32_t *const timer =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400000);
    timer[0x10u / 4u] = 1u;
    timer[0x10u / 4u] = 0u;
    timer[0x20u / 4u] = 3u;
    uint32_t clock = gx8002_resident_clock_frequency_25210(23u);
    timer[0x24u / 4u] = clock / UINT32_C(1000000) - 1u;
    timer[0x28u / 4u] = UINT32_C(0xfffffc18);
    timer[0x10u / 4u] = 2u;

    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x20026d84), 0u, 0x168u);
    gx8002_resident_request_irq_2553c(14u,
        (uint32_t)(uintptr_t)gx8002_resident_timer_dispatch_258c4, 0u);
    gx8002_resident_timer_channel_initialize_257b8();

    volatile uint32_t *const secondary =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400080);
    secondary[0x10u / 4u] = 1u;
    secondary[0x10u / 4u] = 0u;
    secondary[0x20u / 4u] = 1u;
    secondary[0x24u / 4u] = 0u;
    secondary[0x28u / 4u] = 0u;
    secondary[0x10u / 4u] = 2u;
}
