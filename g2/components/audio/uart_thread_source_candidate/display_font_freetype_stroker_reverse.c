/* Native FT_Stroker_ReverseBorder 0x569532: transfer current right border
 * points/tags into left border in reverse, preserving cap tag semantics. */
#include <stdint.h>
extern int32_t audio_uart_font_stroker_border_grow(void *,uint32_t); /* 0x5682de */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
int32_t audio_uart_font_stroker_reverse(void *stroker,uint32_t suppress_caps) {
    uint8_t *left=(uint8_t *)stroker+0x34u;
    uint8_t *right=(uint8_t *)stroker+0x54u;
    uint32_t right_count=word(right,0u),right_start=word(right,20u);
    uint32_t count=right_count-right_start;
    if((int32_t)count<1) return 0;
    int32_t error=audio_uart_font_stroker_border_grow(left,count);
    if(error!=0) return error;
    uint32_t left_count=word(left,0u);
    uint8_t *left_points=(uint8_t *)(uintptr_t)word(left,8u);
    uint8_t *right_points=(uint8_t *)(uintptr_t)word(right,8u);
    uint8_t *left_tags=(uint8_t *)(uintptr_t)word(left,12u);
    uint8_t *right_tags=(uint8_t *)(uintptr_t)word(right,12u);
    for(uint32_t i=0;i<count;i++) {
        uint32_t from=right_count-1u-i,to=left_count+i;
        store(left_points,to*8u,word(right_points,from*8u));
        store(left_points,to*8u+4u,word(right_points,from*8u+4u));
        uint8_t tag=right_tags[from];
        if((tag&12u)==4u||(tag&12u)==8u) tag^=12u;
        if((uint8_t)suppress_caps!=0u) tag&=0xf3u;
        left_tags[to]=tag;
    }
    store(right,0u,right_start);
    store(left,0u,left_count+count);
    left[16u]=0u;right[16u]=0u;
    return 0;
}
