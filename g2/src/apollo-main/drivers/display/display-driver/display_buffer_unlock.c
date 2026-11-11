/* Apollo display buffer unlock, native 0x47386a..0x4738a7. Candidate. */
#include <stdint.h>
/* display_buffer_semaphore: stock 0x200746bc is one cell; defined as an alias of audio_uart_display_lock (Fix 31). */
extern void * volatile display_buffer_semaphore;
extern void lv_log_add(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern int32_t xQueueGiveFromISR(void *,int32_t *);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\lvgl_ambiq_porting\\lv_ambiq_display.c";
static const char function[]="display_buffer_unlock";
static const char missing[]="display buffer semaphore is not initialized!\n";
void display_driver_case3_sync(void) {
    void *sem=display_buffer_semaphore;
    if(sem==0) {
        lv_log_add(3u,source,0x131u,function,missing);
        return;
    }
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if(ipsr!=0u) {
        (void)xQueueGiveFromISR(sem,0);
    } else {
        (void)audio_uart_queue_send(sem,0,0u,0u);
    }
}
/* Single implementation of stock display_buffer_unlock 0x47386a. */
__typeof__(display_driver_case3_sync) audio_uart_display_flush_end_47386a
    __attribute__((alias("display_driver_case3_sync")));
