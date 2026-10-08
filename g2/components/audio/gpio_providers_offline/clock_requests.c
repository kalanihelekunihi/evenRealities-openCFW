#include "clock_requests.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_save_irq(void);
void audio_clock_reference_update(uint32_t reference){
 uint32_t mask=stock_save_irq();
 W(0x40008858)=(W(0x40008858)&~64u)|(((uint8_t)reference&1u)<<6);
 __asm volatile("msr primask, %0"::"r"(mask):"memory");
}
void audio_clock_requests_update(uint32_t mux_index,uint32_t sources){
 uint32_t mask=stock_save_irq();
 B(0x200740ec+(uint8_t)mux_index)=(uint8_t)sources;
 uint32_t needed=0;
 for(uint32_t i=0;i<6;i++)needed|=B(0x200740ec+i);
 for(uint32_t bit=0;bit<5;bit++)W(0x40008858)=(W(0x40008858)&~(1u<<(bit+1)))|(((needed>>bit)&1u)<<(bit+1));
 __asm volatile("msr primask, %0"::"r"(mask):"memory");
}
