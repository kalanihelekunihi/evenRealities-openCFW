#include "startup.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t stock_peripheral_enable(uint32_t);
extern uint32_t stock_temperature_request(uint32_t bounds[2],float temperature);
extern uint32_t stock_wait_status(uint32_t timeout,uint32_t address,uint32_t mask,uint32_t expected);
uint32_t pcm22_reset(void) {
    if(W(0x40021008)!=0 || W(0x40021010)!=0) return 1;
    if(stock_peripheral_enable(29)!=0) return 1;
    uint32_t bounds[2];
    if(stock_temperature_request(bounds,-40.0f)!=0) return 1;
    if(stock_wait_status(2500,0x400083e0,1,0)!=0) return 4;
    return 0;
}

#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t pcm_capture_trim_block(void);
extern uint32_t stock_save_irq(void);
extern uint32_t stock_ton_update(uint32_t,uint32_t);
typedef uint32_t (*callback_t)(void);
uint32_t pcm_ton_initialize_dispatch(void) {
 callback_t callback=(callback_t)(uintptr_t)W(0x20073290);
 return callback ? callback() : 0;
}
uint32_t pcm_common_capture_retention_block(void) {
 pcm_capture_trim_block();
 W(0x4002037c)|=0x40000000;
 W(0x40020380)|=0x10000;
 W(0x40020380)|=0x1000;
 return 0;
}
uint32_t pcm_common_capture_ton_block(void) {
 pcm_common_capture_retention_block();
 uint32_t mask=stock_save_irq();
 (void)pcm_ton_initialize_dispatch();
 (void)stock_ton_update(0,B(0x20074f60));
 __asm volatile("msr primask, %0"::"r"(mask):"memory");
 return 0;
}

uint32_t pcm_lp_initialize_dispatch(void) { callback_t f=(callback_t)(uintptr_t)W(0x200732a0);return f?f():0; }
uint32_t pcm_lp_enable_dispatch(void) { callback_t f=(callback_t)(uintptr_t)W(0x200732a4);return f?f():0; }
uint32_t pcm_lp_disable_dispatch(void) { callback_t f=(callback_t)(uintptr_t)W(0x200732a8);return f?f():0; }

extern void stock_clock_mux_reset(void);
uint32_t pcm_common_capture_to_return(void) {
 pcm_common_capture_ton_block();
 (void)pcm_lp_initialize_dispatch();
 stock_clock_mux_reset();
 if((W(0x4002000c)&255)>=0x22) W(0x400211c8)|=6;
 return 0;
}
