/* Native hub_role_init 0x4a6d28: source owner of HUB role cell. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern volatile uint16_t audio_uart_hub_role_cell; /* RAM 0x20004526 */
void audio_hub_role_init(void) {
    uint8_t role=audio_uart_device_role_get();
    if(role==1u) audio_uart_hub_role_cell=3u;
    else if(role==2u) audio_uart_hub_role_cell=2u;
}
