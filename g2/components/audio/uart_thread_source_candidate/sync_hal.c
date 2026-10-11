/* ARM NVIC helpers 0x5849d4/0x5849f2/0x584a10 and sync finalize 0x584df4.
 * MMIO addresses and ROM pin values are authenticated in Apollo MAIN. */
#include <stdint.h>
extern void *g2_uart_sync_driver; /* RAM0x20074610 */
extern volatile uint8_t g2_uart_sync_started; /* RAM0x20074fc9 */
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* selected 0x480f0c */
extern uint32_t audio_uart_sync_driver_mode(void *,uint32_t,uint32_t); /* 0x58dbb8 */
void audio_uart_sync_hal0(uint32_t irq) { /* NVIC disable */
    if((int16_t)irq>=0)
        *(volatile uint32_t *)(uintptr_t)(0xe000e280u+(((uint32_t)(int16_t)irq>>5)*4u))=
            1u<<(irq&31u);
}
void audio_uart_sync_hal2(uint32_t irq) { /* NVIC enable */
    if((int16_t)irq>=0)
        *(volatile uint32_t *)(uintptr_t)(0xe000e100u+(((uint32_t)(int16_t)irq>>5)*4u))=
            1u<<(irq&31u);
}
void audio_uart_sync_hal1(uint32_t irq,uint32_t priority) { /* NVIC priority */
    uint32_t address;
    if((int16_t)irq<0)
        address=0xe000ed18u+((irq&15u)-4u);
    else address=0xe000e400u+(uint32_t)(int16_t)irq;
    *(volatile uint8_t *)(uintptr_t)address=(uint8_t)(priority<<4);
}
uint32_t audio_uart_sync_finalize(void) {
    if(g2_uart_sync_driver==0) return 1u;
    g2_uart_sync_started=0u;
    uint32_t p2=g2_codec_pin_function(2u,3u); /* ROM0x78ee48 */
    uint32_t p0=g2_codec_pin_function(0u,0xe083u); /* ROM0x78ee4c */
    uint32_t mode=audio_uart_sync_driver_mode(g2_uart_sync_driver,2u,1u);
    return p2|p0|mode;
}
