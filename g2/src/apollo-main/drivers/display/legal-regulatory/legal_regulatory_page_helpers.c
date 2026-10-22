/* LegalRegulatory page construction helpers: stock 0x5bf114, 0x5bf24e,
 * 0x5bf298, 0x5bf2f8 plus three missing LV style setters. */
#include <stdint.h>

extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44120e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44121c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44122a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_498668(uint32_t);
extern void audio_uart_page_498680(uint32_t, const void *);
extern uint32_t audio_uart_page_499416(uint32_t);
extern void audio_uart_page_49942e(uint32_t, const void *);
extern void audio_uart_page_style_apply_44be4c(void *, uint8_t, uint32_t, uint32_t);
extern uint32_t audio_uart_ring_primary_head_cell;


/* Retired: stock 0x4413ce is upstream lv_obj_set_style_image_opa (lvgl/src/core/lv_obj_style_gen.c); this name is a link alias. */
void audio_uart_page_4413ce(uint32_t object, uint32_t value, uint32_t selector);

/* Retired: stock 0x44144c is upstream lv_obj_set_style_text_line_space (lvgl/src/core/lv_obj_style_gen.c); this name is a link alias. */
void audio_uart_page_44144c(uint32_t object, uint32_t value, uint32_t selector);

void audio_legal_regulatory_zero_styles_5bf114(uint32_t object,
                                                 uint32_t value,
                                                 uint32_t selector) {
    audio_uart_page_44122a(object, value, selector);
    audio_uart_page_441238(object, value, selector);
    audio_uart_page_44120e(object, value, selector);
    audio_uart_page_44121c(object, value, selector);
}

uint32_t audio_legal_regulatory_panel_5bf24e(uint32_t parent) {
    uint32_t panel = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(panel, 0x3fffffffu, 0x3fffffffu);
    audio_legal_regulatory_zero_styles_5bf114(panel, 0u, 0u);
    audio_uart_page_44131c(panel, 0u, 0u);
    audio_uart_page_44146a(panel, 0u, 0u);
    audio_uart_page_44129e(panel, 0u, 0u);
    audio_uart_page_43dfa4(panel, 0x370u);
    return panel;
}

uint32_t audio_legal_regulatory_label_5bf298(uint32_t parent,
                                               const void *text) {
    uint32_t label = audio_uart_page_499416(parent);
    audio_uart_page_43f4c0(label, 0x3fffffffu, 0x3fffffffu);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
    uint32_t font = audio_uart_ring_primary_head_cell;
    audio_uart_page_44143e(label, font, 0u);
    audio_uart_page_44144c(label, 0x1cu - *(const uint32_t *)(uintptr_t)(font + 0xcu), 0u);
    audio_uart_page_44145a(label, 1u, 0u);
    audio_uart_page_49942e(label, text);
    return label;
}

uint64_t audio_legal_regulatory_icon_5bf2f8(uint32_t parent,
                                              const void *asset,
                                              uint32_t unused,
                                              uint32_t high_return) {
    (void)unused;
    uint32_t icon = audio_uart_page_498668(parent);
    audio_uart_page_498680(icon, asset);
    audio_uart_page_44127e(icon, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(icon, 0xffu, 0u);
    audio_uart_page_4413ce(icon, 0xffu, 0u);
    return ((uint64_t)high_return << 32) | icon;
}
