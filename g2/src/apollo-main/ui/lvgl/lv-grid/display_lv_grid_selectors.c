/* Native LVGL grid style selectors and one-step grid-position wrappers. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
#define STYLE(name,property) uint32_t name(void *o,uint32_t s){return audio_uart_lv_style_property_44bdea(o,s,property);}
#define BYTE(name,property) uint8_t name(void *o,uint32_t s){return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,property);}
STYLE(audio_uart_lv_grid_x_ofs_48c82e,0x6cu)
STYLE(audio_uart_lv_grid_y_ofs_48c838,0x6du)
STYLE(audio_uart_lv_basic_vertical_48c856,0x14u)
STYLE(audio_uart_lv_basic_horizontal_48c860,0x15u)
STYLE(audio_uart_lv_grid_y_start_48c86a,0x18u)
STYLE(audio_uart_lv_grid_y_end_48c874,0x19u)
STYLE(audio_uart_lv_grid_x_start_48c87e,0x1au)
STYLE(audio_uart_lv_grid_x_end_48c888,0x1bu)
BYTE(audio_uart_lv_grid_base_dir_48c8a8,0x27u)
STYLE(audio_uart_lv_grid_cols_48c8b4,0x82u)
BYTE(audio_uart_lv_grid_h_mode_48c8be,0x7fu)
STYLE(audio_uart_lv_grid_rows_48c8ca,0x81u)
BYTE(audio_uart_lv_grid_v_mode_48c8d4,0x80u)
STYLE(audio_uart_lv_grid_col_48c8e0,0x83u)
BYTE(audio_uart_lv_grid_x_align_48c8ea,0x85u)
STYLE(audio_uart_lv_grid_col_span_48c8f6,0x84u)
STYLE(audio_uart_lv_grid_row_48c900,0x86u)
BYTE(audio_uart_lv_grid_y_align_48c90a,0x88u)
STYLE(audio_uart_lv_grid_row_span_48c916,0x87u)

uint32_t audio_uart_lv_grid_col_descriptor_48c97c(void *o){return audio_uart_lv_grid_cols_48c8b4(o,0u);}
uint32_t audio_uart_lv_grid_row_descriptor_48c986(void *o){return audio_uart_lv_grid_rows_48c8ca(o,0u);}
uint32_t audio_uart_lv_grid_col_48c990(void *o){return audio_uart_lv_grid_col_48c8e0(o,0u);}
uint32_t audio_uart_lv_grid_row_48c99a(void *o){return audio_uart_lv_grid_row_48c900(o,0u);}
uint32_t audio_uart_lv_grid_col_span_48c9a4(void *o){return audio_uart_lv_grid_col_span_48c8f6(o,0u);}
uint32_t audio_uart_lv_grid_row_span_48c9ae(void *o){return audio_uart_lv_grid_row_span_48c916(o,0u);}
