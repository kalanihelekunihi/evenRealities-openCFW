/* Native lv_draw_buf_create_ex 0x48b010 and size helper 0x48b86c. */
#include <stdint.h>
extern void *audio_uart_lv_heap_alloc(uint32_t); /* 0x44f730 */
extern void audio_uart_lv_heap_free(void *); /* 0x44f758 */
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t); /* 0x48aad8 */
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548; descriptor +0xc8 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
static const char function[]="lv_draw_buf_create_ex";
static const char assert_two[]="Asserted at expression: %s (%s)";
static const char nonnull[]="draw_buf != NULL";
static const char oom[]="Out of memory";
static const char alloc_error[]="No memory: %ux%u, cf: %d, stride: %u, %uByte, ";
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void s(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
static uint32_t image_size(uint32_t width,uint32_t height,uint8_t format,uint32_t stride) {
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,format);
    uint32_t bytes=height*stride;
    if(format==20u) return bytes+height*(stride>>1u);
    if(format>=7u&&format<=10u) {
        const uint32_t extra=format==7u?2u:format==8u?4u:format==9u?16u:256u;
        return bytes+extra*4u;
    }
    return bytes;
}
void *audio_uart_font_bitmap_allocate(void *device,uint32_t width,uint32_t height,
                                      uint8_t format,uint32_t stride) {
    uint8_t *buffer=(uint8_t *)audio_uart_lv_heap_alloc(28u);
    if(buffer==0) {
        audio_uart_lvgl_log(3u,source,0x145u,function,assert_two,nonnull,oom);
        for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
    }
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,format);
    uint32_t bytes=image_size(width,height,format,stride);
    void *pixels=0;
    uint32_t callback=w(device,0u);
    if(callback!=0u) pixels=((void *(*)(uint32_t,uint8_t))(uintptr_t)callback)(bytes,format);
    if(pixels==0) {
        audio_uart_lvgl_log(2u,source,0x152u,function,alloc_error,
                            width,height,(uint32_t)format,stride,bytes);
        audio_uart_lv_heap_free(buffer);
        return 0;
    }
    s(buffer,4u,(w(buffer,4u)&0xffff0000u)|(width&0xffffu));
    s(buffer,4u,(w(buffer,4u)&0x0000ffffu)|((height&0xffffu)<<16u));
    s(buffer,0u,(w(buffer,0u)&0xffff00ffu)|((uint32_t)format<<8u));
    s(buffer,0u,(w(buffer,0u)&0x0000ffffu)|(0x30u<<16u));
    s(buffer,8u,(w(buffer,8u)&0xffff0000u)|(stride&0xffffu));
    s(buffer,0u,(w(buffer,0u)&0xffffff00u)|0x19u);
    uint8_t *descriptor=audio_uart_display_lv_state+0xc8u;
    uint32_t palette_callback=w(descriptor,8u);
    uint32_t palette=palette_callback==0u?0u:
        ((uint32_t (*)(void *,uint8_t))(uintptr_t)palette_callback)(pixels,format);
    s(buffer,16u,palette);
    s(buffer,20u,(uint32_t)(uintptr_t)pixels);
    s(buffer,12u,bytes);
    s(buffer,24u,(uint32_t)(uintptr_t)device);
    return buffer;
}
