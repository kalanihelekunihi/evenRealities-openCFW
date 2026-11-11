/* Stock GPIO decode/configuration and ship pulse, using the C operation ABI. */
#include <stdint.h>
extern int32_t osDelay(uint32_t);
__attribute__((noinline)) volatile uint8_t *nrf_gpio_pin_port_decode(
    volatile uint32_t *pin)
{
    uint32_t number = *pin;
    if (number < 32)
        return (volatile uint8_t *)(uintptr_t)UINT32_C(0x50000000);
    *pin = number & 31u;
    return (volatile uint8_t *)(uintptr_t)UINT32_C(0x50000300);
}
__attribute__((noinline)) void nrf_gpio_cfg(uint32_t pin,uint32_t direction,
 uint32_t input,uint32_t pull,uint32_t drive,uint32_t sense)
{
    volatile uint32_t number=pin;
    volatile uint8_t *port=nrf_gpio_pin_port_decode(&number);
    uint32_t config=direction|(input<<1)|(pull<<2)|(drive<<8)|(sense<<16);
    *(volatile uint32_t *)(port+0x700u+number*4u)=config;
}
__attribute__((noinline)) uint32_t r1_ship_mode_pin_pulse(void)
{
    nrf_gpio_cfg(5,1,1,0,0,0);
    volatile uint32_t pin=5;
    volatile uint8_t *port=nrf_gpio_pin_port_decode(&pin);
    /* ARM register shifts use the low byte, with zero at counts >=32. */
    uint32_t shift=pin&255u;
    *(volatile uint32_t *)(port+0x508u)=shift<32 ? UINT32_C(1)<<shift:0;
    (void)osDelay(200);
    nrf_gpio_cfg(5,0,1,0,0,0);
    return 5;
}
