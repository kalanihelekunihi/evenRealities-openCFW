/* Native FT_StrokeBorder_Grow 0x5682de. */
#include <stdint.h>
extern void *audio_uart_font_mem_realloc_items(void *,int32_t,int32_t,int32_t,
                                                void *,int32_t *); /* 0x52919c */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
int32_t audio_uart_font_stroker_border_grow(void *border,uint32_t additional) {
    uint32_t old_capacity=word(border,4u);
    uint32_t required=word(border,0u)+additional;
    if(old_capacity>=required) return 0;
    uint32_t capacity=old_capacity;
    while(capacity<required) capacity+=capacity/2u+16u;
    void *memory=(void *)(uintptr_t)word(border,24u);
    int32_t error=0;
    void *points=audio_uart_font_mem_realloc_items(memory,8,(int32_t)old_capacity,
                           (int32_t)capacity,(void *)(uintptr_t)word(border,8u),&error);
    store(border,8u,(uint32_t)(uintptr_t)points);
    if(error!=0) return error;
    void *tags=audio_uart_font_mem_realloc_items(memory,1,(int32_t)old_capacity,
                           (int32_t)capacity,(void *)(uintptr_t)word(border,12u),&error);
    store(border,12u,(uint32_t)(uintptr_t)tags);
    if(error==0) store(border,4u,capacity);
    return error;
}
