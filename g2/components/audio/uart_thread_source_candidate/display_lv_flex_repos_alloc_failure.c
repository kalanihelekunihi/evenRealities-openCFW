/* Native children_repos assertion 0x48c1xx: exhausted grow weight. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\layouts\\flex\\lv_flex.c";
static const char function[]="children_repos";
static const char format[]="Asserted at expression: %s";
static const char expression[]="grow_value_sum != 0";

_Noreturn void audio_uart_lv_flex_repos_alloc_failure(void)
{
    audio_uart_lvgl_log(3u,source,0x16fu,function,format,expression);
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
