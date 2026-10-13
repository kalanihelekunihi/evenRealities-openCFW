#include <stdint.h>
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern void g2_file_heap_error_log(const char *);
extern volatile uint32_t audio_uart_nema_last_submission;
/* Native51400a..51403c: exact semaphore-success gate, native fail-stop, signed submission wait. */
void audio_uart_nema_wait_irq_51400a(void) {
    void *handle=*(void * volatile *)(uintptr_t)0x20074814u;
    if(xQueueSemaphoreTake(handle,1000u)!=1) {
        g2_file_heap_error_log("GPU assert!!! nema_wait_irq timeout!!!\n");
        for(;;) {}
    }
}
int32_t audio_uart_nema_poll_514026(uint32_t submission) {
    while((int32_t)audio_uart_nema_last_submission<(int32_t)submission)
        audio_uart_nema_wait_irq_51400a();
    return 0;
}
