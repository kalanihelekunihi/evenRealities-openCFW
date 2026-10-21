/* Native FreeType context/outline cleanup 0x4b1fcc/0x52a264 and bitmap
 * release 0x48b216. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_state[]; /* product RAM0x2006f548 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_lv_heap_free(void *);
uint32_t audio_uart_font_outline_dispatch(void *,uint32_t,void *); /* 0x529ea2 */
void audio_uart_font_bitmap_storage_release(void *,void *); /* 0x48b85a */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
void *audio_uart_font_outline_context(void) {
    return *(void **)(void *)(audio_uart_display_lv_state+0x1c0u);
}
void audio_uart_font_outline_release(void *context,void *outline) {
    uint32_t packet[10];
    audio_uart_buffer_zero(packet,0x28u,0u);
    packet[0]=(uint32_t)(uintptr_t)outline;
    audio_uart_font_outline_dispatch(context,0x29u,packet);
}
void audio_uart_font_bitmap_release(void *bitmap) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_destroy";
    if(bitmap==0) {
        audio_uart_lvgl_log(3u,source,0x19eu,function,
                            "Asserted at expression: %s (%s)",
                            "draw_buf != NULL","NULL pointer");
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint32_t *buffer=(uint32_t *)bitmap;
    if((buffer[0]&0x00100000u)!=0u) {
        if(buffer[6]==0u) {
            audio_uart_lvgl_log(3u,source,0x1a3u,function,
                                "Asserted at expression: %s (%s)",
                                "draw_buf->handlers != NULL","NULL pointer");
            for(;;) { /* authenticated native assertion loop */ }
        }
        audio_uart_font_bitmap_storage_release((void *)(uintptr_t)buffer[6],
                                              (void *)(uintptr_t)buffer[5]);
        audio_uart_lv_heap_free(bitmap);
    } else {
        audio_uart_lvgl_log(3u,source,0x1aau,function,
                            "draw buffer is not allocated, ignored");
    }
}
void audio_uart_font_bitmap_storage_release(void *handlers,void *data) { /* native 0x48b85a */
    uint32_t callback=*(uint32_t *)(void *)((uint8_t *)handlers+4u);
    if(callback!=0u) ((void (*)(void *))(uintptr_t)callback)(data);
}
uint32_t audio_uart_font_outline_dispatch(void *context,uint32_t command,void *payload) {
    uint32_t callback=*(uint32_t *)(void *)((uint8_t *)context+0x10u);
    if(callback!=0u) {
        uint32_t event[7];
        audio_uart_buffer_zero(event,0x1cu,0u);
        event[2]=command;
        event[3]=0u;
        event[4]=(uint32_t)(uintptr_t)payload;
        ((void (*)(void *))(uintptr_t)callback)(event);
        return 1u;
    } else {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_outline.c",
            0xe3u,"outline_send_event","event_cb is not set");
        return 0u;
    }
}
