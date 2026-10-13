#include <stdint.h>
extern int32_t g2_thread_create_dynamic(void (*)(void *),const char *,uint16_t,void *,uint32_t,void **);
extern void audio_task_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char lv_thread_message[]="xTaskCreate failed!";
static const char lv_thread_function[]="lv_thread_init";
static const char lv_thread_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\osal\\lv_freertos.c";
/* Native4d4768..4d477a. Native scratchR0 discarded by caller. */
void audio_uart_lv_thread_trampoline_4d4768(void *cell) {
    volatile uint32_t *t=cell;
    void *argument=(void *)(uintptr_t)t[1];
    uint32_t callback=t[0];
    ((void (*)(void *))(uintptr_t)callback)(argument);
    audio_task_delete(0);
}
/* Native4d4610..4d4650: stackbytes>>2 truncated to16-bit depth. */
uint32_t audio_uart_lv_thread_init_4d4610(void *cell,const char *name,uint32_t priority,void (*callback)(void),uint32_t stackbytes,void *argument) {
    volatile uint32_t *t=cell;
    t[1]=(uint32_t)(uintptr_t)argument;
    t[0]=(uint32_t)(uintptr_t)callback;
    int32_t result=g2_thread_create_dynamic(audio_uart_lv_thread_trampoline_4d4768,name,(uint16_t)(stackbytes>>2),cell,(uint8_t)priority,(void **)((uint8_t *)cell+8u));
    if(result!=1) {
        audio_uart_lvgl_log(3u,lv_thread_path,103u,lv_thread_function,lv_thread_message);return 0u;
    }
    return 1u;
}
