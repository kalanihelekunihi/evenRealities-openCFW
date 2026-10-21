/* Apollo GPU mode cache and two callers, native 0x4b06c0..0x4b075d. */
#include <stdint.h>

extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void display_driver_nema_mode_513924(uint32_t mode, int32_t a,
                                             int32_t b, int32_t c);

void display_driver_gpu_mode_lower_4b06c0(uint32_t unit, uint32_t mode,
                                            uint32_t a, uint32_t b,
                                            uint32_t c, uint32_t force)
{
    volatile uint8_t *const state = unit
        ? (volatile uint8_t *)(uintptr_t)unit
        : (volatile uint8_t *)audio_uart_ambiq_default_unit_4c791a();
    if ((uint8_t)force == 0u &&
        mode == *(volatile uint32_t *)(void *)(state + 0x50u) &&
        (int8_t)a == *(volatile int8_t *)(void *)(state + 0x54u) &&
        (int8_t)b == *(volatile int8_t *)(void *)(state + 0x55u) &&
        (int8_t)c == *(volatile int8_t *)(void *)(state + 0x56u))
        return;

    display_driver_nema_mode_513924(mode, (int8_t)a, (int8_t)b, (int8_t)c);
    *(volatile uint32_t *)(void *)(state + 0x50u) = mode;
    state[0x54u] = (uint8_t)a;
    state[0x55u] = (uint8_t)b;
    state[0x56u] = (uint8_t)c;
}

void display_driver_gpu_mode_4b0730(uint32_t unit, uint32_t mode)
{
    display_driver_gpu_mode_lower_4b06c0(unit, mode, 0u, UINT32_MAX,
                                           UINT32_MAX, 0u);
}

void display_driver_gpu_enable_4b0748(uint32_t unit, uint32_t mode)
{
    display_driver_gpu_mode_lower_4b06c0(unit, mode, 0u, 1u,
                                           UINT32_MAX, 0u);
}
