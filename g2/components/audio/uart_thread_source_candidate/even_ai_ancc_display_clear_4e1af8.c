/* Stock ANCC display forwarding wrapper, 0x4e1af8. */
#include <stdint.h>

extern uint8_t g2_audio_ancc_display_context_20073f84;
extern void audio_even_ai_ancc_display_send_5105bc(void *, uint32_t,
                                                    const uint32_t *);

void audio_even_ai_ancc_display_clear_4e1af8(uint32_t value,
                                               uint32_t count) {
    uint32_t saved_count = count;
    audio_even_ai_ancc_display_send_5105bc(
        &g2_audio_ancc_display_context_20073f84, value, &saved_count);
}
