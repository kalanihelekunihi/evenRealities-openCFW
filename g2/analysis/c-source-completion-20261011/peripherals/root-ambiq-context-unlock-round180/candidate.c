#include <stdint.h>
extern uint32_t audio_uart_lv_unlock_core(void *); /* native4d4696 selected */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Native4b0886..4b092a. Decrement/assert BEFORE unlocking, unlike provider. */
uint32_t audio_uart_ambiq_context_unlock_4b0886(void *unit) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_nema_context_unlock";
    if(!unit) {
        audio_uart_lvgl_log(3u,source,295u,name,"Asserted at expression: %s (%s)","unit != NULL","Ambiq GPU draw unit is not initialized!");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    volatile uint32_t *count=(void *)((uint8_t *)unit+140u);
    *count=*count-1u;
    if(*count) {
        audio_uart_lvgl_log(3u,source,297u,name,"Asserted at expression: %s (%s)","unit->nema_context_lock_count == 0","Ambiq GPU mutex lock count error!");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t result=audio_uart_lv_unlock_core((uint8_t *)unit+132u);
    if((uint8_t)result!=1u)
        audio_uart_lvgl_log(3u,source,301u,name,"Ambiq GPU mutex unlock failed!");
    return (uint8_t)result;
}
