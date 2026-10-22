#include "reset.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t stock_peripheral_enable(uint32_t);
extern uint32_t am_hal_pwrctrl_temp_update(float temperature,uint32_t bounds[2]); /* 0x480028 */
extern uint32_t stock_wait_status(uint32_t timeout,uint32_t address,uint32_t mask,uint32_t expected);
/* Stock 0x005A1DA4 (PCM2.1 SPOT default reset) */
uint32_t pcm21_reset(void) {
    if(W(0x40021008)!=0 || W(0x40021010)!=0) return 1;
    if(stock_peripheral_enable(29)!=0) return 1;
    uint32_t bounds[2];
    if(am_hal_pwrctrl_temp_update(-40.0f,bounds)!=0) return 1;
    if(stock_wait_status(2500,0x400083e0,1,0)!=0) return 4;
    return 0;
}
