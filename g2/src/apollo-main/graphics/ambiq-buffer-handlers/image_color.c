/* Apollo Nema image color at 0x513e4c..0x513e6c. */
#include <stdint.h>

extern volatile uint8_t audio_uart_nema_boot_state_200043a8[];
extern uint32_t audio_uart_ambiq_color_premultiply_4b15b4(uint32_t);
extern void audio_uart_ambiq_color_register_4b1474(uint32_t,uint32_t);

/* Stock 0x513E56 (secondary entry of 0x513E4C after the boot-state test: premultiply, ^0xff000000, register 3) */
void audio_uart_ambiq_image_color_513e4c(uint32_t color) {
    if (audio_uart_nema_boot_state_200043a8[0]==0u) return;
    const uint32_t premultiplied=audio_uart_ambiq_color_premultiply_4b15b4(color);
    audio_uart_ambiq_color_register_4b1474(3u,premultiplied^0xff000000u);
}
