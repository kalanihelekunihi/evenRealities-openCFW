/* Native FT_Stroker_Outside 0x568abe. Round, bevel and variable-width
 * miter branches retain the original child call/error ordering. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern int32_t audio_uart_font_stroker_round_cap(void *,uint32_t); /* 0x568870 */
extern int32_t audio_uart_font_stroker_angle_diff(int32_t,int32_t); /* 0x52910e */
extern int32_t audio_uart_font_vector_cos(int32_t); /* 0x528f8c */
extern int32_t audio_uart_font_vector_sin(int32_t); /* 0x528f9a */
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t); /* 0x5246f8 */
extern int32_t audio_uart_font_divide_metric(int32_t,int32_t); /* 0x524754 */
extern int32_t audio_uart_font_mul_div(int32_t,int32_t,int32_t); /* 0x524606 */
extern void audio_uart_font_vector_from_polar(Vector *,uint32_t,uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_stroker_border_add(void *,const Vector *,uint32_t); /* 0x5683f2 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static Vector offset_point(const uint8_t *s,uint32_t radius,uint32_t angle) {
    Vector point;
    audio_uart_font_vector_from_polar(&point,radius,angle);
    point.x=(int32_t)((uint32_t)point.x+word(s,8u));
    point.y=(int32_t)((uint32_t)point.y+word(s,12u));
    return point;
}
int32_t audio_uart_font_stroker_cap_second(void *stroker,uint8_t side,
                                            uint32_t length) {
    uint8_t *s=(uint8_t *)stroker;
    uint8_t *border=s+0x34u+(uint32_t)side*0x20u;
    uint8_t join=s[42u];
    if(join==0u) return audio_uart_font_stroker_round_cap(stroker,side);
    uint32_t radius=word(s,0x30u);
    uint32_t perpendicular=0x5a0000u-(uint32_t)side*0xb40000u;
    uint8_t use_fallback=(uint8_t)(join==1u);
    uint8_t use_bevel=(uint8_t)(join!=2u);
    int32_t half=0;
    uint32_t bisector=0u;
    int32_t cosine=0;
    int32_t ratio=0;
    if(use_fallback==0u) {
        int32_t turn=audio_uart_font_stroker_angle_diff((int32_t)word(s,0u),
                                                         (int32_t)word(s,4u));
        if(turn==0xb40000) {
            half=(int32_t)perpendicular;
            bisector=word(s,0u);
        } else {
            half=turn/2;
            bisector=perpendicular+word(s,0u)+(uint32_t)half;
        }
        cosine=audio_uart_font_vector_cos(half);
        ratio=audio_uart_font_scale_metric(word(s,44u),cosine);
        if(ratio<65536 && (use_bevel!=0u ||
            (int32_t)(half<0?0u-(uint32_t)half:(uint32_t)half)>=58))
            use_fallback=1u;
    }
    if(use_fallback!=0u) {
        if(use_bevel!=0u) {
            Vector point=offset_point(s,radius,perpendicular+word(s,4u));
            border[16u]=0u;
            return audio_uart_font_stroker_border_add(border,&point,0u);
        }
        uint32_t outer=(uint32_t)audio_uart_font_scale_metric(radius,
                                                               (int32_t)word(s,44u));
        Vector intersection=offset_point(s,outer,bisector);
        int32_t sine=audio_uart_font_vector_sin(half);
        uint32_t abs_sine=sine<0?0u-(uint32_t)sine:(uint32_t)sine;
        int32_t extend=audio_uart_font_mul_div((int32_t)radius,
                       (int32_t)(65536u-(uint32_t)ratio),(int32_t)abs_sine);
        Vector delta;
        audio_uart_font_vector_from_polar(&delta,(uint32_t)extend,
                                           bisector+perpendicular);
        Vector point={(int32_t)((uint32_t)intersection.x+(uint32_t)delta.x),
                      (int32_t)((uint32_t)intersection.y+(uint32_t)delta.y)};
        int32_t error=audio_uart_font_stroker_border_add(border,&point,0u);
        if(error!=0) return error;
        audio_uart_font_vector_from_polar(&delta,(uint32_t)extend,
                                           bisector-perpendicular);
        point.x=(int32_t)((uint32_t)intersection.x+(uint32_t)delta.x);
        point.y=(int32_t)((uint32_t)intersection.y+(uint32_t)delta.y);
        error=audio_uart_font_stroker_border_add(border,&point,0u);
        if(error!=0||length!=0u) return error;
        point=offset_point(s,radius,perpendicular+word(s,4u));
        return audio_uart_font_stroker_border_add(border,&point,0u);
    }
    int32_t reach=audio_uart_font_divide_metric((int32_t)radius,cosine);
    Vector point=offset_point(s,(uint32_t)reach,bisector);
    int32_t error=audio_uart_font_stroker_border_add(border,&point,0u);
    if(error!=0||length!=0u) return error;
    point=offset_point(s,radius,perpendicular+word(s,4u));
    return audio_uart_font_stroker_border_add(border,&point,0u);
}
