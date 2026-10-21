/* Stock EvenAI text-stream initialization at 0x4e551e. */
#include <stdint.h>

extern uint32_t audio_even_ai_text_stream_handle_20074c04;
extern uint32_t audio_text_stream_create_552b30(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "even_ai.ui";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\ui_even_ai.c";
static const char function[] = "even_ai_init_text_stream_service";
static const char message[] = "Failed to initialize Even AI text stream service";
static const char short_message[] =
    "[even_ai.ui]Failed to initialize Even AI text stream service";

void audio_even_ai_init_text_stream_4e551e(void) {
    if (audio_even_ai_text_stream_handle_20074c04 != 0u)
        return;
    audio_even_ai_text_stream_handle_20074c04 = audio_text_stream_create_552b30();
    if (audio_even_ai_text_stream_handle_20074c04 != 0u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 0x133u, message);
    uint32_t flags = audio_log_flags();
    if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
        (void)compressed_log_output(0x04000000u, short_message, short_message);
}
