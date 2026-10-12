/* Native log-structured persistence ring helpers 0x48e8d4/e2/f0,
 * validator 0x48e900 and reset 0x48e99c. */
#include <stdint.h>
extern uint8_t audio_uart_ring_persist_storage[0x1000u]; /* RAM 0x200761f4 */
extern uint8_t audio_uart_ring_persist_queue_state[24u]; /* RAM 0x200771f4 */
static uint32_t word(const uint8_t *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)(p+offset);
}
static void put(uint8_t *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)(p+offset)=value;
}
uint32_t audio_uart_ring_persist_read_word_48e8e2(uint32_t position) {
    return word(audio_uart_ring_persist_storage,position&0xffcu);
}
void audio_uart_ring_persist_write_word_48e8d4(uint32_t position,uint32_t value) {
    put(audio_uart_ring_persist_storage,position&0xffcu,value);
}
uint32_t audio_uart_ring_persist_record_size_48e8f0(uint32_t position) {
    return (audio_uart_ring_persist_read_word_48e8e2(position)&15u)*4u+8u;
}
uint32_t audio_uart_ring_persist_validate_48e900(void) {
    const uint8_t *q=audio_uart_ring_persist_queue_state;
    uint32_t read=word(q,12u),write=word(q,8u),tail=word(q,16u);
    if(word(q,0u)!=0x31435054u || word(q,4u)!=0x1000u)return 0u;
    if(((tail|read|write)&3u)!=0u)return 0u;
    if(write-read>0x1000u)return 0u;
    if(write-read<tail-read)return 0u;
    uint32_t current=read;
    for(uint32_t i=0;i<0x202u;i++) {
        if(current==write)return 1u;
        uint32_t header=audio_uart_ring_persist_read_word_48e8e2(current);
        if((header&0xf0u)!=0xa0u || (header&15u)>8u)return 0u;
        current+=(header&15u)*4u+8u;
        if(current-read>write-read)return 0u;
    }
    return 0u;
}
void audio_uart_ring_persist_reset_48e99c(void) {
    uint8_t *q=audio_uart_ring_persist_queue_state;
    put(q,0u,0x31435054u);
    put(q,4u,0x1000u);
    for(uint32_t i=8u;i<=20u;i+=4u)put(q,i,0u);
}
