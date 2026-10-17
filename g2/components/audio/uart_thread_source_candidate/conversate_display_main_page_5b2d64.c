/* Apollo Main Conversate display-main-page route, 0x5b2d64..0x5b30c7. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint8_t audio_conversate_machine_context_200e3aec[];
extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */
extern const uint8_t audio_conversate_title_label_5b3334[];
struct audio_conversate_icon_descriptor;
extern const struct audio_conversate_icon_descriptor audio_conversate_prep_icon_76a47c;
extern void *audio_conversate_prep_note_get_5b4766(void);
extern void audio_lv_delete_44d7b8(uint32_t);
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f6b8(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_display_style_5b22bc(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_display_tick_5b22ee(void);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern uint32_t audio_conversate_pre_notes_anim_create_58c7a0(uint32_t, uint32_t);
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_lv_label_create_499416(uint32_t);
extern void audio_lv_label_text_49942e(uint32_t, uint32_t);
extern void audio_lv_label_mode_499678(uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f6d6(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_conversate_route_scroll_5b22fa(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_main_list_container_5b12ba(uint32_t);
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);
extern uint32_t audio_conversate_prep_button_create_5b1150(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4411aa(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441386(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44e368(uint32_t, uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern void audio_uart_page_499678(uint32_t, uint32_t);
extern void audio_uart_page_49942e(uint32_t, uint32_t);
extern void audio_uart_page_44144c(uint32_t, int32_t, uint32_t);
extern void audio_uart_page_43f6ac(uint32_t, uint32_t);
extern void audio_conversate_ui_main_list_layout_5b0d86(void);
extern void audio_uart_page_58c238(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_action_display_main_page";
static const char stopped[] = "display main page but app not running";
static const char stopped_compact[] =
    "[conversate.ui]display main page but app not running";
static const char prep_id[] = "ID_CONVERSATE_PREP_NOTES";

static uint32_t word(const volatile uint8_t *bytes, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(bytes + offset);
}
static void put_word(volatile uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(bytes + offset) = value;
}

uint32_t audio_conversate_ui_route_5b2d64(uint32_t ignored, uint32_t elapsed,
                                            uint32_t other, uint32_t detail) {
    (void)ignored;
    (void)other;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const volatile uint8_t *const notes =
        (const volatile uint8_t *)audio_conversate_prep_note_get_5b4766();
    if (audio_conversate_machine_context_200e3aec[0] != 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x161u, stopped, detail);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u, stopped_compact,
                                        stopped_compact);
        return UINT32_MAX;
    }
    if (word(ui, 12u) != 0u) {
        audio_lv_delete_44d7b8(word(ui, 12u));
        put_word(ui, 12u, 0u);
    }
    if (word(ui, 4u) != 0u) {
        audio_lv_delete_44d7b8(word(ui, 4u));
        put_word(ui, 4u, 0u);
        put_word(ui, 0x84u, 0u);
        put_word(ui, 0x80u, 0u);
        put_word(ui, 0x7cu, 0u);
        put_word(ui, 0x64u, 0u);
    }
    const uint32_t root = audio_uart_page_43de82(audio_conversate_ui_app_id_200743a0);
    put_word(ui, 8u, root);
    audio_uart_page_43f4c0(root, 0x240u, 0xccu);
    audio_uart_page_43f6b8(root, 2u, 0u, 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_conversate_display_style_5b22bc(root, 0u, 0u);
    audio_uart_page_43dfa4(root, 0x70u);

    const uint32_t header = audio_uart_page_43de82(root);
    put_word(ui, 0x10u, header);
    audio_uart_page_43f4c0(header, 0x3fffffffu, 0x1cu);
    audio_uart_page_43f6b8(header, 3u, UINT32_MAX - 11u, 8u);
    audio_uart_page_44129e(header, 0u, 0u);
    audio_uart_page_44131c(header, 0u, 0u);
    audio_uart_page_44146a(header, 0u, 0u);
    audio_conversate_display_style_5b22bc(header, 0u, 0u);
    const uint32_t indicator = audio_conversate_pre_notes_anim_create_58c7a0(
        header, (uint32_t)(uintptr_t)audio_conversate_display_tick_5b22ee);
    put_word(ui, 0x18u, indicator);
    audio_uart_page_43f4c0(indicator, 0x3fffffffu, 0x3fffffffu);
    audio_uart_page_43f6b8(indicator, 7u, 0u, 0u);
    audio_uart_display_audio_reset_441488(indicator, 0x33u, 0u);
    const uint32_t label = audio_lv_label_create_499416(header);
    put_word(ui, 0x14u, label);
    audio_uart_page_43f4c0(label, 0x3fffffffu, 0x3fffffffu);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0u);
    audio_uart_page_44145a(label, 2u, 0u);
    audio_uart_page_43f6d6(label, indicator, 0x14u, 8u);
    audio_conversate_route_scroll_5b22fa(label, elapsed);
    put_word(ui, 0x9cu, elapsed / 60u);
    const uint32_t list = audio_conversate_ui_main_list_container_5b12ba(root);
    put_word(ui, 0x64u, list);
    if (*(const volatile uint16_t *)(const void *)notes == 0u || word(notes, 0x84u) == 0u) {
        audio_uart_page_43f6b8(list, 2u, 0u, 0u);
    } else {
        const uint32_t item = audio_uart_page_45fffe(
            prep_id, audio_uart_page_460084(prep_id));
        const uint32_t button = audio_conversate_prep_button_create_5b1150(
            root, (uint32_t)(uintptr_t)&audio_conversate_prep_icon_76a47c, item, 0u);
        put_word(ui, 0x7cu, button);
        audio_uart_page_43f6b8(button, 1u, 0u, 0u);
        audio_uart_page_43f6d6(list, button, 13u, 0u);
    }
    const uint32_t footer = audio_uart_page_43de82(audio_conversate_ui_app_id_200743a0);
    put_word(ui, 0x20u, footer);
    audio_uart_page_43f4c0(footer, 0x240u, 0x3fffffffu);
    audio_uart_page_4411aa(footer, 0x54u, 0u);
    audio_uart_page_43f6b8(footer, 5u, 0u, 0u);
    audio_uart_page_44129e(footer, 0u, 0u);
    audio_uart_page_44131c(footer, 0u, 0u);
    audio_uart_page_44146a(footer, 0u, 0u);
    audio_uart_page_441386(footer, 0u, 0u);
    audio_conversate_display_style_5b22bc(footer, 0u, 0u);
    audio_uart_page_44e368(footer, 0u);
    audio_uart_page_43ded4(footer, 0x10u);
    audio_uart_page_43dfa4(footer, 0x360u);
    const uint32_t footer_label = audio_lv_label_create_499416(footer);
    audio_uart_page_49942e(footer_label,
                           (uint32_t)(uintptr_t)audio_conversate_title_label_5b3334);
    audio_uart_page_44140e(footer_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f4c0(footer_label, 0x240u, 0x3fffffffu);
    audio_lv_label_mode_499678(footer_label, 0u);
    audio_uart_page_44145a(footer_label, 1u, 0u);
    const uint32_t font = audio_uart_ring_primary_head_cell;
    audio_uart_page_44143e(footer_label, font, 0u);
    audio_uart_page_44144c(footer_label,
        0x1c - *(const int32_t *)(uintptr_t)(font + 12u), 0u);
    audio_uart_page_43f6ac(footer_label, 4u);
    if (ui[0x8du] == 0u) audio_uart_page_43ded4(footer, 1u);
    if (ui[0x8cu] == 0u) audio_uart_page_43ded4(list, 1u);
    audio_conversate_ui_main_list_layout_5b0d86();
    audio_uart_page_58c238(root, 250u, 0u);
    return 0u;
}
