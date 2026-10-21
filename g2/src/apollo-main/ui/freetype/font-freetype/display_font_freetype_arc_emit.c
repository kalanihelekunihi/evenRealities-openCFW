/* Native FT_StrokeBorder_Arcto 0x56851e. Bezier emission and fixed-point
 * trigonometric children retain their authenticated native interfaces. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern void audio_uart_font_vector_from_polar(Vector *,uint32_t,uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_vector_cos(int32_t); /* 0x528f8c */
extern int32_t audio_uart_font_vector_sin(int32_t); /* 0x528f9a */
extern int32_t audio_uart_font_mul_div(int32_t,int32_t,int32_t); /* 0x524606 */
extern int32_t audio_uart_font_stroker_border_cubic(void *,const Vector *,
                                                    const Vector *,const Vector *); /* 0x5684c2 */
static Vector sum(Vector a,Vector b) {
    Vector r={(int32_t)((uint32_t)a.x+(uint32_t)b.x),
              (int32_t)((uint32_t)a.y+(uint32_t)b.y)};
    return r;
}
int32_t audio_uart_font_stroker_arc_emit(void *border,const Vector *center,
                                         uint32_t radius,uint32_t angle,
                                         int32_t sweep) {
    Vector current;
    audio_uart_font_vector_from_polar(&current,radius,angle);
    current=sum(current,*center);
    int32_t direction=sweep<0?-0x5a0000:0x5a0000;
    int32_t remain=sweep;
    while(remain!=0) {
        int32_t step=remain;
        if(step>=0x5a0001) step=0x5a0000;
        if(step<-0x5a0000) step=-0x5a0000;
        uint32_t next_angle=angle+(uint32_t)step;
        Vector control_a,control_b,next;
        audio_uart_font_vector_from_polar(&next,radius,next_angle);
        next=sum(*center,next);
        int32_t half=(step<0?-step:step)>>1;
        int32_t cosine=audio_uart_font_vector_cos(half);
        int32_t sine=audio_uart_font_vector_sin(half);
        int32_t denominator=(int32_t)((uint32_t)(cosine+65536)*3u);
        int32_t tangent=audio_uart_font_mul_div((int32_t)radius,
                                                  (int32_t)((uint32_t)sine<<2u),
                                                  denominator);
        audio_uart_font_vector_from_polar(&control_a,(uint32_t)tangent,
                                          angle+(uint32_t)direction);
        control_a=sum(current,control_a);
        audio_uart_font_vector_from_polar(&control_b,(uint32_t)tangent,
                                          next_angle-(uint32_t)direction);
        control_b=sum(next,control_b);
        int32_t error=audio_uart_font_stroker_border_cubic(border,&control_a,
                                                            &control_b,&next);
        if(error!=0) return error;
        current=next;
        remain=(int32_t)((uint32_t)remain-(uint32_t)step);
        angle=next_angle;
    }
    return 0;
}
