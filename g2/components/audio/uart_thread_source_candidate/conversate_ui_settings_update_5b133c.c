/* Native conversate_ui_settings_update 0x5b133c..0x5b13fd. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

/* The machine cell ends at the separately owned tag-storage cell. */
__attribute__((used, section(".g2_conversate_machine_context_200e3aec")))
uint8_t audio_conversate_machine_context_200e3aec[8];

/* UI-state byte at 0x20071368 is owned by conversate_ui_state_ram_20071368.c. */
__attribute__((used, section(".g2_conversate_ui_settings_extension_20071369")))
uint8_t audio_conversate_ui_settings_extension_20071369[0x94];

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_settings_update";
static const char message[] =
    "ai_cue_display:%d, transcribe_display:%d, tag_display_height:%d, auto_pop_en:%d, cue_duration:%d";
static const char short_message[] =
    "[conversate.ui]ai_cue_display:%d, transcribe_display:%d, tag_display_height:%d, auto_pop_en:%d, cue_duration:%d";

void audio_conversate_apply_config_5b133c(void) {
    const uint8_t *const settings = audio_conversate_machine_context_200e3aec + 1u;
    uint8_t *const ui = audio_conversate_ui_settings_extension_20071369;
    ui[0x8b] = settings[0];
    ui[0x8c] = settings[1];
    const uint32_t height = settings[1] != 0u ? 204u : 288u;
    ui[0x8f] = (uint8_t)height;
    ui[0x90] = (uint8_t)(height >> 8);
    ui[0x91] = 0u;
    ui[0x92] = 0u;
    ui[0x8d] = (settings[2] != 0u && settings[0] != 0u) ? 1u : 0u;
    ui[0x93] = settings[4];
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 388u, message,
                           ui[0x8b], ui[0x8c], height, ui[0x8d], ui[0x93]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0d400000u, short_message, short_message,
                         ui[0x8b], ui[0x8c], height, ui[0x8d], ui[0x93]);
}
