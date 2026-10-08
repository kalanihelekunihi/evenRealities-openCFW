#include "reset.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t stock_peripheral_enable(uint32_t);
extern uint32_t stock_temperature_request(uint32_t bounds[2],float temperature);
extern uint32_t stock_wait_status(uint32_t timeout,uint32_t address,uint32_t mask,uint32_t expected);
uint32_t pcm21_reset(void) {
    if(W(0x40021008)!=0 || W(0x40021010)!=0) return 1;
    if(stock_peripheral_enable(29)!=0) return 1;
    uint32_t bounds[2];
    if(stock_temperature_request(bounds,-40.0f)!=0) return 1;
    if(stock_wait_status(2500,0x400083e0,1,0)!=0) return 4;
    return 0;
}
