/* Stock Terminal empty-list subtree constructor at 0x5ea342. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */
extern uint32_t audio_uart_page_43de82(uint32_t parent);
extern void audio_uart_page_43f4c0(uint32_t object, uint32_t width, uint32_t height);
extern void audio_uart_page_43f09a(uint32_t object, uint32_t x, uint32_t y);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flags);
extern void audio_uart_page_44129e(uint32_t object, uint32_t value, uint32_t selector);
extern void audio_uart_page_44131c(uint32_t object, uint32_t value, uint32_t selector);
extern void audio_terminal_lv_style_four_5ea224(uint32_t object, uint32_t value, uint32_t selector);
extern void audio_uart_page_44146a(uint32_t object, uint32_t value, uint32_t selector);
extern uint32_t audio_uart_page_498668(uint32_t parent);
extern void audio_uart_page_498680(uint32_t object, uint32_t source);
extern void audio_uart_page_43f6b8(uint32_t object, uint32_t index, uint32_t value, uint32_t selector);
extern uint32_t audio_terminal_initial_image_y_5ea2d4(void);
extern uint32_t audio_uart_page_499416(uint32_t parent);
extern void audio_uart_page_43f506(uint32_t object, uint32_t width);
extern void audio_uart_page_layout_499678(uint32_t object, uint32_t mode);
extern void audio_uart_page_49942e(uint32_t object, uint32_t text);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);
extern void audio_uart_page_44140e(uint32_t object, uint32_t color, uint32_t selector);
extern void audio_uart_page_44145a(uint32_t object, uint32_t value, uint32_t selector);
extern void audio_uart_page_44143e(uint32_t object, uint32_t font, uint32_t selector);

static uint32_t state_word(uint32_t offset) {
    return *(uint32_t *)(void *)(audio_terminal_ui_state_base + offset);
}
static void set_state_word(uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(audio_terminal_ui_state_base + offset) = value;
}
static void configure_panel(uint32_t object) {
    audio_uart_page_43dfa4(object, 0x10u);
    audio_uart_page_44129e(object, 0u, 0u);
    audio_uart_page_44131c(object, 0u, 0u);
    audio_terminal_lv_style_four_5ea224(object, 0u, 0u);
    audio_uart_page_44146a(object, 0u, 0u);
}

void audio_terminal_reset_subtree_5ea342(void) {
    uint32_t root = state_word(0u);
    if (root == 0u || state_word(0x1e0u) != 0u)
        return;
    uint32_t panel = audio_uart_page_43de82(root);
    set_state_word(0x1e0u, panel);
    audio_uart_page_43f4c0(panel, 0x240u, 0x120u);
    audio_uart_page_43f09a(panel, 0u, 0u);
    configure_panel(panel);

    uint32_t first_image = audio_uart_page_498668(panel);
    set_state_word(0x1e4u, first_image);
    audio_uart_page_498680(first_image,
                            (uint32_t)(uintptr_t)&audio_terminal_asset_773028);
    audio_uart_page_43f4c0(first_image, 0x3fffffffu, 0x3fffffffu);
    audio_uart_page_43f09a(first_image, 0x1cu, 0x1cu);

    uint32_t second_panel = audio_uart_page_43de82(panel);
    set_state_word(0x1e8u, second_panel);
    audio_uart_page_43f4c0(second_panel, 0x240u, 0x3fffffffu);
    audio_uart_page_43f6b8(second_panel, 4u, 0u, 0xfffffffcu);
    configure_panel(second_panel);

    uint32_t second_image = audio_uart_page_498668(second_panel);
    set_state_word(0x1ecu, second_image);
    audio_uart_page_498680(second_image,
                            (uint32_t)(uintptr_t)&audio_terminal_asset_7733a8);
    audio_uart_page_43f4c0(second_image, 0x3fffffffu, 0x3fffffffu);
    audio_uart_page_43f09a(second_image, 6u,
                            audio_terminal_initial_image_y_5ea2d4());

    uint32_t label = audio_uart_page_499416(second_panel);
    set_state_word(0x1f0u, label);
    audio_uart_page_43f09a(label, 0x1cu, 0u);
    audio_uart_page_43f506(label, 0x224u);
    audio_uart_page_layout_499678(label, 0u);
    audio_uart_page_49942e(label,
                            (uint32_t)(uintptr_t)audio_terminal_welcome_text_7069d0);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x00ffffffu), 0u);
    audio_uart_page_44145a(label, 1u, 0u);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
}
