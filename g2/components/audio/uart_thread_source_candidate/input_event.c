/* Native input-event forwarder 0x4445a4: 10-byte little-endian record,
 * protected ring write, then 12-byte display-queue notice. */
#include <stdint.h>

extern void *audio_uart_input_mutex; /* *DAT_004448a0 */
extern void *audio_uart_input_queue; /* *DAT_004448a4 */
extern void *audio_uart_input_ring; /* DAT_004448b0 */
extern const void *audio_uart_input_queue_failure_context; /* DAT_004448b4 */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected 0x44981c */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t audio_uart_input_ring_write(void *,const void *,uint32_t); /* 0x46d8c4 */
extern int32_t audio_ble_hci_boot_log_4733ee(const void *,...); /* selected 0x4733ee */
extern void audio_delay_scheduler_assert(void); /* 0x5fa0a4 */

uint32_t audio_uart_input_event(uint32_t id,uint32_t field4,uint32_t field8) {
    uint8_t bytes[10];
    bytes[0]=(uint8_t)id;bytes[1]=(uint8_t)(id>>8);
    for(uint32_t i=0;i<4u;i++) {
        bytes[2u+i]=(uint8_t)(field4>>(8u*i));
        bytes[6u+i]=(uint8_t)(field8>>(8u*i));
    }
    (void)audio_file_mutex_acquire(audio_uart_input_mutex,UINT32_MAX);
    (void)audio_uart_input_ring_write(audio_uart_input_ring,bytes,10u);
    (void)audio_file_mutex_release(audio_uart_input_mutex);
    uint32_t notice[3]={7u,0u,10u};
    if(audio_cmsis_queue_put(audio_uart_input_queue,notice,0u,1000u)!=0) {
        (void)audio_ble_hci_boot_log_4733ee(audio_uart_input_queue_failure_context);
        audio_delay_scheduler_assert();
        for(;;) __asm volatile("nop");
    }
    return 0u;
}
