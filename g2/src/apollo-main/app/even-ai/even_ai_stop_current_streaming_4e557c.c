/* Stock EvenAI stream stop/pause dispatcher at 0x4e557c. */
#include <stdint.h>

extern uint32_t audio_even_ai_text_stream_handle_20074c04;
extern uint8_t audio_even_ai_stream_display_state_20073a1c[0x20];
extern void audio_text_stream_stop_552d10(uint32_t);
extern void audio_text_stream_pause_552d40(uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "even_ai.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\ui_even_ai.c";
static const char function[] = "even_ai_stop_current_streaming";
static const char message[] =
    "Stopped current streaming display for phase transition";
static const char short_message[] =
    "[even_ai.ui]Stopped current streaming display for phase transition";

void audio_even_ai_stop_current_streaming_4e557c(uint32_t mode) {
    uint32_t handle = audio_even_ai_text_stream_handle_20074c04;
    if (!handle)
        return;
    if ((uint8_t)mode) {
        audio_text_stream_stop_552d10(handle);
        audio_uart_buffer_zero(audio_even_ai_stream_display_state_20073a1c,
                               0x20u, 0u);
    } else {
        audio_text_stream_pause_552d40(handle);
        audio_even_ai_stream_display_state_20073a1c[0] = 0u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x148u, message);
    uint32_t flags = audio_log_flags();
    if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
        (void)compressed_log_output(0x0c000000u, short_message,
                                    short_message);
}
