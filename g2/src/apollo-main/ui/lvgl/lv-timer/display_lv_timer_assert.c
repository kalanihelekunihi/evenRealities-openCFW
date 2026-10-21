/* Native null branch inside lv_timer_pause 0x464512. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
static const char function[]="lv_timer_pause";
static const char format[]="Asserted at expression: %s (%s)";
static const char condition[]="timer != NULL";
static const char reason[]="NULL pointer";
void audio_uart_lv_assert_null(void) {
    audio_uart_lvgl_log(3u,source,0xccu,function,format,condition,reason);
    for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
}
