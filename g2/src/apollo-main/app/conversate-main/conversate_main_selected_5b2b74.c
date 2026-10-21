/* Apollo Main Conversate main-page selected route, 0x5b2b74..0x5b2c67. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern void audio_terminal_ui_scroll_to_view_44ea2e(uint32_t, uint32_t);
extern void audio_terminal_list_anim_new_start_58c622(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_ui_list_view_mode_set_5b0edc(uint32_t, uint32_t, const char *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_action_main_page_selected";
static const char disabled[] = "AI cue display is disabled, skip main selected";
static const char disabled_compact[] =
    "[conversate.ui]AI cue display is disabled, skip main selected";
static const char missing[] = "Main selected skipped: no valid selectable button";
static const char missing_compact[] =
    "[conversate.ui]Main selected skipped: no valid selectable button";
static const char reason[] = "main selected";

static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}
static void put_word(volatile uint8_t *state, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(state + offset) = value;
}

uint32_t audio_conversate_ui_route_5b2b74(uint32_t ignored_a, uint32_t ignored_b) {
    (void)ignored_a;
    (void)ignored_b;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t list = word(ui, 0x64u);
    const uint32_t first = list ? audio_lv_child_44dce2(list, 0u) : 0u;
    const uint32_t selected = word(ui, 0x7cu);
    if (selected == 0u && ui[0x8cu] == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x113u, disabled);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u,
                                        disabled_compact, disabled_compact);
        return UINT32_MAX;
    }
    const uint32_t target = selected ? selected : first;
    const uint32_t index = selected ? UINT32_MAX : 0u;
    if (target == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x11bu, missing);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u,
                                        missing_compact, missing_compact);
        return UINT32_MAX;
    }
    if (first != 0u) audio_terminal_ui_scroll_to_view_44ea2e(first, 0u);
    audio_terminal_list_anim_new_start_58c622(target, 250u, 0u);
    put_word(ui, 0x80u, target);
    put_word(ui, 0x84u, index);
    ui[0x96u] = 1u;
    audio_conversate_ui_list_view_mode_set_5b0edc(2u, 1u, reason);
    return 0u;
}
