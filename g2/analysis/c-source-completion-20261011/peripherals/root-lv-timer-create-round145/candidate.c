/* Native lv_timer_create464466..4644ee; actual helpers already selected.
 * Non-executable assertion literals authenticated from locked payload. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_prepend_482b12(uint32_t *);
extern uint32_t audio_uart_lv_tick(void);
extern void audio_uart_lv_timer_update_464696(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char timer_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
static const char timer_function[]="lv_timer_create";
static const char timer_format[]="Asserted at expression: %s (%s)";
static const char timer_expression[]="new_timer != NULL";
static const char timer_reason[]="Out of memory";
void *audio_uart_lv_timer_create_464466(void (*callback)(void *),uint32_t period,void *user) {
    volatile uint32_t *timer=audio_uart_lv_list_prepend_482b12((uint32_t *)(void *)(audio_uart_display_lv_root+0x74u));
    if(!timer) {
        audio_uart_lvgl_log(3u,timer_path,170u,timer_function,timer_format,timer_expression,timer_reason);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    timer[0]=period;
    timer[2]=(uint32_t)(uintptr_t)callback;
    timer[4]=UINT32_MAX;
    timer[5]=timer[5]&~1u;
    uint32_t tick=audio_uart_lv_tick();
    timer[1]=tick;
    timer[3]=(uint32_t)(uintptr_t)user;
    timer[5]=timer[5]|2u;
    *(volatile uint8_t *)(audio_uart_display_lv_root+0x83u)=1u;
    audio_uart_lv_timer_update_464696();
    return (void *)timer;
}
