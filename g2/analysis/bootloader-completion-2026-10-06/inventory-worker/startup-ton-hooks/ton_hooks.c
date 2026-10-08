#include <stdint.h>
#include "ton_hooks.h"

#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))

/* Preserved as explicit call-frontier cuts, not recovered here. */
extern uint32_t ton_cut_41c838(uint32_t value);
extern uint32_t ton_cut_41d1c0(uint32_t value);

uint32_t opencfw_ton_trim_cache(void) {
    uint32_t revision = W(0x4002000c) & 0xffu;
    uint32_t variant = W(0x20000098);
    if (!(revision >= 34u || (revision == 33u && variant != 0u))) {
        B(0x20000554) = 14;
        B(0x20000555) = 31;
        B(0x20000558) = 21;
        B(0x20000559) = 31;
        B(0x20000556) = 11;
        B(0x20000557) = 11;
        return 0;
    }
    uint32_t trim = W(0x40020344);
    B(0x20000554) = (uint8_t)((trim >> 25) & 31u);
    B(0x20000555) = (uint8_t)((trim >> 11) & 31u);
    trim = W(0x40020358);
    B(0x20000558) = (uint8_t)((trim >> 8) & 31u);
    trim = W(0x40020354);
    B(0x20000559) = (uint8_t)((trim >> 17) & 31u);
    trim = W(0x4002034c);
    B(0x20000556) = (uint8_t)((trim >> 25) & 31u);
    B(0x20000557) = (uint8_t)((trim >> 11) & 31u);
    return 0;
}

uint32_t opencfw_ton_trim_apply(uint32_t gpu_on, uint32_t gpu_mode) {
    volatile uint32_t *const state = (volatile uint32_t *)(uintptr_t)0x40021100;
    uint32_t was_enabled = *state & 1u;
    if (was_enabled) {
        (void)ton_cut_41c838(0);
        (void)ton_cut_41d1c0(5);
        *state &= ~1u;
    }

    uint32_t row = 0;
    if ((uint8_t)gpu_on != 0u)
        row = ((uint8_t)gpu_mode == 0u) ? 1u : 2u;

    const volatile uint8_t *const cfg =
        (const volatile uint8_t *)(uintptr_t)(0x433f20u + row * 3u);
    uint32_t use_first = cfg[1] == 1u;
    uint32_t use_second = cfg[2] == 1u;
    W(0x40020340) |= 0x80000000u;

    uint32_t a, b;
    a = B(use_first ? 0x20000554 : 0x20000555);
    b = B(use_second ? 0x20000554 : 0x20000555);
    W(0x40020344) = (W(0x40020344) & ~(31u << 25)) | (a << 25);
    W(0x40020344) = (W(0x40020344) & ~(31u << 11)) | (b << 11);

    a = B(use_first ? 0x20000558 : 0x20000559);
    b = B(use_second ? 0x20000558 : 0x20000559);
    W(0x40020358) = (W(0x40020358) & ~(31u << 8)) | (a << 8);
    W(0x40020354) = (W(0x40020354) & ~(31u << 17)) | (b << 17);

    a = B(use_first ? 0x20000556 : 0x20000557);
    b = B(use_second ? 0x20000556 : 0x20000557);
    W(0x4002034c) = (W(0x4002034c) & ~(31u << 25)) | (a << 25);
    W(0x4002034c) = (W(0x4002034c) & ~(31u << 11)) | (b << 11);

    if (was_enabled) {
        *state |= 1u;
        (void)ton_cut_41d1c0(5);
        (void)ton_cut_41c838(1);
    }
    return 0;
}
