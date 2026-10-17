/* Native Conversate UI display-config route 0x5b3398..0x5b349b. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_ui_app_id_200743a0;
extern void audio_conversate_ui_child_style_clear_5b3340(uint32_t);
extern void audio_lv_delete_44d7b8(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_lv_child_count_44ddea(uint32_t);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern void audio_conversate_ui_slot_fade_5b1072(uint32_t, uint32_t);
extern void audio_conversate_ui_list_view_mode_set_5b0edc(uint32_t, uint32_t,
                                                             const char *);

static const char display_config[] = "display config";

static uint32_t word(const volatile uint8_t *ui, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(ui + offset);
}
static void put_word(volatile uint8_t *ui, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(ui + offset) = value;
}
static void show_reset(uint32_t object) {
    audio_uart_page_43dfa4(object, 1u);
    audio_uart_display_audio_reset_441488(object, 0xffu, 0u);
}

uint32_t audio_conversate_ui_route_5b3398(uint32_t state, uint32_t value) {
    (void)value;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    audio_conversate_ui_child_style_clear_5b3340(
        audio_conversate_ui_app_id_200743a0);
    if ((uint8_t)state == 4u || (uint8_t)state == 5u) {
        const uint32_t old = word(ui, 0x1cu);
        if (old != 0u) {
            audio_lv_delete_44d7b8(old);
            put_word(ui, 0x1cu, 0u);
        }
    }
    const uint32_t menu = word(ui, 0x64u);
    if (ui[0x8cu] != 0u)
        show_reset(menu);
    else
        audio_uart_page_43ded4(menu, 1u);
    const uint32_t secondary = word(ui, 0x20u);
    if (ui[0x8du] != 0u)
        audio_uart_page_43dfa4(secondary, 1u);
    else
        audio_uart_page_43ded4(secondary, 1u);
    show_reset(word(ui, 8u));
    const uint32_t count = audio_lv_child_count_44ddea(menu);
    for (uint32_t index = 0u; (uint8_t)index < (uint8_t)count; ++index) {
        const uint32_t child = audio_lv_child_44dce2(menu, (uint8_t)index);
        if (child != 0u) {
            show_reset(child);
            audio_conversate_ui_slot_fade_5b1072(child, 0u);
        }
    }
    put_word(ui, 0x80u, 0u);
    put_word(ui, 0x84u, 0u);
    ui[0x96u] = 0u;
    audio_conversate_ui_list_view_mode_set_5b0edc(0u, 0u, display_config);
    const uint32_t footer = word(ui, 0x7cu);
    if (footer != 0u) {
        show_reset(footer);
        audio_conversate_ui_slot_fade_5b1072(footer, 0u);
    }
    return 0u;
}
