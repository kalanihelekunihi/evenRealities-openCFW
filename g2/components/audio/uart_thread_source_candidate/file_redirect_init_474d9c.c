/* Stock redirect mutex initialization, Apollo 0x474d9c. */
#include <stdint.h>

extern void *g2_codec_redirect_mutex;
extern void *g2_codec_heap_mutex;
extern uint32_t audio_even_ai_mutex_create_44971c(const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "redirect";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\redirect.c";
static const char function[] = "redirect_init";
static const char failure[] = "Failed to create redirect mutex for IAR.";
static const char success[] = "redirect init with mutex protection.";
static const char short_failure[] =
    "[redirect]Failed to create redirect mutex for IAR.";
static const char short_success[] =
    "[redirect]redirect init with mutex protection.";

int32_t audio_file_redirect_init_474d9c(void) {
    g2_codec_redirect_mutex =
        (void *)(uintptr_t)audio_even_ai_mutex_create_44971c(0);
    g2_codec_heap_mutex =
        (void *)(uintptr_t)audio_even_ai_mutex_create_44971c(0);
    if (!g2_codec_redirect_mutex || !g2_codec_heap_mutex) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x47au, failure);
        uint32_t flags = audio_log_flags();
        if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
            (void)compressed_log_output(0x04000000u, short_failure,
                                        short_failure);
        return -1;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x47eu, success);
    uint32_t flags = audio_log_flags();
    if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
        (void)compressed_log_output(0x0c000000u, short_success,
                                    short_success);
    return 0;
}
