/* Apollo Main Conversate list layout refresh, native 0x5b0d86..0x5b0edb. */
#include <stdint.h>

extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *);
extern void audio_lv_delete_44d7b8(uint32_t);
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_ui_style_5b0ac4(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f6d6(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_conversate_list_view_apply_5b0d24(uint32_t, uint32_t);

static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}
static void put_word(volatile uint8_t *state, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(state + offset) = value;
}

void audio_conversate_ui_main_list_layout_5b0d86(void) {
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t app = audio_conversate_ui_app_id_200743a0;
    if (app == 0u || word(ui, 0x64u) == 0u) return;
    const uint32_t old = word(ui, 0x68u);
    if (old != 0u && audio_terminal_ui_object_valid_43e2ea((void *)(uintptr_t)old) != 0u)
        audio_lv_delete_44d7b8(old);
    const uint32_t root = audio_uart_page_43de82(app);
    put_word(ui, 0x68u, root);
    audio_uart_buffer_zero((void *)(ui + 0x6cu), 0x10u, 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_conversate_ui_style_5b0ac4(root, 0u, 0u);
    audio_uart_page_43dfa4(root, 0x12u);
    for (uint32_t i = 0u; i < 4u; ++i) {
        const uint32_t row = audio_uart_page_43de82(root);
        put_word(ui, 0x6cu + i * 4u, row);
        audio_uart_page_43f09a(row, 0u, i * 0x28u);
        audio_uart_page_43f4c0(row, 0x1b8u, 0x28u);
        audio_uart_page_44127e(row, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(row, 0xffu, 0u);
        audio_uart_page_44131c(row, 0u, 0u);
        audio_uart_page_44146a(row, 0u, 0u);
        audio_conversate_ui_style_5b0ac4(row, 0u, 0u);
        audio_uart_page_43dfa4(row, 0x12u);
    }
    audio_uart_page_43f4c0(root, 0x1b8u, 0xa0u);
    audio_uart_page_43f6d6(root, word(ui, 0x64u), 1u, 0u);
    audio_conversate_list_view_apply_5b0d24((uint32_t)(uintptr_t)ui, ui[0x97u]);
}
