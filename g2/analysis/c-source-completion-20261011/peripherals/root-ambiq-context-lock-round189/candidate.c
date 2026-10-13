#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Native4b07de..4b0886. Only lowbyte success1 increments the lock count. */
uint32_t audio_uart_ambiq_context_lock_4b07de(void *unit) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_nema_context_lock";
    if(!unit) {
        audio_uart_lvgl_log(3u,source,273u,name,"Asserted at expression: %s (%s)","unit != NULL","Ambiq GPU draw unit is not initialized!");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t result=audio_uart_lv_lock_core((uint8_t *)unit+132u);
    if((uint8_t)result!=1u) {
        audio_uart_lvgl_log(3u,source,277u,name,"Ambiq GPU mutex lock failed!");
    } else {
        volatile uint32_t *count=(void *)((uint8_t *)unit+140u);
        *count=*count+1u;
        if(*count!=1u) {
            audio_uart_lvgl_log(3u,source,282u,name,"Asserted at expression: %s (%s)","unit->nema_context_lock_count == 1","Ambiq GPU mutex lock count error!");
            for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
    }
    return (uint8_t)result;
}
