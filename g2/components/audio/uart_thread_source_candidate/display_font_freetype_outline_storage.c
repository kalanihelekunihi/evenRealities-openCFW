/* Native FT_Outline_Check 0x52798c, Copy 0x5279e0, Translate 0x527b2e.
 * Retains signed count and flag semantics; memory copying uses the selected
 * compiler helper at 0x439be4 through its existing C provider. */
#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
static int16_t half(const void *p,uint32_t offset) {
    return *(const int16_t *)(const void *)((const uint8_t *)p+offset);
}
static uint32_t word(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void store(void *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+offset)=value;
}
int32_t audio_uart_font_outline_check(const void *outline) {
    if(outline==0) return 6;
    int32_t points=half(outline,2u),contours=half(outline,0u);
    if((points|contours)==0) return 0;
    if(points<1||contours<1) return 6;
    const int16_t *ends=(const int16_t *)(uintptr_t)word(outline,12u);
    int32_t previous=-1;
    for(int32_t i=0;i<contours;i++) {
        int32_t end=ends[i];
        if(end<=previous||end>=points) return 6;
        previous=end;
    }
    return previous==points-1?0:6;
}
int32_t audio_uart_font_outline_copy(void *source,void *target) {
    if(source==0||target==0) return 20;
    int32_t points=half(source,2u);
    if(points!=half(target,2u)||half(source,0u)!=half(target,0u)) return 6;
    if(source==target) return 0;
    if(points!=0) {
        audio_uart_checksum_copy((void *)(uintptr_t)word(target,4u),
                                 (const void *)(uintptr_t)word(source,4u),(uint32_t)points*8u);
        audio_uart_checksum_copy((void *)(uintptr_t)word(target,8u),
                                 (const void *)(uintptr_t)word(source,8u),(uint32_t)points);
    }
    int32_t contours=half(source,0u);
    if(contours!=0)
        audio_uart_checksum_copy((void *)(uintptr_t)word(target,12u),
                                 (const void *)(uintptr_t)word(source,12u),(uint32_t)contours*2u);
    store(target,16u,(word(source,16u)&~1u)|(word(target,16u)&1u));
    return 0;
}
void audio_uart_font_outline_translate(void *outline,int32_t dx,int32_t dy) {
    if(outline==0) return;
    int32_t points=half(outline,2u);
    uint8_t *vectors=(uint8_t *)(uintptr_t)word(outline,4u);
    for(uint32_t i=0;(int32_t)(uint16_t)i<points;i++) {
        uint32_t x=word(vectors,i*8u),y=word(vectors,i*8u+4u);
        store(vectors,i*8u,x+(uint32_t)dx);
        store(vectors,i*8u+4u,y+(uint32_t)dy);
    }
}
extern void audio_uart_font_mem_free(void *,void *); /* native 0x529256 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x48949c */
static int32_t outline_done_memory(void *memory,void *outline) { /* 0x527a70 */
    if(outline==0) return 20;
    if(memory==0) return 6;
    if((word(outline,16u)&1u)!=0u) {
        audio_uart_font_mem_free(memory,(void *)(uintptr_t)word(outline,4u));
        store(outline,4u,0u);
        audio_uart_font_mem_free(memory,(void *)(uintptr_t)word(outline,8u));
        store(outline,8u,0u);
        audio_uart_font_mem_free(memory,(void *)(uintptr_t)word(outline,12u));
        store(outline,12u,0u);
    }
    audio_uart_buffer_zero(outline,20u,0u);
    return 0;
}
int32_t audio_uart_font_outline_done(void *library,void *outline) { /* 0x527abc */
    if(library==0) return 33;
    return outline_done_memory((void *)(uintptr_t)word(library,0u),outline);
}
extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *); /* native 0x529148 */
static int32_t outline_new_memory(void *memory,int32_t points,int32_t contours,
                                  void *outline) { /* 0x5278c2 */
    if(memory==0||outline==0) return 6;
    audio_uart_buffer_zero(outline,20u,0u);
    if(contours<0||(uint32_t)points<(uint32_t)contours) return 6;
    if((uint32_t)points>=0x8000u) return 10;
    int32_t error=0;
    void *vectors=audio_uart_font_mem_alloc(memory,points*8,&error);
    store(outline,4u,(uint32_t)(uintptr_t)vectors);
    if(error==0) {
        void *tags=audio_uart_font_mem_alloc(memory,points,&error);
        store(outline,8u,(uint32_t)(uintptr_t)tags);
    }
    if(error==0) {
        void *ends=audio_uart_font_mem_alloc(memory,contours*2,&error);
        store(outline,12u,(uint32_t)(uintptr_t)ends);
    }
    if(error!=0) {
        store(outline,16u,word(outline,16u)|1u);
        (void)outline_done_memory(memory,outline);
        return error;
    }
    *(int16_t *)(void *)((uint8_t *)outline+2u)=(int16_t)points;
    *(int16_t *)(void *)outline=(int16_t)contours;
    store(outline,16u,word(outline,16u)|1u);
    return 0;
}
int32_t audio_uart_font_outline_new(void *library,int32_t points,int32_t contours,
                                    void *outline) { /* 0x52797a */
    if(library==0) return 33;
    return outline_new_memory((void *)(uintptr_t)word(library,0u),points,contours,outline);
}
