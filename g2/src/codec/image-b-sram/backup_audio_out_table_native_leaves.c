/* SPDX-License-Identifier: MIT
 * Source reductions for four native audio output table targets. These are
 * genuine hardware-facing bodies; MMIO writes and wait completion require
 * device qualification beyond source-level control-flow evidence.
 * Native addresses: 0x10005ff4, 0x100060ec, 0x10006124,
 * 0x10006194, 0x100061b4, 0x100061bc, 0x1000657c, 0x100065bc,
 * 0x1000660c, 0x1000663c, 0x100064ec, 0x10006540, 0x10006774,
 * 0x1000612c.
 */
#include <stdint.h>

#define LATE_AUDIO __attribute__((section(".image_b_late_audio")))

extern void gx8002_image_b_delay_ms_10005194(uint32_t milliseconds);
extern void gx8002_image_b_platform_gate_10003be8(
    uint32_t module, uint32_t enable);
extern void gx8002_image_b_audio_start_10005e9c(void);
extern void gx8002_image_b_zero_100113c4(
    void *destination, uint32_t value, uint32_t bytes);
extern void gx8002_image_b_dcache_clean_range_10004e74(
    uint32_t address, int32_t length);
extern void gx8002_image_b_copy_10011344(
    void *destination, const void *source, uint32_t count);

LATE_AUDIO
int32_t gx8002_image_b_audio_out_route_mode_1000612c(
    uint32_t unused_handle, uint32_t mode)
{
    (void)unused_handle;
    /* Three 4-word native control fields at 0x10012b68..0x10012b98. */
    static const uint8_t low_bit[4] = {0u, 0u, 0u, 1u};
    static const uint8_t upper_field[4] = {1u, 0u, 1u, 1u};
    static const uint8_t lower_field[4] = {0u, 0u, 1u, 0u};
    uint32_t first = mode < 4u ? low_bit[mode] : 0u;
    uint32_t upper = mode < 4u ? upper_field[mode] : 0u;
    uint32_t lower = mode < 4u ? lower_field[mode] : 0u;
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    uint32_t control = dac[5];
    dac[5] = (control & ~UINT32_C(0x00000f00)) | (lower << 8);
    control = dac[5];
    dac[5] = (control & ~UINT32_C(0x0000f000)) | (upper << 12);
    control = dac[5];
    dac[5] = (control & ~1u) | first;
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_push_descriptor_10006774(
    volatile uint8_t *state, const void *descriptor)
{
    if (descriptor == (const void *)0) return -1;
    gx8002_image_b_copy_10011344((void *)(state + 0x20u), descriptor, 8u);
    uint32_t end = *(volatile uint32_t *)(volatile void *)(state + 0x24u);
    uint32_t start = *(volatile uint32_t *)(volatile void *)(state + 0x20u);
    int32_t divisor = state[0x19u];
    int32_t blocks = (int32_t)(end + 1u - start) / divisor;
    volatile uint32_t *const audio = (volatile uint32_t *)(uintptr_t)0xa0b80000u;
    (void)audio[5];
    audio[5] = start;
    (void)audio[6];
    audio[6] = end;
    uint32_t status = audio[9];
    audio[9] = (status & UINT32_C(0xff000000)) |
               ((uint32_t)blocks & UINT32_C(0x00ffffff));
    audio[11] |= 2u;
    if (state[0x1au] == 0u &&
        *(volatile uint32_t *)(volatile void *)(state + 0x2cu) != 0u) {
        state[0x1au] = 1u;
        volatile uint32_t *const dac =
            (volatile uint32_t *)(uintptr_t)0xa0b00000u;
        dac[0] |= 2u;
        dac[2] |= 2u;
    }
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_set_buffers_100064ec(
    uint32_t unused_handle, const uint32_t *descriptor)
{
    (void)unused_handle;
    uint32_t first = descriptor[0];
    if (first == 0u || (first & 15u) != 0u) return -1;
    volatile uint32_t *const audio = (volatile uint32_t *)(uintptr_t)0xa0b80000u;
    audio[1] = first + UINT32_C(0xe0000000);
    gx8002_image_b_dcache_clean_range_10004e74(first, (int32_t)descriptor[2]);
    uint32_t second = descriptor[1];
    if (second != 0u) {
        if ((second & 15u) != 0u) return -1;
        audio[2] = second + UINT32_C(0xe0000000);
        gx8002_image_b_dcache_clean_range_10004e74(second,
                                                     (int32_t)descriptor[2]);
    }
    audio[3] = descriptor[2];
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_clear_runtime_10006540(
    volatile uint8_t *state)
{
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    dac[2] &= ~1u;
    volatile uint32_t *const audio = (volatile uint32_t *)(uintptr_t)0xa0b80000u;
    (void)audio[5];
    audio[5] = 0u;
    (void)audio[6];
    audio[6] = 0u;
    gx8002_image_b_audio_start_10005e9c();
    gx8002_image_b_zero_100113c4((void *)(state + 0x10u), 0u, 36u);
    if (state != (volatile uint8_t *)0 && state[4] != 0u) state[4] = 0u;
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_enable_routes_1000657c(
    volatile uint8_t *state)
{
    gx8002_image_b_platform_gate_10003be8(11u, 1u);
    gx8002_image_b_platform_gate_10003be8(15u, 1u);
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    if (state[0x1bu] != 0u) dac[2] |= 1u;
    if (state[0x1au] != 0u) state[0x1au] = 0u;
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_disable_routes_100065bc(
    volatile uint8_t *state)
{
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    if (state[0x1bu] != 0u) {
        dac[2] &= ~1u;
        dac[3] &= 1u;
    }
    if (state[0x1au] != 0u) {
        dac[0] &= ~(1u << 1);
        dac[2] &= ~(1u << 1);
        dac[3] &= 2u;
    }
    gx8002_image_b_platform_gate_10003be8(11u, 0u);
    gx8002_image_b_platform_gate_10003be8(15u, 0u);
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_power_down_1000660c(void)
{
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    dac[8] &= ~(1u << 1);
    dac[8] &= ~(1u << 2);
    dac[8] &= ~(1u << 3);
    gx8002_image_b_platform_gate_10003be8(11u, 0u);
    gx8002_image_b_platform_gate_10003be8(15u, 0u);
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_power_up_1000663c(uint32_t mode)
{
    gx8002_image_b_platform_gate_10003be8(11u, 1u);
    gx8002_image_b_platform_gate_10003be8(15u, 1u);
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    dac[8] |= 1u << 1;
    dac[8] |= 1u << 2;
    dac[8] |= 1u << 3;
    uint32_t control = dac[1] & ~((1u << 10) | (1u << 11));
    if (mode == 2u) {
        dac[1] = control | (1u << 10);
        dac[1] &= ~(1u << 7);
    } else {
        dac[1] = control | ((mode << 10) & (3u << 10));
    }
    gx8002_image_b_audio_start_10005e9c();
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_config_route_10005ff4(
    volatile uint8_t *state, const uint32_t *configuration)
{
    uint32_t first = configuration[0];
    if (first != 0u) {
        volatile uint32_t *const dac =
            (volatile uint32_t *)(uintptr_t)0xa0b00000u;
        uint32_t current = dac[2];
        dac[2] = current | 1u;
        *(volatile uint32_t *)(volatile void *)(state + 0x28u) = first;
        state[0x1bu] = 1u;
    }
    uint32_t second = configuration[1];
    if (second != 0u) {
        *(volatile uint32_t *)(volatile void *)(state + 0x2cu) = second;
        state[0x1au] = 0u;
    }
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_dac_mute_100060ec(
    volatile uint8_t *state, uint32_t value)
{
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    uint32_t bit = (value != 0u);
    uint32_t control = dac[1];
    dac[1] = (control & ~(1u << 9)) | (bit << 9);
    control = dac[5];
    dac[5] = (control & ~(1u << 11)) | (bit << 11);
    control = dac[5];
    dac[5] = (control & ~(1u << 15)) | (bit << 15);
    *(volatile uint16_t *)(volatile void *)(state + 0x10u) = 1u;
    return 0;
}

LATE_AUDIO
uint32_t gx8002_image_b_audio_out_status_halfword_10006124(
    const volatile uint8_t *state)
{
    return *(const volatile uint16_t *)(const volatile void *)(state + 0x10u);
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_dac_high_word_10006194(
    uint32_t unused_handle, uint32_t value)
{
    (void)unused_handle;
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    dac[4] |= UINT32_C(0x80000000);
    uint32_t current = dac[4];
    dac[4] = (current & UINT32_C(0xff000000)) |
             ((value << 8) & UINT32_C(0x00ffffff));
    return 0;
}

LATE_AUDIO
uint32_t gx8002_image_b_audio_out_dac_read_100061b4(void)
{
    return *(volatile uint32_t *)(uintptr_t)0xa0b80010u;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_dac_start_wait_100061bc(
    volatile uint8_t *state)
{
    state[0x1cu] = 0u;
    state[0x1au] = 1u;
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    dac[0] |= 2u;
    dac[2] |= 2u;
    while (state[0x1cu] == 0u)
        gx8002_image_b_delay_ms_10005194(1u);
    return 0;
}
