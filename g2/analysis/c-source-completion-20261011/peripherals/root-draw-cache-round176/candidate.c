#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern void audio_uart_lv_draw_full_area_48b8d8(void *,void *);
extern void audio_uart_lv_area_set_450b5c(void *,uint32_t,uint32_t,uint32_t,uint32_t);
static void cache_assert(uint32_t line,const char *name,const char *expression) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    audio_uart_lvgl_log(3u,source,line,name,"Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Native48ab30..48abb8. Cached handler table; callback freshly reread. */
void audio_uart_lv_draw_invalidate_cache_48ab30(void *buffer,const void *area) {
    volatile uint32_t *b=buffer;
    if(!b)cache_assert(121u,"lv_draw_buf_invalidate_cache","draw_buf != NULL");
    if(!b[6])cache_assert(122u,"lv_draw_buf_invalidate_cache","draw_buf->handlers != NULL");
    volatile uint32_t *h=(void *)(uintptr_t)b[6];
    if(h[3]) {
        uint32_t full[4];
        if(!area){audio_uart_lv_draw_full_area_48b8d8(buffer,full);area=full;}
        uint32_t callback=h[3];
        ((void (*)(void *,const void *))(uintptr_t)callback)(buffer,area);
    }
}
/* Native48abb8..48ac40. Same contract, flush slot at handlerword4. */
void audio_uart_lv_draw_flush_cache_48abb8(void *buffer,const void *area) {
    volatile uint32_t *b=buffer;
    if(!b)cache_assert(143u,"lv_draw_buf_flush_cache","draw_buf != NULL");
    if(!b[6])cache_assert(144u,"lv_draw_buf_flush_cache","draw_buf->handlers != NULL");
    volatile uint32_t *h=(void *)(uintptr_t)b[6];
    if(h[4]) {
        uint32_t full[4];
        if(!area){audio_uart_lv_draw_full_area_48b8d8(buffer,full);area=full;}
        uint32_t callback=h[4];
        ((void (*)(void *,const void *))(uintptr_t)callback)(buffer,area);
    }
}
/* Native48b8d8..48b8f6. Fresh height then width header reads, uint16 zero wraps. */
void audio_uart_lv_draw_full_area_48b8d8(void *buffer,void *area) {
    const volatile uint32_t *b=buffer;
    uint32_t y2=(b[1]>>16)-1u;
    uint32_t x2=(uint16_t)b[1]-1u;
    audio_uart_lv_area_set_450b5c(area,0u,0u,x2,y2);
}
