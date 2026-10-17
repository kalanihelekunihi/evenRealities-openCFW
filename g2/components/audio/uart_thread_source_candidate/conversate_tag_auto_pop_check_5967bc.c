/* Native conversate_tag_auto_pop_check, 0x5967bc..0x596921. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.tag";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_tag_auto_pop_check";
static const char display_off[] = "AI cue display is disabled";
static const char display_off_short[] =
    "[conversate.tag]AI cue display is disabled";
static const char auto_off[] = "Auto pop is disabled";
static const char auto_off_short[] = "[conversate.tag]Auto pop is disabled";
static const char no_storage[] = "Storage not initialized";
static const char no_storage_short[] =
    "[conversate.tag]Storage not initialized";
static const char no_head[] = "Head is NULL, no previous node";
static const char no_head_short[] =
    "[conversate.tag]Head is NULL, no previous node";
static const char head_same[] =
    "Auto disp node is head, no need to keep auto pop";
static const char head_same_short[] =
    "[conversate.tag]Auto disp node is head, no need to keep auto pop";

static void note(uint32_t level, uint32_t line, uint32_t compact_level,
                 const char *message, const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(compact_level, short_message, short_message);
}

uint32_t audio_conversate_tag_ai_cue_enabled_5967bc(void) {
    const volatile uint8_t *const ui = (const volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint8_t *const storage = audio_conversate_tag_storage_state_200e3af4;
    if (ui[0x8cu] == 0u) {
        note(4u, 0x17du, 0x10000000u, display_off, display_off_short);
        return 0u;
    }
    if (ui[0x8eu] == 0u) {
        note(4u, 0x182u, 0x10000000u, auto_off, auto_off_short);
        return 0u;
    }
    if (storage[10] == 0u) {
        note(2u, 0x187u, 0x08000000u, no_storage, no_storage_short);
        return 0u;
    }
    const uint32_t head = *(const uint32_t *)(const void *)storage;
    if (head == 0u) {
        note(2u, 0x18cu, 0x08000000u, no_head, no_head_short);
        return 0u;
    }
    const uint32_t displayed = *(const uint32_t *)(const void *)(storage + 4u);
    if (displayed != head)
        return 1u;
    note(4u, 0x191u, 0x10000000u, head_same, head_same_short);
    return 0u;
}
