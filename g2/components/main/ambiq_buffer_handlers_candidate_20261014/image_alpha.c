/* Apollo Nema image alpha at native 0x513e2e. */
#include <stdint.h>
extern uint32_t audio_uart_ambiq_color_register_4b1474(uint32_t,uint32_t);
extern volatile uint8_t audio_uart_nema_boot_state_200043a8[];
extern void audio_uart_nema_alpha_command_522960(uint32_t);
void audio_uart_ambiq_image_alpha_513e2e(uint32_t alpha) {
    audio_uart_ambiq_color_register_4b1474(1u,alpha);
    if(audio_uart_nema_boot_state_200043a8[0]!=0u)
        audio_uart_nema_alpha_command_522960(alpha);
}
