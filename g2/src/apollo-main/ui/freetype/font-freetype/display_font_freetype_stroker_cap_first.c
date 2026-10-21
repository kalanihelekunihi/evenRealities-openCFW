/* Native FT_Stroker_Inside 0x5689e6: bounded miter intersection or
 * radius-offset fallback, with stock call and active-flag ordering. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern int32_t audio_uart_font_stroker_angle_diff(int32_t,int32_t); /* 0x52910e */
extern int32_t audio_uart_font_vector_tan(int32_t); /* 0x528fa8 */
extern int32_t audio_uart_font_vector_cos(int32_t); /* 0x528f8c */
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t); /* 0x5246f8 */
extern int32_t audio_uart_font_divide_metric(int32_t,int32_t); /* 0x524754 */
extern void audio_uart_font_vector_from_polar(Vector *,uint32_t,uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_stroker_border_add(void *,const Vector *,uint32_t); /* 0x5683f2 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
int32_t audio_uart_font_stroker_cap_first(void *stroker,uint8_t side,uint32_t length) {
    uint8_t *s=(uint8_t *)stroker;
    uint8_t *border=s+0x34u+(uint32_t)side*0x20u;
    uint32_t offset=0x5a0000u-(uint32_t)side*0xb40000u;
    int32_t turn=audio_uart_font_stroker_angle_diff((int32_t)word(s,0u),
                                                     (int32_t)word(s,4u));
    int32_t half=turn/2;
    uint32_t radius=word(s,0x30u);
    uint8_t use_intersection=0u;
    if(border[16u]!=0u&&length!=0u&&
       (uint32_t)((uint32_t)half+0x59c000u)<0xb38001u) {
        int32_t tangent=audio_uart_font_vector_tan(half);
        int32_t scaled=audio_uart_font_scale_metric(radius,tangent);
        uint32_t distance=(uint32_t)(scaled<0?0u-(uint32_t)scaled:(uint32_t)scaled);
        if(distance!=0u&&(int32_t)word(s,16u)>=(int32_t)distance&&
           (int32_t)length>=(int32_t)distance)
            use_intersection=1u;
    }
    Vector point;
    if(use_intersection==0u) {
        audio_uart_font_vector_from_polar(&point,radius,offset+word(s,4u));
        border[16u]=0u;
    } else {
        int32_t cosine=audio_uart_font_vector_cos(half);
        int32_t reach=audio_uart_font_divide_metric((int32_t)radius,cosine);
        audio_uart_font_vector_from_polar(&point,(uint32_t)reach,
                                           offset+word(s,0u)+(uint32_t)half);
    }
    point.x=(int32_t)((uint32_t)point.x+word(s,8u));
    point.y=(int32_t)((uint32_t)point.y+word(s,12u));
    return audio_uart_font_stroker_border_add(border,&point,0u);
}
