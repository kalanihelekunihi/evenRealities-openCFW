/* Native FT_StrokeBorder_Moveto, 0x568636. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern void audio_uart_font_stroker_border_close(void *,uint32_t); /* 0x56834a */
extern int32_t audio_uart_font_stroker_border_add(void *,const Vector *,uint32_t); /* 0x5683f2 */
int32_t audio_uart_font_stroker_border_move(void *border,const Vector *point) {
    uint8_t *b=(uint8_t *)border;
    if(*(int32_t *)(void *)(b+20u)>=0)
        audio_uart_font_stroker_border_close(border,0u);
    *(uint32_t *)(void *)(b+20u)=*(const uint32_t *)(const void *)b;
    b[16u]=0;
    return audio_uart_font_stroker_border_add(border,point,0u);
}
