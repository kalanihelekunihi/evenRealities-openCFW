/* Native persistence record append 0x48e9be: bounded 4 KiB circular words. */
#include <stdint.h>
extern uint8_t audio_uart_ring_persist_queue_state[24u]; /* RAM 0x200771f4 */
extern uint32_t audio_uart_ring_persist_record_size_48e8f0(uint32_t);
extern void audio_uart_ring_persist_write_word_48e8d4(uint32_t,uint32_t);
void audio_uart_ring_persist_append_48e9be(uint32_t key,uint32_t count,
                                           const uint32_t *data,uint32_t stamp) {
    uint32_t size=count*4u+8u;
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    uint32_t *q=(uint32_t *)(void *)audio_uart_ring_persist_queue_state;
    uint32_t write=q[2];
    while(size+(write-q[3])>0x1000u) {
        uint32_t next=q[3]+audio_uart_ring_persist_record_size_48e8f0(q[3]);
        q[3]=next;
        if((int32_t)(q[4]-next)<0) {
            q[4]=next;
            q[5]++;
        }
    }
    audio_uart_ring_persist_write_word_48e8d4(write,(count&15u)|0xa0u|(key<<8));
    audio_uart_ring_persist_write_word_48e8d4(write+4u,stamp);
    for(uint32_t i=0;i<count;i++)
        audio_uart_ring_persist_write_word_48e8d4(write+i*4u+8u,data[i]);
    q[2]=write+size;
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
}
