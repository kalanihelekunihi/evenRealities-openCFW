#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
static void submit_store(uint32_t data,uint32_t index,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=value;
}
static uint32_t submit_advance(volatile uint32_t *ring,uint32_t capacity) {
    uint32_t index=ring[4]+1u;
    return (int32_t)index>=(int32_t)capacity?0u:index;
}
static uint32_t submit_pad(volatile uint32_t *ring,uint32_t data,uint32_t capacity,uint32_t index) {
    do {
        ring[4]=index;submit_store(data,index,0x10000u);
        index=ring[4]+1u;
    } while((int32_t)index<(int32_t)capacity && index!=0u);
    return 0u;
}
/* Native523f10..52404a: signed submission gate, ring command/padding/alignment, fresh descriptor after flush. */
void audio_uart_nema_submit_523f10(uint32_t submission) {
    if((int32_t)submission<=0)return;
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3];
    uint32_t index=ring[4];
    uint32_t data=audio_uart_nema_ring_descriptor[1];
    if((int32_t)capacity<(int32_t)(index+2u)) {index=submit_pad(ring,data,capacity,index);ring[4]=index;}
    index=ring[4];submit_store(data,index,328u);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,submission);
    index=submit_advance(ring,capacity);
    if((int32_t)capacity<(int32_t)(index+2u))index=submit_pad(ring,data,capacity,index);
    ring[4]=index;submit_store(data,index,248u);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,1u);
    index=submit_advance(ring,capacity);
    if((int32_t)(index+4u)>=(int32_t)capacity)index=submit_pad(ring,data,capacity,index);
    while(index&3u) {
        ring[4]=index;submit_store(data,index,0x10000u);
        index=submit_advance(ring,capacity);
    }
    uint32_t physical=audio_uart_nema_ring_descriptor[2];
    ring[4]=index;submit_store(data,index,0xff0000f0u);
    uint32_t target=physical+(index+4u)*4u;
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,target);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,0xff0000f4u);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,audio_uart_nema_ring_descriptor[4]);
    index=submit_advance(ring,capacity);ring[4]=index;
    audio_uart_nema_buffer_flush_5140ea((void *)ring);
    ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    physical=audio_uart_nema_ring_descriptor[2];index=ring[4];
    audio_uart_nema_reg_write_514046(236u,(physical+index*4u)|4u);
}
