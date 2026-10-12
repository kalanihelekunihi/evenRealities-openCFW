/* Native 0x4c3e9a group-2 IRQ enable (bit release and power-down). */
#include <stdint.h>

extern uint32_t audio_uart_mux_bit_get(uint32_t,uint32_t); /* 0x4c37a8 */
extern uint32_t audio_uart_mux_bit_set(uint32_t,uint32_t,uint32_t); /* 0x4c37fe */
extern uint32_t audio_uart_mux_any(uint32_t); /* 0x4c377a */
extern uint32_t g2_gpio_critical_save(void); /* 0x473940 */
extern uint32_t audio_oscillator_control(uint32_t,const void *); /* selected exact 0x4809c4 */
/* Authenticated ROM literals at 0x4c4680/84 point to these live RAM cells.
 * Their storage and startup initialization remain linker/runtime contracts. */
#define GROUP2_FLAG (*(volatile uint8_t *)(uintptr_t)0x20074f56u)
#define GROUP2_LIVE_PTR (*(volatile uint32_t *)(uintptr_t)0x20074260u)

uint32_t audio_ble_vendor_irq_enable_bank2_4c3e9a(uint32_t pin)
{
    pin=(uint8_t)pin;
    if(audio_uart_mux_bit_get(2u,pin)==0u) return 0u;
    uint32_t saved=g2_gpio_critical_save();
    (void)audio_uart_mux_bit_set(2u,pin,0u);
    if(audio_uart_mux_any(2u)==0u) {
        uint8_t command=1u;
        (void)audio_oscillator_control(4u,&command);
        GROUP2_FLAG=0u;
        GROUP2_LIVE_PTR=0u;
    }
    __asm volatile("msr primask, %0" : : "r"(saved) : "memory");
    return 0u;
}
