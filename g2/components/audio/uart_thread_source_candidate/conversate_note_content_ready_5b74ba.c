/* Apollo Main prep-note content-ready route, 0x5b74ba..0x5b7517. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_prep_note_refresh_5b6cd0(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.prep";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_prep_note_page.c";
static const char function[] = "conversate_ui_action_prep_note_content_ready";
static const char message[] =
    "prep note content ready while animating, defer refresh until animation end";
static const char compact[] =
    "[conversate.prep]prep note content ready while animating, defer refresh until animation end";

uint32_t audio_conversate_ui_route_5b74ba(uint32_t ignored, uint32_t arg) {
    (void)ignored;
    (void)arg;
    const volatile uint8_t *const ui = (const volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t root = *(const volatile uint32_t *)(const void *)(ui + 0x1cu);
    if (root == 0u) return UINT32_MAX;
    if (ui[0x98u] == 0u)
        return audio_conversate_prep_note_refresh_5b6cd0(0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x1d5u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, compact, compact);
    return 0u;
}
