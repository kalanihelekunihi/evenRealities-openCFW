/* Entire scrollbar raw-property and input iterator/field getter bodies.
 * Native property IDs/narrowing and root/list/node offsets retained.
 * Pinned LVGL lv_obj_scroll.c, lv_indev.c167/507/514, and lv_ll.c head/next. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
extern uint8_t audio_uart_display_lv_root[];
int32_t audio_uart_lv_style_length_44e226(void *o,uint32_t selector){return (int32_t)audio_uart_lv_style_property_44bdea(o,selector,3u);}
int32_t audio_uart_lv_style_raw_pad_top_44e230(void *o,uint32_t selector){return (int32_t)audio_uart_lv_style_property_44bdea(o,selector,16u);}
int32_t audio_uart_lv_style_raw_pad_bottom_44e23a(void *o,uint32_t selector){return (int32_t)audio_uart_lv_style_property_44bdea(o,selector,17u);}
int32_t audio_uart_lv_style_raw_pad_left_44e244(void *o,uint32_t selector){return (int32_t)audio_uart_lv_style_property_44bdea(o,selector,18u);}
int32_t audio_uart_lv_style_raw_pad_right_44e24e(void *o,uint32_t selector){return (int32_t)audio_uart_lv_style_property_44bdea(o,selector,19u);}
uint8_t audio_uart_lv_style_background_opacity_44e276(void *o,uint32_t selector){return (uint8_t)audio_uart_lv_style_property_44bdea(o,selector,29u);}
uint8_t audio_uart_lv_style_border_opacity_44e282(void *o,uint32_t selector){return (uint8_t)audio_uart_lv_style_property_44bdea(o,selector,50u);}
void *audio_uart_lv_input_next_452edc(void *input)
{
 const volatile uint32_t *list=(const volatile uint32_t *)(audio_uart_display_lv_root+0x44u);
 if(input==0)return (void *)(uintptr_t)list[1];
 uint32_t node_size=list[0];
 return (void *)(uintptr_t)*(const volatile uint32_t *)((uintptr_t)input+node_size+4u);
}
uint32_t audio_uart_lv_input_scroll_direction_452f8c(const void *input)
{
 if(input==0)return 0u;
 const volatile uint8_t *p=(const volatile uint8_t *)input;
 if(p[0]!=1u && p[0]!=3u)return 0u;
 return p[168]&15u;
}
void *audio_uart_lv_input_scroll_object_452fae(const void *input)
{
 if(input==0)return 0;
 const volatile uint8_t *p=(const volatile uint8_t *)input;
 if(p[0]!=1u && p[0]!=3u)return 0;
 return (void *)(uintptr_t)*(const volatile uint32_t *)(p+112);
}
