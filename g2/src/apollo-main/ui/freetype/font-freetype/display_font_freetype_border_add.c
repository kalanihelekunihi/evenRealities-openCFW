/* Native FT_StrokeBorder_Lineto 0x5683f2, including duplicate-point and
 * active-segment replacement behavior. */
#include <stdint.h>
extern int32_t audio_uart_font_stroker_border_grow(void *,uint32_t); /* 0x5682de */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
int32_t audio_uart_font_stroker_border_add(void *border,const void *point,
                                           uint32_t active) {
    uint8_t *b=(uint8_t *)border;
    const uint8_t *p=(const uint8_t *)point;
    uint32_t count=word(b,0u);
    uint8_t *vectors=(uint8_t *)(uintptr_t)word(b,8u);
    if(b[16u]!=0u) {
        uint32_t offset=(count-1u)*8u;
        store(vectors,offset,word(p,0u));
        store(vectors,offset+4u,word(p,4u));
        b[16u]=(uint8_t)active;
        return 0;
    }
    if(count!=0u) {
        uint32_t offset=(count-1u)*8u;
        uint32_t dx=word(vectors,offset)-word(p,0u)+1u;
        uint32_t dy=word(vectors,offset+4u)-word(p,4u)+1u;
        if(dx<3u&&dy<3u) return 0;
    }
    int32_t error=audio_uart_font_stroker_border_grow(border,1u);
    if(error==0) {
        count=word(b,0u);
        vectors=(uint8_t *)(uintptr_t)word(b,8u);
        uint8_t *tags=(uint8_t *)(uintptr_t)word(b,12u);
        store(vectors,count*8u,word(p,0u));
        store(vectors,count*8u+4u,word(p,4u));
        tags[count]=1u;
        store(b,0u,count+1u);
    }
    b[16u]=(uint8_t)active;
    return error;
}
