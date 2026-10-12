/* Native RTC extraction at 0x4d3554.  The retained literal at 0x4d3608
 * identifies the live shadow word (0x200742ac); 0x4d360c identifies
 * the hardware RTC word (0x4000885c). */
#include <stdint.h>

extern volatile uint32_t audio_uart_ring_rtc_shadow_200742ac;

uint32_t audio_uart_ring_rtc_snapshot_4d3554(void *result) {
    uint8_t *out = (uint8_t *)result;
    if (out == (void *)0) return 6u;
    uint32_t value = audio_uart_ring_rtc_shadow_200742ac;
    if (value == 0u) {
        value = *(volatile const uint32_t *)(uintptr_t)0x4000885cu;
        audio_uart_ring_rtc_shadow_200742ac = value;
    }
    value &= 0x1fffu;
    audio_uart_ring_rtc_shadow_200742ac = value;
    *(uint16_t *)(void *)out = (uint16_t)value;
    for (unsigned bit = 0; bit < 11u; ++bit) out[2u + bit] = (uint8_t)((value >> bit) & 1u);
    out[13] = 0u;
    out[14] = (uint8_t)((value >> 12) & 1u);
    return value == 0u ? 1u : 0u;
}
