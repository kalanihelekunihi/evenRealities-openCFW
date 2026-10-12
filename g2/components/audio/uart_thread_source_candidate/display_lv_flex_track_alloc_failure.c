/* Native 0x48c026..0x48c052 allocation assertion inside find_track_end. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\layouts\\flex\\lv_flex.c";
static const char function[]="find_track_end";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="new_dsc != NULL";
static const char message[]="Out of memory";

_Noreturn void audio_uart_lv_flex_grow_alloc_failure(void)
{
    audio_uart_lvgl_log(3u,source,0x11au,function,format,expression,message);
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
