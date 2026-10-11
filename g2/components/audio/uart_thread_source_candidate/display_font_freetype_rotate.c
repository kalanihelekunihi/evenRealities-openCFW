/* Native FT_Vector_Rotate 0x529006. Its CORDIC, normalize and shrink
 * children are source-defined in the same selected Audio archive. */
#include <stdint.h>
typedef struct {int32_t x,y;} Vector;
extern int32_t audio_uart_font_vector_normalize(Vector *); /* 0x528e18 */
extern void audio_uart_font_vector_rotate_core(Vector *,uint32_t); /* 0x528e5a */
extern int32_t audio_uart_font_vector_shrink(int32_t); /* 0x528db8 */
void audio_uart_font_vector_rotate(void *vector,uint32_t angle) {
    if(vector==0||angle==0u) return;
    Vector value=*(Vector *)vector;
    if((value.x|value.y)==0) return;
    int32_t shift=audio_uart_font_vector_normalize(&value);
    audio_uart_font_vector_rotate_core(&value,angle);
    value.x=audio_uart_font_vector_shrink(value.x);
    value.y=audio_uart_font_vector_shrink(value.y);
    if(shift>=1) {
        uint32_t bias=1u<<((uint32_t)(shift-1)&31u);
        uint32_t x=(uint32_t)value.x+bias+(uint32_t)(value.x>>31);
        uint32_t y=(uint32_t)value.y+bias+(uint32_t)(value.y>>31);
        ((Vector *)vector)->x=(int32_t)x>>((uint32_t)shift&31u);
        ((Vector *)vector)->y=(int32_t)y>>((uint32_t)shift&31u);
    } else {
        uint32_t left=(uint32_t)(-shift)&31u;
        ((Vector *)vector)->x=(int32_t)((uint32_t)value.x<<left);
        ((Vector *)vector)->y=(int32_t)((uint32_t)value.y<<left);
    }
}
