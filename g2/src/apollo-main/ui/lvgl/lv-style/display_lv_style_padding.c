/* Native43efc6/43eff4/43f022/43f050: space is style padding plus
 * border width iff the native uint8 side mask includes that edge.
 * All sums wrap as native 32-bit ADD; provider call order is preserved. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
static int32_t space(void *object,uint32_t selector,uint32_t property,uint32_t side)
{
    uint32_t padding=audio_uart_lv_style_property_44bdea(object,selector,property);
    uint32_t border=audio_uart_lv_style_property_44bdea(object,selector,48u);
    uint8_t sides=(uint8_t)audio_uart_lv_style_property_44bdea(object,selector,52u);
    return (int32_t)(padding+((sides&side)!=0u?border:0u));
}
int32_t audio_uart_lv_style_pad_left_43efc6(void *o,uint32_t s,uint32_t r2,uint32_t r3)
{ (void)r2;(void)r3;return space(o,s,18u,4u); }
int32_t audio_uart_lv_style_pad_right_43eff4(void *o,uint32_t s)
{ return space(o,s,19u,8u); }
int32_t audio_uart_lv_style_pad_top_43f022(void *o,uint32_t s,uint32_t r2,uint32_t r3)
{ (void)r2;(void)r3;return space(o,s,16u,2u); }
int32_t audio_uart_lv_style_pad_bottom_43f050(void *o,uint32_t s)
{ return space(o,s,17u,1u); }
