/* Native LV basic-theme style selectors 0x48c842..0x48c89c. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
int32_t audio_uart_lv_basic_y_base_48c842(void *object,uint32_t selector)
{ return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,0x10u); }
int32_t audio_uart_lv_basic_x_base_48c84c(void *object,uint32_t selector)
{ return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,0x12u); }
int32_t audio_uart_lv_basic_offset_48c892(void *object,uint32_t selector)
{ return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,0x30u); }
uint32_t audio_uart_lv_basic_flags_48c89c(void *object,uint32_t selector)
{ return (uint8_t)audio_uart_lv_style_property_44bdea(object,selector,0x34u); }
