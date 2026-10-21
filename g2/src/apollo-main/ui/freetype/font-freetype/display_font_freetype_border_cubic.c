/* Native FT_StrokeBorder_CubicTo, 0x5684c2. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern int32_t audio_uart_font_stroker_border_grow(void *,uint32_t); /* 0x5682de */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
int32_t audio_uart_font_stroker_border_cubic(void *border,const Vector *first,
                                             const Vector *second,const Vector *end) {
    uint8_t *b=(uint8_t *)border;
    int32_t error=audio_uart_font_stroker_border_grow(border,3u);
    if(error==0) {
        uint32_t n=word(b,0u);
        Vector *points=(Vector *)(void *)(uintptr_t)word(b,8u);
        uint8_t *tags=(uint8_t *)(uintptr_t)word(b,12u);
        points[n]=*first;points[n+1u]=*second;points[n+2u]=*end;
        tags[n]=2u;tags[n+1u]=2u;tags[n+2u]=1u;
        *(uint32_t *)(void *)b=n+3u;
    }
    b[16u]=0;
    return error;
}
