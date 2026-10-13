#include <stdint.h>
extern void audio_uart_lv_mutex_ensure(uint32_t *);
extern int32_t xQueueTakeMutexRecursive(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
uint32_t audio_uart_lv_lock_core(void *cell) {
    uint32_t *mutex=(uint32_t *)cell;
    audio_uart_lv_mutex_ensure(mutex);
    uint32_t ok=(uint32_t)xQueueTakeMutexRecursive((void *)(uintptr_t)mutex[1],UINT32_MAX);
    if(ok!=1u)
        audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\osal\\lv_freertos.c",0x84u,
                            "lv_mutex_lock","xSemaphoreTake failed!");
    return ok==1u;
}
