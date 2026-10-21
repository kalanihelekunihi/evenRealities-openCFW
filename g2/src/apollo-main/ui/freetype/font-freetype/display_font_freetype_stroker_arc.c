/* Native FT_Stroker_Cap 0x5688b8: round, square and butt cap paths.
 * Polar-vector and border-add geometry remain typed native children. */
#include <stdint.h>
typedef struct {int32_t x,y;} Vector;
extern void audio_uart_font_vector_from_polar(Vector *,uint32_t,uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_stroker_border_add(void *,const Vector *,uint32_t); /* 0x5683f2 */
extern int32_t audio_uart_font_stroker_round_cap(void *,uint32_t); /* 0x568870 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
int32_t audio_uart_font_stroker_arc(void *stroker,uint32_t angle,uint32_t side) {
    uint8_t *s=(uint8_t *)stroker;
    uint8_t cap=s[0x29u];
    if(cap==1u) {
        store(s,0u,angle);
        store(s,4u,angle+0xb40000u);
        return audio_uart_font_stroker_round_cap(stroker,side);
    }
    if(cap!=0u&&cap!=2u) return 0;
    uint32_t delta=0x5a0000u-0xb40000u*side;
    uint32_t radius=word(s,0x30u);
    void *border=s+0x34u+side*0x20u;
    if(cap==2u) {
        Vector rotated,forward;
        audio_uart_font_vector_from_polar(&rotated,radius,angle+delta);
        audio_uart_font_vector_from_polar(&forward,radius,angle);
        Vector point={(int32_t)((uint32_t)word(s,8u)+(uint32_t)rotated.x+(uint32_t)forward.x),
                      (int32_t)((uint32_t)word(s,12u)+(uint32_t)rotated.y+(uint32_t)forward.y)};
        int32_t error=audio_uart_font_stroker_border_add(border,&point,0u);
        if(error!=0) return error;
        audio_uart_font_vector_from_polar(&rotated,radius,angle-delta);
        audio_uart_font_vector_from_polar(&forward,radius,angle);
        point.x=(int32_t)((uint32_t)word(s,8u)+(uint32_t)rotated.x+(uint32_t)forward.x);
        point.y=(int32_t)((uint32_t)word(s,12u)+(uint32_t)rotated.y+(uint32_t)forward.y);
        return audio_uart_font_stroker_border_add(border,&point,0u);
    }
    Vector rotated;
    audio_uart_font_vector_from_polar(&rotated,radius,angle+delta);
    rotated.x=(int32_t)((uint32_t)word(s,8u)+(uint32_t)rotated.x);
    rotated.y=(int32_t)((uint32_t)word(s,12u)+(uint32_t)rotated.y);
    int32_t error=audio_uart_font_stroker_border_add(border,&rotated,0u);
    if(error!=0) return error;
    audio_uart_font_vector_from_polar(&rotated,radius,angle-delta);
    rotated.x=(int32_t)((uint32_t)word(s,8u)+(uint32_t)rotated.x);
    rotated.y=(int32_t)((uint32_t)word(s,12u)+(uint32_t)rotated.y);
    return audio_uart_font_stroker_border_add(border,&rotated,0u);
}
