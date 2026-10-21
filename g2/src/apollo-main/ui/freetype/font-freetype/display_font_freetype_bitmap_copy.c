/* Native FT_Bitmap_Copy 0x58ed2e; pinned FreeType 2.9.1 ftbitmap.c. */
#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439be4 */
extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *); /* 0x529176 */
extern void *audio_uart_font_mem_realloc_raw(void *,int32_t,int32_t,int32_t,
                                              void *,int32_t *); /* 0x5291e4 */
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void s(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
int32_t audio_uart_font_bitmap_copy(void *library,const void *source,void *target) {
    if(!library) return 0x21;
    if(!source||!target) return 6;
    if(source==target) return 0;
    int32_t src_pitch=(int32_t)w(source,8u);
    int32_t dst_pitch=(int32_t)w(target,8u);
    int32_t src_sign=src_pitch<0?-1:1;
    int32_t dst_sign=dst_pitch<0?-1:1;
    if(w(source,12u)==0u) {
        audio_uart_checksum_copy(target,source,24u);
        if(src_sign!=dst_sign) s(target,8u,0u-w(target,8u));
        return 0;
    }
    void *memory=(void *)(uintptr_t)w(library,0u);
    uint32_t pitch=(uint32_t)(src_pitch<0?0u-(uint32_t)src_pitch:(uint32_t)src_pitch);
    uint32_t size=w(source,0u)*pitch;
    void *buffer=(void *)(uintptr_t)w(target,12u);
    int32_t error=0;
    if(buffer!=0) {
        int32_t old_pitch=(int32_t)w(target,8u);
        uint32_t old_width=(uint32_t)(old_pitch<0?0u-(uint32_t)old_pitch:(uint32_t)old_pitch);
        uint32_t old_size=w(target,0u)*old_width;
        if(old_size!=size) buffer=audio_uart_font_mem_realloc_raw(memory,1,(int32_t)old_size,
                                           (int32_t)size,buffer,&error);
    } else buffer=audio_uart_font_mem_alloc(memory,(int32_t)size,&error);
    s(target,12u,(uint32_t)(uintptr_t)buffer);
    if(error!=0) return error;
    audio_uart_checksum_copy(target,source,24u);
    s(target,12u,(uint32_t)(uintptr_t)buffer);
    if(src_sign==dst_sign) audio_uart_checksum_copy(buffer,
                                  (const void *)(uintptr_t)w(source,12u),size);
    else {
        const uint8_t *from=(const uint8_t *)(uintptr_t)w(source,12u);
        uint8_t *to=(uint8_t *)buffer+(w(target,0u)-1u)*pitch;
        for(uint32_t row=w(target,0u);row!=0u;row--) {
            audio_uart_checksum_copy(to,from,pitch);
            from+=pitch;
            to-=pitch;
        }
    }
    return 0;
}
