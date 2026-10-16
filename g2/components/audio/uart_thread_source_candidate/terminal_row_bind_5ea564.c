/* Stock Terminal row text and image binding at 0x5ea564. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */
extern uint32_t audio_lv_child_44dce2(uint32_t parent, uint32_t index);
extern uint32_t audio_lv_child_count_44ddea(uint32_t parent);
extern uint32_t audio_lv_label_create_499416(uint32_t parent);
extern uint32_t audio_lv_image_create_498668(uint32_t parent);
extern void audio_uart_page_43f09a(uint32_t object, uint32_t x, uint32_t y);
extern void audio_lv_width_43f506(uint32_t object, uint32_t width);
extern void audio_lv_label_mode_499678(uint32_t object, uint32_t mode);
extern void audio_lv_style_a_44145a(uint32_t object, uint32_t value, uint32_t selector);
extern void audio_lv_style_font_44143e(uint32_t object, uint32_t font, uint32_t selector);
extern void audio_lv_style_spacing_44144c(uint32_t object, uint32_t spacing, uint32_t selector);
extern uint32_t audio_terminal_row_color_5ea2f2(uint32_t item);
extern void audio_lv_label_text_49942e(uint32_t object, uint32_t text);
extern uint32_t audio_lv_color_44104c(uint32_t rgb);
extern void audio_lv_style_color_44140e(uint32_t object, uint32_t color, uint32_t selector);
extern void audio_lv_style_alpha_44142e(uint32_t object, uint32_t alpha, uint32_t selector);
extern uint32_t audio_terminal_row_image_5ea524(uint32_t index, uint32_t item);
extern void audio_lv_image_source_498680(uint32_t object, uint32_t image);
extern uint32_t audio_terminal_image_y_5ea2b0(void);
extern void audio_lv_style_opa_441488(uint32_t object, uint32_t value, uint32_t selector);
extern void audio_lv_delete_44d7b8(uint32_t object);
extern int32_t audio_terminal_item_spacing_5ea2c2(void);

void audio_terminal_row_bind_5ea564(uint32_t parent, uint32_t item, uint32_t index) {
    if (parent == 0u || item == 0u)
        return;
    uint32_t label = audio_lv_child_44dce2(parent, 0u);
    if (label == 0u) {
        label = audio_lv_label_create_499416(parent);
        audio_uart_page_43f09a(label, 0x1cu, 0u);
        audio_lv_width_43f506(label, 0x21au);
        audio_lv_label_mode_499678(label, 0u);
        audio_lv_style_a_44145a(label, 1u, 0u);
        audio_lv_style_font_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_lv_style_spacing_44144c(label, (uint32_t)audio_terminal_item_spacing_5ea2c2(), 0u);
    }
    uint32_t colored = audio_terminal_row_color_5ea2f2(item);
    audio_lv_label_text_49942e(label, item + 2u);
    uint32_t rgb = colored != 0u ? 0x00333333u : 0x00ffffffu;
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(rgb), 0u);
    audio_lv_style_alpha_44142e(label, 0xffu, 0u);
    uint32_t image = audio_lv_child_count_44ddea(parent) >= 2u
        ? audio_lv_child_44dce2(parent, 1u) : 0u;
    uint32_t source = audio_terminal_row_image_5ea524((uint16_t)index, item);
    if (source != 0u) {
        if (image == 0u)
            image = audio_lv_image_create_498668(parent);
        audio_lv_image_source_498680(image, source);
        audio_uart_page_43f09a(image, 8u, audio_terminal_image_y_5ea2b0());
        audio_lv_style_opa_441488(image, colored != 0u ? 0x33u : 0xffu, 0u);
    } else if (image != 0u) {
        audio_lv_delete_44d7b8(image);
    }
}
