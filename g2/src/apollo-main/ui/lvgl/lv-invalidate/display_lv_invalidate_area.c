/* Native LVGL lv_obj_invalidate_area 0x4405d4. The visible-area test and
 * render invalidator remain genuine children, not success substitutes. */
#include <stdint.h>

extern void *audio_uart_lv_display_for_object(void *); /* 0x44dc0a */
extern uint32_t audio_uart_lv_display_has_active_window(void *); /* 0x44fed2 */
extern uint32_t audio_uart_lv_visible_area(void *,const int32_t *); /* 0x4406c4 */
extern void audio_uart_lv_render_invalidate(void *,const int32_t *); /* 0x4534be */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char function[]="lv_obj_invalidate_area";
static const char asserted[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char null_pointer[]="NULL pointer";

void audio_uart_display_invalidate_area(void *object,const int32_t *input) {
    if(object==0) {
        audio_uart_lvgl_log(3u,source_path,824u,function,asserted,expression,null_pointer);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    void *display=audio_uart_lv_display_for_object(object);
    if(audio_uart_lv_display_has_active_window(display)==0u) return;
    int32_t area[4]={input[0],input[1],input[2],input[3]};
    if(audio_uart_lv_visible_area(object,area)==0u) return;
    uint8_t *parent=*(uint8_t **)(void *)((uint8_t *)object+8u);
    if(parent!=0 && ((*(uint16_t *)(void *)(parent+0x32u)>>10u)&3u)==2u) {
        area[0]-=5;
        area[1]-=5;
        area[2]+=5;
        area[3]+=5;
    }
    display=audio_uart_lv_display_for_object(object);
    audio_uart_lv_render_invalidate(display,area);
}
