/* Native LV flex style accessors, selected style-property ABI 0x44bdea. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);

uint32_t audio_uart_lv_flex_flow_48b9cc(void *o,uint32_t s)
{return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,0x7au);}
uint8_t audio_uart_lv_flex_main_place_48b9d8(void *o,uint32_t s)
{return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,0x7bu);}
uint8_t audio_uart_lv_flex_cross_place_48b9e4(void *o,uint32_t s)
{return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,0x7cu);}
uint8_t audio_uart_lv_flex_track_place_48b9f0(void *o,uint32_t s)
{return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,0x7du);}
uint32_t audio_uart_lv_flex_base_dir_48b9c0(void *o,uint32_t s)
{return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,0x27u);}
int32_t audio_uart_lv_flex_pad_column_48b96e(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,0x14u);}
int32_t audio_uart_lv_flex_pad_row_48b978(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,0x15u);}
int32_t audio_uart_lv_flex_width_48b90a(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,1u);}
int32_t audio_uart_lv_flex_height_48b928(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,2u);}
extern int32_t audio_uart_lv_flex_space_top_base_48b95a(void *,uint32_t);
extern int32_t audio_uart_lv_flex_space_left_base_48b964(void *,uint32_t);
extern int32_t audio_uart_lv_flex_space_offset_48b9aa(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_space_flags_48b9b4(void *,uint32_t);
int32_t audio_uart_lv_flex_space_top_48ba36(void *o,uint32_t s)
{
    int32_t base=audio_uart_lv_flex_space_top_base_48b95a(o,s);
    int32_t offset=audio_uart_lv_flex_space_offset_48b9aa(o,s);
    if(audio_uart_lv_flex_space_flags_48b9b4(o,s)&2u)
        base=(int32_t)((uint32_t)base+(uint32_t)offset);
    return base;
}
int32_t audio_uart_lv_flex_space_left_48ba08(void *o,uint32_t s)
{
    int32_t base=audio_uart_lv_flex_space_left_base_48b964(o,s);
    int32_t offset=audio_uart_lv_flex_space_offset_48b9aa(o,s);
    if(audio_uart_lv_flex_space_flags_48b9b4(o,s)&4u)
        base=(int32_t)((uint32_t)base+(uint32_t)offset);
    return base;
}
