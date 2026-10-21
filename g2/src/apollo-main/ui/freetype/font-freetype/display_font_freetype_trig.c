/* Native vector unit 0x528fde, cosine 0x528f8c, sine 0x528f9a. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern void audio_uart_font_vector_rotate_core(Vector *,uint32_t); /* 0x528e5a */
extern int32_t audio_uart_font_divide_metric(int32_t,int32_t); /* 0x524754 */
void audio_uart_font_vector_unit(Vector *vector,uint32_t angle) {
    if(vector==0) return;
    vector->x=0xdbd95b;
    vector->y=0;
    audio_uart_font_vector_rotate_core(vector,angle);
    vector->x=(int32_t)((int32_t)((uint32_t)vector->x+128u)>>8);
    vector->y=(int32_t)((int32_t)((uint32_t)vector->y+128u)>>8);
}
int32_t audio_uart_font_vector_cos(int32_t angle) {
    Vector vector;
    audio_uart_font_vector_unit(&vector,(uint32_t)angle);
    return vector.x;
}
int32_t audio_uart_font_vector_sin(int32_t angle) {
    Vector vector;
    audio_uart_font_vector_unit(&vector,(uint32_t)angle);
    return vector.y;
}
int32_t audio_uart_font_vector_tan(int32_t angle) {
    Vector vector;
    audio_uart_font_vector_unit(&vector,(uint32_t)angle);
    return audio_uart_font_divide_metric(vector.y,vector.x);
}
