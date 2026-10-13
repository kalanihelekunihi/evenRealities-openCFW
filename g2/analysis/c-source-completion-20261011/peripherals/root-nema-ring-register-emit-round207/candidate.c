#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
/* Native523e92..523f0e: cached ring/data/capacity, fresh write-index reads. */
void audio_uart_nema_register_emit_523e92(uint32_t reg,uint32_t value) {
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t index=ring[4];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3];
    uint32_t data=audio_uart_nema_ring_descriptor[1];
    if((int32_t)capacity<(int32_t)(index+2u)) {
        do {
            ring[4]=index;
            *(volatile uint32_t *)(uintptr_t)(data+index*4u)=0x10000u;
            index=ring[4]+1u;
        } while((int32_t)index<(int32_t)capacity && index!=0u);
        ring[4]=0u;
    }
    index=ring[4];
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=reg;
    index=ring[4]+1u;
    if((int32_t)index>=(int32_t)capacity)index=0u;
    ring[4]=index;
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=value;
    index=ring[4]+1u;
    if((int32_t)index>=(int32_t)capacity)index=0u;
    ring[4]=index;
    if(reg&0xff000000u) {
        audio_uart_nema_buffer_flush_5140ea((void *)ring);
        ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
        uint32_t physical=audio_uart_nema_ring_descriptor[2];
        index=ring[4];
        audio_uart_nema_reg_write_514046(236u,(physical+index*4u)|4u);
    }
}
