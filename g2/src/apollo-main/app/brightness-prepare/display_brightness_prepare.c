/* Native brightness flash power transitions 0x46f50c/0x46f52c. */
#include <stdint.h>
extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t); /* 0x4c26e0 */
extern void *audio_uart_font_flash_device; /* RAM0x20074544 */
extern uint8_t audio_uart_font_flash_sleep; /* RAM0x20074fb9 */

void audio_uart_brightness_close_prepare_46f50c(void)
{
    if (audio_uart_font_flash_sleep!=1u) {
        (void)audio_uart_font_flash_power(audio_uart_font_flash_device,2u,1u);
        audio_uart_font_flash_sleep=1u;
    }
}

void audio_uart_brightness_open_prepare_46f52c(void)
{
    (void)audio_uart_font_flash_power(audio_uart_font_flash_device,0u,1u);
    audio_uart_font_flash_sleep=0u;
}
