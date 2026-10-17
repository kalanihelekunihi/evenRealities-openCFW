/* Apollo Main Conversate menu-page scroll-down route 0x5b5bf0..0x5b5cc7. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern void *audio_conversate_reply_list_get_5b43e8(void);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern uint32_t audio_terminal_session_animate_5896fc(uint32_t, uint32_t,
                                                        uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *,
                                      const char *, ...);

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_menu_page.c";
static const char function[] = "conversate_ui_action_menu_page_scroll_down";
static const char bottom[] =
    "Reached bottom button during scroll, stopping at index %d";
static const char bottom_short[] =
    "[conversate.ui]Reached bottom button during scroll, stopping at index %d";
static const char no_next[] = "No next button found";
static const char no_next_short[] = "[conversate.ui]No next button found";

static uint32_t ui_word(uint32_t offset) {
    const volatile uint8_t *const ui =
        (const volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    return *(const volatile uint32_t *)(const void *)(ui + offset);
}

static void set_ui_word(uint32_t offset, uint32_t value) {
    volatile uint8_t *const ui =
        (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    *(volatile uint32_t *)(void *)(ui + offset) = value;
}

uint32_t audio_conversate_ui_route_5b5bf0(uint32_t state, uint32_t value) {
    (void)state;
    (void)value;
    const uint8_t *const replies = audio_conversate_reply_list_get_5b43e8();
    if (replies == 0 || *(const uint16_t *)(const void *)replies == 0u)
        return 0u;

    const uint32_t index = ui_word(0x84u);
    const uint32_t last =
        (uint32_t)(*(const uint16_t *)(const void *)replies - 1u);
    if ((int32_t)index >= (int32_t)last) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, source, function, 0xe2u,
                               bottom, index);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10400000u, bottom_short,
                                        bottom_short, index);
        return 0u;
    }

    const uint32_t child = audio_lv_child_44dce2(ui_word(0x64u), index + 1u);
    if (child == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0xe8u, no_next);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, no_next_short,
                                        no_next_short);
        return UINT32_MAX;
    }
    (void)audio_terminal_session_animate_5896fc(ui_word(0x80u), child, 200u);
    set_ui_word(0x80u, child);
    set_ui_word(0x84u, index + 1u);
    return 0u;
}
