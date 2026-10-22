/* Native display brightness open/close wrappers 0x46f68a/0x46f6a2. */
#include <stdint.h>
extern uint8_t audio_uart_font_flash_mode; /* authenticated RAM0x20074fb8 */
extern void audio_uart_brightness_stage_46f5a6(void);
extern void audio_uart_brightness_open_prepare_46f52c(void);
extern void audio_uart_brightness_close_prepare_46f50c(void);
extern void audio_uart_brightness_commit_46f604(void);

/* Stock 0x0046F68A (display_brightness_open_46f68a) */
void audio_uart_display_brightness_open(void)
{
    audio_uart_brightness_stage_46f5a6();
    audio_uart_brightness_open_prepare_46f52c();
    audio_uart_font_flash_mode=1u;
    audio_uart_brightness_commit_46f604();
}

/* Stock 0x0046F6A2 (display_brightness_close_46f6a2) */
void audio_uart_display_brightness_close(void)
{
    audio_uart_brightness_stage_46f5a6();
    audio_uart_font_flash_mode=0u;
    audio_uart_brightness_close_prepare_46f50c();
    audio_uart_brightness_commit_46f604();
}
