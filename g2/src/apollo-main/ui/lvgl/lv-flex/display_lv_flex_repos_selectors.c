/* Native LVGL flex child style selectors used by track and reposition loops. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
#define STYLE(name,id) int32_t name(void *o,uint32_t s){return (int32_t)audio_uart_lv_style_property_44bdea(o,s,id);}
STYLE(audio_uart_lv_flex_height_start_48b982,0x18u)
STYLE(audio_uart_lv_flex_height_end_48b98c,0x19u)
STYLE(audio_uart_lv_flex_width_start_48b996,0x1au)
STYLE(audio_uart_lv_flex_width_end_48b9a0,0x1bu)
uint32_t audio_uart_lv_flex_x_ofs_48b946(void *o,uint32_t s)
{return audio_uart_lv_style_property_44bdea(o,s,0x6cu);}
uint32_t audio_uart_lv_flex_y_ofs_48b950(void *o,uint32_t s)
{return audio_uart_lv_style_property_44bdea(o,s,0x6du);}
uint32_t audio_uart_lv_flex_grow_48b9fc(void *o,uint32_t s)
{return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,0x7eu);}
