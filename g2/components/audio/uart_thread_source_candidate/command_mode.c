/* Native productModeGet 0x4abe60..0x4abe65, used as UART command gate. */
#include <stdint.h>
extern volatile uint8_t g2_uart_product_mode_state[]; /* object 0x200038f0 */
uint32_t audio_uart_command_pending(void)
{
    return g2_uart_product_mode_state[1];
}
