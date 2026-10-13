#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
static void packet_store(uint32_t data,uint32_t index,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=value;
}
static uint32_t packet_advance(volatile uint32_t *ring,uint32_t capacity) {
    uint32_t index=ring[4]+1u;
    return (int32_t)index>=(int32_t)capacity?0u:index;
}
static uint32_t packet_pad(volatile uint32_t *ring,uint32_t data,uint32_t capacity,uint32_t index) {
    do {
        ring[4]=index;packet_store(data,index,0x10000u);
        index=ring[4]+1u;
    } while((int32_t)index<(int32_t)capacity && index!=0u);
    return 0u;
}
static uint32_t packet_emit(uint32_t physical,uint32_t words) {
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3],data=audio_uart_nema_ring_descriptor[1];
    uint32_t index=ring[4];
    if((int32_t)(index+4u)>=(int32_t)capacity) {index=packet_pad(ring,data,capacity,index);ring[4]=index;}
    while(((volatile uint8_t *)ring)[16]&3u) {
        index=ring[4];packet_store(data,index,0x10000u);
        index=packet_advance(ring,capacity);ring[4]=index;
    }
    index=ring[4];packet_store(data,index,240u);
    index=packet_advance(ring,capacity);ring[4]=index;packet_store(data,index,physical);
    index=packet_advance(ring,capacity);ring[4]=index;packet_store(data,index,0x000200f4u);
    index=packet_advance(ring,capacity);ring[4]=index;packet_store(data,index,words);
    index=packet_advance(ring,capacity);ring[4]=index;
    audio_uart_nema_buffer_flush_5140ea((void *)ring);
    ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t current_physical=audio_uart_nema_ring_descriptor[2];index=ring[4];
    audio_uart_nema_reg_write_514046(236u,(current_physical+index*4u)|4u);
    ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t sequence=ring[5]+1u;
    if((int32_t)sequence>=0x01000000)sequence=0u;
    ring[5]=sequence;return sequence;
}
/* Native523ce0..523dba and523dba..523e92: packet wrappers with distinct zero-length read policy. */
uint32_t audio_uart_nema_sector_finalize_523ce0(uint32_t physical,uint32_t words) {
    if(words==0u)return UINT32_MAX;
    return packet_emit(physical,words);
}
uint32_t audio_uart_nema_chain_finalize_523dba(void *cell,uint32_t words) {
    uint32_t physical=((volatile uint32_t *)cell)[3];
    if(words==0u)return UINT32_MAX;
    return packet_emit(physical,words);
}
