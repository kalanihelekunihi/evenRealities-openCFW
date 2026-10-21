/* Native LVGL display invalidation 0x4534be. Rectangle arithmetic and the
 * 32-entry coalescing threshold follow the product's LVGL 9.3 body. */
#include <stdint.h>

extern void *audio_uart_display_default_get(void); /* 0x44fa1a */
extern uint32_t audio_uart_lv_display_has_active_window(void *); /* 0x44fed2 */
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern uint32_t audio_uart_lv_area_contains_450f28(const int32_t *,const int32_t *,uint32_t);
extern void audio_uart_lv_area_copy_4530fc(int32_t *,const int32_t *);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *,uint32_t,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";

void audio_uart_lv_render_invalidate(void *display,const int32_t *input) {
    if(display==0)display=audio_uart_display_default_get();
    if(display==0 || audio_uart_lv_display_has_active_window(display)==0u)return;
    uint8_t *d=(uint8_t *)display;
    if(((*(uint32_t *)(void *)(d+0x38u)>>25u)&1u)!=0u) {
        audio_uart_lvgl_log(3u,path,0x117u,"lv_inv_area",
                            "Asserted at expression: %s (%s)",
                            "!disp->rendering_in_progress",
                            "Invalidate area is not allowed during rendering.");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(input==0) {*(uint32_t *)(void *)(d+0x260u)=0u;return;}
    int32_t clipped[4];
    int32_t screen[4]={0,0,(int32_t)audio_uart_lv_display_width_44fa7e(display)-1,
                           (int32_t)audio_uart_lv_display_height_44faa8(display)-1};
    if((uint8_t)audio_uart_lv_area_intersect_450bcc(clipped,input,screen)==0u)return;
    if(d[0x3cu]==7u) {
        clipped[0]&=~7;clipped[2]|=7;
    }
    if(d[0x39u]==2u) {
        __builtin_memcpy(d+0x40u,screen,16u);
        *(uint32_t *)(void *)(d+0x260u)=1u;
        audio_uart_lv_display_event_44fdbe(display,0x38u,0);
        return;
    }
    if((uint8_t)audio_uart_lv_display_event_44fdbe(display,0x35u,clipped)!=1u)return;
    uint32_t count=*(uint32_t *)(void *)(d+0x260u);
    for(uint32_t i=0;(uint16_t)i<count;i++) {
        if(audio_uart_lv_area_contains_450f28(clipped,(int32_t *)(void *)(d+0x40u+16u*(uint16_t)i),0u)!=0u)return;
    }
    const int32_t *new_area=clipped;
    if(count>=32u) {*(uint32_t *)(void *)(d+0x260u)=0u;count=0u;new_area=screen;}
    audio_uart_lv_area_copy_4530fc((int32_t *)(void *)(d+0x40u+16u*count),new_area);
    *(uint32_t *)(void *)(d+0x260u)=count+1u;
    audio_uart_lv_display_event_44fdbe(display,0x38u,0);
}
