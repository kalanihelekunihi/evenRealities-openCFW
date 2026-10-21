/* Native Conversate menu-list route, 0x5b59fa..0x5b5b95. */
#include <stdint.h>

struct audio_conversate_menu_icon_descriptor;
extern const struct audio_conversate_menu_icon_descriptor audio_conversate_menu_icon_76a2a0;
extern const struct audio_conversate_menu_icon_descriptor audio_conversate_prep_icon_76a47c;
extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_uart_ring_primary_head_cell;
extern void *audio_conversate_reply_list_get_5b43e8(void);
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_menu_style_5b5720(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_44d878(uint32_t);
extern uint32_t audio_lv_label_create_499416(uint32_t);
extern void audio_lv_label_text_49942e(uint32_t, uint32_t);
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_conversate_prep_button_create_5b1150(uint32_t, uint32_t,
                                                             uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_main_list_container_5b12ba(uint32_t);
extern void audio_conversate_ui_slot_fade_5b1072(uint32_t, uint32_t);
extern void audio_terminal_ui_scroll_to_view_44ea2e(uint32_t, uint32_t);

static const char select_key[] = "ID_CONVERSATE_SELECT_PREP_NOTES";
static const char skip_key[] = "ID_CONVERSATE_SKIP_N_START";

static uint32_t word(const volatile uint8_t *p, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(p + offset);
}
static void put_word(volatile uint8_t *p, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(p + offset) = value;
}

uint32_t audio_conversate_ui_route_5b59fa(uint32_t state, uint32_t value) {
    (void)value;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint8_t *const replies = audio_conversate_reply_list_get_5b43e8();
    if ((uint8_t)state == 0u) {
        const uint32_t root = audio_uart_page_43de82(audio_conversate_ui_app_id_200743a0);
        put_word(ui, 4u, root);
        audio_uart_page_43f4c0(root, 0x240u, 0x120u);
        audio_uart_page_43f09a(root, 0u, 0u);
        audio_uart_page_44129e(root, 0u, 0u);
        audio_uart_page_44131c(root, 0u, 0u);
        audio_uart_page_44146a(root, 0u, 0u);
        audio_conversate_menu_style_5b5720(root, 0u, 0u);
        audio_uart_page_43dfa4(root, 0x10u);
    }
    const uint32_t root = word(ui, 4u);
    audio_uart_page_44d878(root);
    const uint32_t label = audio_lv_label_create_499416(root);
    const uint32_t select_len = audio_uart_page_460084(select_key);
    audio_lv_label_text_49942e(label, audio_uart_page_45fffe(select_key, select_len));
    audio_uart_page_43f4c0(label, 0x3fffffffu, 0x2cu);
    audio_uart_page_43f09a(label, 0xcu, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x00ffffffu), 0u);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44145a(label, 2u, 0u);
    const uint32_t skip_len = audio_uart_page_460084(skip_key);
    const uint32_t skip_text = audio_uart_page_45fffe(skip_key, skip_len);
    const uint32_t skip_button = audio_conversate_prep_button_create_5b1150(
        root, (uint32_t)(uintptr_t)&audio_conversate_menu_icon_76a2a0,
        skip_text, 0u);
    put_word(ui, 0x7cu, skip_button);
    audio_uart_page_43f09a(skip_button, 0u, 0x3cu);
    if (*(const uint16_t *)(const void *)replies == 0u) {
        put_word(ui, 0x80u, skip_button);
        put_word(ui, 0x84u, UINT32_MAX);
        audio_conversate_ui_slot_fade_5b1072(skip_button, 1u);
        return 0u;
    }
    const uint32_t list = audio_conversate_ui_main_list_container_5b12ba(root);
    put_word(ui, 0x64u, list);
    audio_uart_page_43f09a(list, 0u, 0x64u);
    const uint16_t count = *(const uint16_t *)(const void *)replies;
    for (uint32_t i = 0u; i < count; ++i) {
        const uint8_t *const item = replies + i * 0x88u;
        const uint32_t button = audio_conversate_prep_button_create_5b1150(
            list, (uint32_t)(uintptr_t)&audio_conversate_prep_icon_76a47c,
            (uint32_t)(uintptr_t)(item + 0xau), 0u);
        if (button != 0u && word(replies, 0xaa4u) == word(item, 4u)) {
            put_word(ui, 0x80u, button);
            put_word(ui, 0x84u, i);
            audio_conversate_ui_slot_fade_5b1072(button, 1u);
        }
    }
    if (word(ui, 0x80u) != 0u) {
        audio_terminal_ui_scroll_to_view_44ea2e(word(ui, 0x80u), 0u);
    } else {
        put_word(ui, 0x80u, skip_button);
        put_word(ui, 0x84u, UINT32_MAX);
        audio_conversate_ui_slot_fade_5b1072(skip_button, 1u);
    }
    return 0u;
}
