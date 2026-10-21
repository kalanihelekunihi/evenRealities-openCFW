/* Native Conversate tag-update route, 0x5b6426..0x5b660d. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_tag_storage_count_59674e(void);
extern uint32_t audio_conversate_ui_list_count_5b0c18(void);
extern void *audio_conversate_tag_get_by_index_5964e2(uint32_t);
extern uint32_t audio_conversate_tag_icon_get_5b0af6(uint32_t);
extern uint32_t audio_conversate_prep_button_create_5b1150(uint32_t, uint32_t,
                                                             uint32_t, uint32_t);
extern void audio_uart_page_44daca(uint32_t, uint32_t);
extern uint32_t audio_conversate_tag_ai_cue_enabled_5967bc(void);
extern void audio_conversate_tag_scroll_update_5b63d4(volatile uint8_t *);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern void audio_conversate_ui_list_view_mode_set_5b0edc(uint32_t, uint32_t,
                                                            const char *);
extern void audio_conversate_ui_slot_fade_5b1072(uint32_t, uint32_t);
extern void audio_terminal_list_anim_new_start_58c622(uint32_t, uint32_t,
                                                        uint32_t);
extern void audio_terminal_list_anim_old_start_58c6c4(uint32_t, uint32_t,
                                                        uint32_t);
extern void audio_terminal_ui_scroll_to_view_44ea2e(uint32_t, uint32_t);
extern void audio_conversate_ui_main_page_refresh_5b13fe(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_tag_page.c";
static const char function[] = "conversate_ui_action_tag_update";
static const char create_failed[] = "Failed to create new button";
static const char create_failed_short[] =
    "[conversate.ui]Failed to create new button";
static const char display_disabled[] =
    "AI cue display is disabled, set current button to new button";
static const char display_disabled_short[] =
    "[conversate.ui]AI cue display is disabled, set current button to new button";
static const char auto_pop[] = "tag update auto pop en";
static const char single_highlight[] = "tag update single highlight";

static uint32_t word(const volatile uint8_t *p, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(p + offset);
}
static void put_word(volatile uint8_t *p, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(p + offset) = value;
}

uint32_t audio_conversate_ui_route_5b6426(uint32_t state, uint32_t value) {
    (void)state;
    (void)value;
    const uint32_t stored = audio_conversate_tag_storage_count_59674e();
    const uint32_t shown = audio_conversate_ui_list_count_5b0c18();
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    if (stored == 0u || shown >= stored)
        return UINT32_MAX;
    const uint8_t *const tag = audio_conversate_tag_get_by_index_5964e2(0u);
    if (tag == 0)
        return UINT32_MAX;
    const uint32_t icon = audio_conversate_tag_icon_get_5b0af6(tag[0]);
    const uint32_t button = audio_conversate_prep_button_create_5b1150(
        word(ui, 0x64u), icon,
        *(const uint32_t *)(const void *)(tag + 4u), 0u);
    if (button == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0x126u,
                               create_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, create_failed_short,
                                        create_failed_short);
        return UINT32_MAX;
    }
    audio_uart_page_44daca(button, 0u);
    if (ui[0x8cu] == 0u) {
        put_word(ui, 0x80u, button);
        put_word(ui, 0x84u, 0u);
        ui[0x96u] = 0u;
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, source, function, 0x12fu,
                               display_disabled);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, display_disabled_short,
                                        display_disabled_short);
        return 0u;
    }
    if (ui[0x8eu] != 0u) {
        if (ui[0x96u] == 1u) {
            audio_conversate_tag_scroll_update_5b63d4(ui);
        } else {
            if (audio_conversate_tag_ai_cue_enabled_5967bc() == 1u && ui[0] == 2u)
                audio_conversate_report_5b02e4(8u, 1u);
            put_word(ui, 0x80u, button);
            put_word(ui, 0x84u, 0u);
            audio_conversate_ui_list_view_mode_set_5b0edc(0u, 0u, auto_pop);
        }
        audio_conversate_ui_main_page_refresh_5b13fe();
        return 0u;
    }
    if (ui[0x96u] == 0u) {
        audio_conversate_ui_list_view_mode_set_5b0edc(1u, 0u, single_highlight);
        audio_conversate_ui_slot_fade_5b1072(button, 1u);
        audio_terminal_list_anim_new_start_58c622(button, 0xfau, 0u);
        audio_terminal_ui_scroll_to_view_44ea2e(button, 0u);
        put_word(ui, 0x80u, button);
        put_word(ui, 0x84u, 0u);
        ui[0x96u] = 1u;
        audio_conversate_ui_main_page_refresh_5b13fe();
    } else if (ui[0x97u] == 1u) {
        const uint32_t old = word(ui, 0x80u);
        if (old != 0u) {
            audio_conversate_ui_slot_fade_5b1072(old, 0u);
            audio_terminal_list_anim_old_start_58c6c4(old, 0xfau, 0u);
        }
        audio_conversate_ui_slot_fade_5b1072(button, 1u);
        audio_terminal_list_anim_new_start_58c622(button, 0xfau, 0u);
        audio_terminal_ui_scroll_to_view_44ea2e(button, 0u);
        put_word(ui, 0x80u, button);
        put_word(ui, 0x84u, 0u);
        ui[0x96u] = 1u;
    } else {
        audio_conversate_tag_scroll_update_5b63d4(ui);
    }
    audio_conversate_ui_main_page_refresh_5b13fe();
    return 0u;
}
