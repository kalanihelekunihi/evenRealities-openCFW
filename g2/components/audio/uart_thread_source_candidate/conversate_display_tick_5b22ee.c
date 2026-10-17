/* Apollo Main Conversate display animation completion, 0x5b22ee..0x5b22f9. */
#include <stdint.h>

extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

void audio_conversate_display_tick_5b22ee(void) {
    audio_conversate_report_5b02e4(18u, 0u);
}
