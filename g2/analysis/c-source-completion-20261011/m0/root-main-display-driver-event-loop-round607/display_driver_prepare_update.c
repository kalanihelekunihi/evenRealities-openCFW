/* Apollo display-buffer lock 0x47381e..0x473869. Candidate. */
#include <stdint.h>
extern void * volatile display_buffer_semaphore; /* source-owned 0x200746bc */
extern int32_t xQueueSemaphoreTake(void *,uint32_t); /* selected 0x441c44 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* selected 0x44d25c */
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\lvgl_ambiq_porting\\lv_ambiq_display.c";
static const char function[]="display_buffer_lock";
static const char missing[]="display buffer semaphore is not initialized!\n";
static const char timeout[]="display buffer transfer timer out!";
void display_driver_prepare_update_47381e(void) {
    void *semaphore=display_buffer_semaphore;
    if(semaphore==0) {
        audio_uart_lvgl_log(3u,path,0x124u,function,missing);
        return;
    }
    if(xQueueSemaphoreTake(semaphore,1000u)==0)
        audio_uart_lvgl_log(3u,path,0x12au,function,timeout);
}
