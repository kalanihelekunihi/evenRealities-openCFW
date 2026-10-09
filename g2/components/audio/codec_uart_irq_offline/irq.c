#include "irq.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t codec_irq_status(void *,uint32_t *,uint32_t);
extern uint32_t codec_irq_clear(void *,uint32_t);
extern uint32_t codec_irq_service(void *,uint32_t);
extern uint32_t codec_fifo_read(void *,uint8_t *,uint32_t,uint32_t *);
static void receive(uint32_t channel,uint32_t amount,uint32_t deliver){
 uint32_t d=0x20000d2cu+channel*28u,rx=W(d+16),count=0;
 codec_fifo_read((void *)(uintptr_t)W(d+4),(uint8_t *)(uintptr_t)(W(rx+12)+W(rx+8)),amount,&count);
 W(rx+8)=W(rx+8)+count;
 if(deliver){uint32_t callback=W(d+20);if(callback)((void(*)(uint32_t,uint32_t))(uintptr_t)callback)(W(rx+12),W(rx+8));W(rx+8)=0;}
}
uint32_t codec_uart_irq(uint32_t input){
 uint32_t channel=(uint8_t)input;if(channel>=4)return 0;
 uint32_t d=0x20000d2cu+channel*28u,status=0,handle=W(d+4);
 codec_irq_status((void *)(uintptr_t)handle,&status,1);
 codec_irq_clear((void *)(uintptr_t)handle,status);
 codec_irq_service((void *)(uintptr_t)handle,status);
 if(status&0x10)receive(channel,15,0);
 if(status&0x40)receive(channel,16,1);
 if(status&1)B(d+25)=1;
 return status;
}
