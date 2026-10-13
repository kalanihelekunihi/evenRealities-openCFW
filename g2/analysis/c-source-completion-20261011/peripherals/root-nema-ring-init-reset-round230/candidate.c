#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
static void ring_init_store(uint32_t data,uint32_t offset,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(data+offset)=value;
}
/* Native523bf8..523c88: descriptor always records size; signed positive-size gate. */
int32_t audio_uart_nema_ring_initialize_523bf8(void *cell,uint32_t initialize) {
    volatile uint32_t *ring=cell;
    uint32_t size=ring[0];audio_uart_nema_ring_descriptor[4]=size;
    if((int32_t)size<=0) {audio_uart_nema_error_set_4b127c(4u);return -1;}
    audio_uart_nema_ring_descriptor[0]=(uint32_t)(uintptr_t)cell;
    uint32_t data=ring[2];audio_uart_nema_ring_descriptor[1]=data;
    uint32_t physical=ring[3];
    uint32_t capacity=(uint32_t)((int32_t)size/4)-4u;
    audio_uart_nema_ring_descriptor[2]=physical;audio_uart_nema_ring_descriptor[3]=capacity;
    if(initialize!=0u) {
        ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
        ring[4]=0u;ring[5]=0u;
        uint32_t tail=data+capacity*4u;
        ring_init_store(tail,0u,0xff0000f0u);ring_init_store(tail,4u,physical);
        ring_init_store(tail,8u,0xff0000f4u);ring_init_store(tail,12u,size);
        audio_uart_nema_buffer_flush_5140ea((void *)ring);
        audio_uart_nema_reg_write_514046(328u,0u);
        physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(236u,physical|6u);
        physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(240u,physical);
        size=audio_uart_nema_ring_descriptor[4];audio_uart_nema_reg_write_514046(244u,size);
    }
    return 0;
}
/* Native523c88..523ce0: tail store order differs from first initialization. */
void audio_uart_nema_child_523c88(void) {
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    ring[4]=0u;ring[5]=0u;
    uint32_t data=audio_uart_nema_ring_descriptor[1];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3];
    uint32_t tail=data+capacity*4u;
    ring_init_store(tail,0u,0xff0000f0u);
    uint32_t physical=audio_uart_nema_ring_descriptor[2];
    ring_init_store(tail,8u,0xff0000f4u);ring_init_store(tail,4u,physical);
    uint32_t size=audio_uart_nema_ring_descriptor[4];ring_init_store(tail,12u,size);
    audio_uart_nema_buffer_flush_5140ea((void *)ring);
    audio_uart_nema_reg_write_514046(328u,0u);
    physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(236u,physical|6u);
    physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(240u,physical);
    size=audio_uart_nema_ring_descriptor[4];audio_uart_nema_reg_write_514046(244u,size);
}
