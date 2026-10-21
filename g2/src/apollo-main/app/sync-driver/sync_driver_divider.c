/* Ambiq UART baud-divider calculation, native 0x58de38. Frequency and
 * status words are authenticated ROM constants. Valid nonzero requested
 * baud is the qualified domain; native zero-divisor behavior is untested. */
#include <stdint.h>
uint32_t audio_uart_divider_configure(uint32_t instance,uint32_t requested,
                                      uint32_t *actual) {
    uintptr_t base=(uintptr_t)(0x40039000u+instance*0x1000u);
    uint32_t mode=(*(volatile uint32_t *)(base+0x30u)>>4)&7u;
    uint32_t frequency;
    switch(mode) {
    case 1u: frequency=0x16e3600u;break;
    case 2u: frequency=0x0b71b00u;break;
    case 3u: frequency=0x05b8d80u;break;
    case 4u: frequency=0x02dc6c0u;break;
    case 5u: frequency=0x2dc6c00u;break;
    case 6u: frequency=0x2ee0000u;break;
    default:*actual=0u;return 0x8000002u;
    }
    uint32_t denominator=requested<<4;
    uint32_t integer=frequency/denominator;
    uint64_t fraction=((uint64_t)frequency<<6)/denominator;
    uint32_t fractional=(uint32_t)fraction-integer*0x40u;
    if(integer==0u) {
        *actual=0u;
        return 0x8000003u;
    }
    *(volatile uint32_t *)(base+0x24u)=integer;
    *(volatile uint32_t *)(base+0x28u)=fractional;
    *actual=frequency/((fractional>>2)+integer*0x10u);
    return 0u;
}
