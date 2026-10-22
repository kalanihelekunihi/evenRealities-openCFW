/* MX25U/MSPI descendant 0x4c45a4 (clock-manager release of every MSPI user). */
#include <stdint.h>

extern uint32_t audio_uart_pin_mux_disable(uint32_t,uint32_t); /* 0x4c4530 */
extern uint32_t audio_uart_mux_bit_get(uint32_t,uint32_t); /* 0x4c37a8 */

/* mspi_clkgen_ctrl 0x4c0758, mspi_cq_enable 0x4bfd44, mspi_cq_disable 0x4bfd62
 * and am_hal_mspi_interrupt_disable 0x4c235c (formerly audio_uart_font_mspi_*
 * and audio_uart_font_power_prepare here, with private CMDQ enable/disable
 * copies) now come from AmbiqSuite 5.1.0 hal/mcu/am_hal_mspi.c and
 * am_hal_cmdq.c. */
uint32_t audio_uart_font_pin_mux_disable(uint32_t pin) {
    pin=(uint8_t)pin;
    if(pin>=0x39u) return 6u;
    for(uint32_t group=0u;group<7u;group++) {
        if(audio_uart_mux_bit_get(group,pin)!=0u)
            (void)audio_uart_pin_mux_disable(group,pin);
    }
    return 0u;
}
