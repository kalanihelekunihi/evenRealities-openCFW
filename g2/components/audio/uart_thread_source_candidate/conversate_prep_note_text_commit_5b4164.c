/* Native conversate_prep_note_layout_rebuild 0x5b4164..0x5b41bd. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_conversate_prep_note_layout_parse_5b4000(const void *, uint32_t);

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_prep_note_layout_rebuild";
static const char message[] = "prep note layout rebuild skipped, empty input";
static const char short_message[] =
    "[conversate.data]prep note layout rebuild skipped, empty input";

void audio_conversate_prep_note_text_commit_5b4164(const void *text,
                                                    uint32_t length) {
    if (!text || (uint16_t)length == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 147u, message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, short_message, short_message);
        return;
    }
    audio_conversate_prep_note_layout_parse_5b4000(text, (uint16_t)length);
}
