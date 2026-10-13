/* Complete native content-sizing helper bodies, source-backed lv_obj_pos.c/lv_style.h. */
#include <stdint.h>
#include <stddef.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);
int32_t audio_uart_lv_style_x_43eee2(void *o,uint32_t s){return (int32_t)audio_uart_lv_style_property_44bdea(o,s,8u);}
int32_t audio_uart_lv_style_y_43eeec(void *o,uint32_t s){return (int32_t)audio_uart_lv_style_property_44bdea(o,s,9u);}
uint8_t audio_uart_lv_style_align_43eef6(void *o,uint32_t s){return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,10u);}
uint32_t audio_uart_lv_layout_positioned_43f612(void *o)
{
 if(audio_uart_lv_obj_has_flag_any_43e11c(o,0x60001u))return 0u;
 void *parent=audio_uart_lv_obj_parent_44dca2(o);
 if(parent==NULL)return 0u;
 return (uint16_t)audio_uart_lv_style_property_44bdea(parent,0u,22u)!=0u;
}
int32_t audio_uart_lv_self_width_43ff44(void *o)
{
 int32_t size[2]={0,(int32_t)0xe0000001u};
 (void)audio_uart_lv_obj_event_451670(o,52u,size);
 return size[0];
}
int32_t audio_uart_lv_self_height_43ff5e(void *o)
{
 int32_t size[2]={(int32_t)0xe0000001u,0};
 (void)audio_uart_lv_obj_event_451670(o,52u,size);
 return size[1];
}
