/* Native FT_Atan2 0x528fbc and FT_Vector_Length 0x529086. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern int32_t audio_uart_font_vector_normalize(Vector *); /* 0x528e18 */
extern void audio_uart_font_vector_angle_core(Vector *); /* 0x528ee4 */
extern int32_t audio_uart_font_vector_shrink(int32_t); /* 0x528db8 */

int32_t audio_uart_font_vector_angle(int32_t x,int32_t y) {
    if((x|y)==0) return 0;
    Vector v={x,y};
    (void)audio_uart_font_vector_normalize(&v);
    audio_uart_font_vector_angle_core(&v);
    return v.y;
}

int32_t audio_uart_font_vector_length(const Vector *vector) {
    if(vector==0) return 0;
    Vector v=*vector;
    if(v.x==0) return (int32_t)(v.y<0?0u-(uint32_t)v.y:(uint32_t)v.y);
    if(v.y==0) return (int32_t)(v.x<0?0u-(uint32_t)v.x:(uint32_t)v.x);
    int32_t shift=audio_uart_font_vector_normalize(&v);
    audio_uart_font_vector_angle_core(&v);
    uint32_t scaled=(uint32_t)audio_uart_font_vector_shrink(v.x);
    if(shift>=1) {
        uint32_t round=1u<<((uint32_t)(shift-1)&31u);
        return (int32_t)((int32_t)(scaled+round)>>((uint32_t)shift&31u));
    }
    return (int32_t)(scaled<<((uint32_t)(-shift)&31u));
}
