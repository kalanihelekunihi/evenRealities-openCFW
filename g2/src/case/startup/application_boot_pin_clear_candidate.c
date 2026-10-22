/* SPDX-License-Identifier: MIT
 * Native CASE 0x08004c1c pin deconfiguration and EXTI detachment.
 */
#include <stdint.h>
static uint32_t port_index(uint32_t base)
{
    if(base==0x50000000u)return 0u;
    if(base==0x50000400u)return 1u;
    if(base==0x50000800u)return 2u;
    if(base==0x50000c00u)return 3u;
    if(base==0x50001000u)return 4u;
    return 5u;
}
/* Stock 0x08004C1C (case_release_pins) */
void case_boot_pin_config(uint32_t base,uint32_t mask)
{
    volatile uint32_t *gpio=(volatile uint32_t *)(uintptr_t)base;
    for(uint32_t pin=0u;pin<16u && (mask>>pin)!=0u;++pin){
        uint32_t bit=1u<<pin;
        if((mask&bit)==0u)continue;
        volatile uint32_t *exti=(volatile uint32_t *)(uintptr_t)0x40021800u;
        uint32_t slot=pin>>2u,shift=(pin&3u)*8u;
        uint32_t field=0xfu<<shift;
        if((exti[0x60u/4u+slot]&field)==(port_index(base)<<shift)){
            exti[0x80u/4u]&=~bit;
            exti[0x84u/4u]&=~bit;
            exti[1u]&=~bit;
            exti[0u]&=~bit;
            exti[0x60u/4u+slot]&=~field;
        }
        uint32_t mode=3u<<(pin*2u);
        gpio[0u]|=mode;
        gpio[0x20u/4u+(pin>>3u)]&=~(0xfu<<((pin&7u)*4u));
        gpio[2u]&=~mode;
        gpio[1u]&=~bit;
        gpio[3u]&=~mode;
    }
}
