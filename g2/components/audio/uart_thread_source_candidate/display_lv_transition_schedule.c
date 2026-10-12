/* Native LVGL transition timer selection 0x4509da and resume/update
 * descendants 0x46453e/0x464696; product LV root is live RAM. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_first(void *); /* selected 0x482cd8 */
extern void audio_uart_lv_timer_pause(void *); /* selected 0x46450c */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
void audio_uart_lv_timer_update_464696(void) {
    uint8_t *root=audio_uart_display_lv_root;
    uint32_t zero=0u;__builtin_memcpy(root+0x84u,&zero,4u);
    void (*callback)(void *)=*(void (**)(void *))(void *)(root+0x9cu);
    if(callback!=0) {
        void *argument=*(void **)(void *)(root+0xa0u);
        callback(argument);
    }
}
void audio_uart_lv_timer_resume_46453e(void *timer) {
    if(timer==0) {
        audio_uart_lvgl_log(3u,path,0xd2u,"lv_timer_resume",
                            "Asserted at expression: %s (%s)","timer != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint8_t *t=(uint8_t *)timer;
    uint32_t flags;__builtin_memcpy(&flags,t+0x14u,4u);
    flags&=~1u;__builtin_memcpy(t+0x14u,&flags,4u);
    audio_uart_lv_timer_update_464696();
}
void audio_uart_lv_transition_schedule_4509da(void) {
    uint8_t *root=audio_uart_display_lv_root;
    root[0xa4u]=1u;
    void *timer=*(void **)(void *)(root+0xa8u);
    if(audio_uart_lv_list_first(root+0xacu)==0)
        audio_uart_lv_timer_pause(timer);
    else audio_uart_lv_timer_resume_46453e(timer);
}
