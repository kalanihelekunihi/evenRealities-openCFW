/* Authenticated native LV flex/grid callback installers 0x48ba64/0x48ca26. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* RAM 0x2006f548 */
extern void audio_uart_lv_theme_default_apply_48bae4(void);
extern void audio_uart_lv_theme_basic_apply_48ca3c(void);

void audio_uart_lv_theme_default_48ba64(void)
{
    uint8_t *themes = *(uint8_t **)(void *)(audio_uart_display_lv_root + 0x5cu);
    *(void (**)(void))(void *)(themes + 8u) = audio_uart_lv_theme_default_apply_48bae4;
    *(uint32_t *)(void *)(themes + 12u) = 0u;
}

void audio_uart_lv_theme_basic_48ca26(void)
{
    uint8_t *themes = *(uint8_t **)(void *)(audio_uart_display_lv_root + 0x5cu);
    *(void (**)(void))(void *)(themes + 16u) = audio_uart_lv_theme_basic_apply_48ca3c;
    *(uint32_t *)(void *)(themes + 20u) = 0u;
}
