/* Native FT_Vector_From_Polar 0x5290fa. Rotation remains native child0x529006. */
#include <stdint.h>
extern void audio_uart_font_vector_rotate(void *,uint32_t); /* 0x529006 */
void audio_uart_font_vector_from_polar(void *vector,uint32_t length,uint32_t angle) {
    if(vector==0) return;
    uint32_t *v=(uint32_t *)vector;
    v[0]=length;v[1]=0u;
    audio_uart_font_vector_rotate(vector,angle);
}
