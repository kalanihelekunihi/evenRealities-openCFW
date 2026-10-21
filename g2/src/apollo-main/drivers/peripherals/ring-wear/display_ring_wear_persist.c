/* Native settings/event persistence gateway 0x48eb32, reached by ring wear. */
#include <stdint.h>
extern volatile uint8_t audio_uart_ring_persist_initialized; /* RAM 0x20075032 */
extern volatile uint8_t audio_uart_ring_persist_wake_pending; /* RAM 0x20075037 */
extern volatile uint8_t audio_uart_ring_persist_wake_blocked; /* RAM 0x20075036 */
extern uint8_t audio_uart_ring_persist_queue_state[]; /* RAM 0x200771f4 */
extern void audio_uart_ring_persist_initialize_48eac8(void); /* native 0x48eac8 */
extern void audio_uart_ring_persist_submit_48ea66(uint32_t,uint32_t,const void *); /* native 0x48ea66 */
extern void audio_uart_ring_persist_notify_47dd92(void); /* native 0x47dd92 */
void audio_uart_ring_wear_persist_48eb32(uint32_t key,uint32_t length,const void *payload) {
    if(length>8u)length=8u;
    if(payload==0)length=0u;
    if(audio_uart_ring_persist_initialized==0u)
        audio_uart_ring_persist_initialize_48eac8();
    audio_uart_ring_persist_submit_48ea66(key,length,payload);
    uint32_t write=*(const uint32_t *)(const void *)(audio_uart_ring_persist_queue_state+8u);
    uint32_t read=*(const uint32_t *)(const void *)(audio_uart_ring_persist_queue_state+16u);
    if(write-read>0xbffu && audio_uart_ring_persist_wake_pending==0u &&
       audio_uart_ring_persist_wake_blocked==0u) {
        audio_uart_ring_persist_wake_pending=1u;
        audio_uart_ring_persist_notify_47dd92();
    }
}
