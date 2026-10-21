/* ABI adapters from Terminal row calls to existing C-owned stock-address providers. */
#include <stdint.h>

extern uint32_t audio_uart_lv_child_get_44dce2(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_child_count_44ddea(uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_delete_event_filter_44d7b8(uint32_t);
extern uint32_t audio_uart_page_498668(uint32_t);
extern void audio_uart_page_498680(uint32_t, uint32_t);
extern uint32_t audio_uart_page_499416(uint32_t);
extern void audio_uart_page_layout_499678(uint32_t, uint32_t);
extern void audio_uart_page_49942e(uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44142e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44144c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);

uint32_t audio_lv_child_44dce2(uint32_t a, uint32_t b) { return audio_uart_lv_child_get_44dce2(a, b); }
uint32_t audio_lv_child_count_44ddea(uint32_t a) { return audio_uart_lv_child_count_44ddea(a); }
uint32_t audio_lv_color_44104c(uint32_t a) { return audio_uart_page_44104c(a); }
void audio_lv_delete_44d7b8(uint32_t a) { audio_uart_page_delete_event_filter_44d7b8(a); }
uint32_t audio_lv_image_create_498668(uint32_t a) { return audio_uart_page_498668(a); }
void audio_lv_image_source_498680(uint32_t a, uint32_t b) { audio_uart_page_498680(a, b); }
uint32_t audio_lv_label_create_499416(uint32_t a) { return audio_uart_page_499416(a); }
void audio_lv_label_mode_499678(uint32_t a, uint32_t b) { audio_uart_page_layout_499678(a, b); }
void audio_lv_label_text_49942e(uint32_t a, uint32_t b) { audio_uart_page_49942e(a, b); }
void audio_lv_style_a_44145a(uint32_t a, uint32_t b, uint32_t c) { audio_uart_page_44145a(a, b, c); }
void audio_lv_style_alpha_44142e(uint32_t a, uint32_t b, uint32_t c) { audio_uart_page_44142e(a, b, c); }
void audio_lv_style_color_44140e(uint32_t a, uint32_t b, uint32_t c) { audio_uart_page_44140e(a, b, c); }
void audio_lv_style_font_44143e(uint32_t a, uint32_t b, uint32_t c) { audio_uart_page_44143e(a, b, c); }
void audio_lv_style_opa_441488(uint32_t a, uint32_t b, uint32_t c) { audio_uart_display_audio_reset_441488(a, b, c); }
void audio_lv_style_spacing_44144c(uint32_t a, uint32_t b, uint32_t c) { audio_uart_page_44144c(a, b, c); }
void audio_lv_width_43f506(uint32_t a, uint32_t b) { audio_uart_page_43f506(a, b); }
