/* Native LVGL flex track min/max selectors and object margin extents. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
extern int32_t audio_uart_lv_flex_width_start_48b996(void *,uint32_t);
extern int32_t audio_uart_lv_flex_width_end_48b9a0(void *,uint32_t);
extern int32_t audio_uart_lv_flex_height_start_48b982(void *,uint32_t);
extern int32_t audio_uart_lv_flex_height_end_48b98c(void *,uint32_t);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);

int32_t audio_uart_lv_flex_min_width_48b914(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,4u);}
int32_t audio_uart_lv_flex_min_height_48b91e(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,5u);}
int32_t audio_uart_lv_flex_max_width_48b932(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,6u);}
int32_t audio_uart_lv_flex_max_height_48b93c(void *o,uint32_t s)
{return (int32_t)audio_uart_lv_style_property_44bdea(o,s,7u);}
int32_t audio_uart_lv_flex_width_margin_48c7b4(void *o)
{
    int32_t start=audio_uart_lv_flex_width_start_48b996(o,0u);
    int32_t size=audio_uart_lv_obj_width_43fd9e(o);
    int32_t end=audio_uart_lv_flex_width_end_48b9a0(o,0u);
    return (int32_t)((uint32_t)start+(uint32_t)size+(uint32_t)end);
}
int32_t audio_uart_lv_flex_height_margin_48c7d8(void *o)
{
    int32_t start=audio_uart_lv_flex_height_start_48b982(o,0u);
    int32_t size=audio_uart_lv_obj_height_43fdda(o);
    int32_t end=audio_uart_lv_flex_height_end_48b98c(o,0u);
    return (int32_t)((uint32_t)start+(uint32_t)size+(uint32_t)end);
}
