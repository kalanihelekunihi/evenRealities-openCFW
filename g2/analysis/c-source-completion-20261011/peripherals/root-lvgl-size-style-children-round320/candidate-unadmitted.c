/* Complete native style leaves: native selectors agree with pinned LVGL lv_style.h.
 * Area copy43ee94..43eea4 intentionally retains interleaved load/store for overlap. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
int32_t audio_uart_lv_style_width_43eea6(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,1u);}
int32_t audio_uart_lv_style_min_width_43eeb0(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,4u);}
int32_t audio_uart_lv_style_max_width_43eeba(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,5u);}
int32_t audio_uart_lv_style_height_43eec4(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,2u);}
int32_t audio_uart_lv_style_min_height_43eece(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,6u);}
int32_t audio_uart_lv_style_max_height_43eed8(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,7u);}
int32_t audio_uart_lv_style_margin_top_43ef70(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,24u);}
int32_t audio_uart_lv_style_margin_bottom_43ef7a(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,25u);}
int32_t audio_uart_lv_style_margin_left_43ef84(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,26u);}
int32_t audio_uart_lv_style_margin_right_43ef8e(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,27u);}
uint8_t audio_uart_lv_style_base_dir_43efba(void *object,uint32_t selector)
{return (uint8_t)audio_uart_lv_style_property_44bdea(object,selector,39u);}
void audio_uart_lv_area_copy_43ee94(void *destination,const void *source)
{
 volatile uint32_t *d=destination;
 const volatile uint32_t *s=source;
 d[0]=s[0]; d[1]=s[1]; d[2]=s[2]; d[3]=s[3];
}
