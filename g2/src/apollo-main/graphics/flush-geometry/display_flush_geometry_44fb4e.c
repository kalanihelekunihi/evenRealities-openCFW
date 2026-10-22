/* Apollo Main display flush area copy, geometry and ready accessors.
 * Native spans 0x439c04, 0x44fa1a, 0x44fad2, 0x44fb10,
 * 0x44fb4e, 0x44fb9a, 0x44fc42. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];


void *audio_uart_display_area_copy_439c04(void *out, const void *in, uint32_t count) {
    uint8_t *dst = (uint8_t *)out;
    const uint8_t *src = (const uint8_t *)in;
    for (uint32_t index = 0; index < count; ++index) dst[index] = src[index];
    return out;
}






