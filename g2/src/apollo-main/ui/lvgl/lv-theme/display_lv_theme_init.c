/* Native LV flex/grid layout callback table initialization 0x4546dc. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_malloc(uint32_t); /* selected native0x44f718 */
extern void audio_uart_lv_theme_default_48ba64(void);
extern void audio_uart_lv_theme_basic_48ca26(void);

void audio_uart_lv_init_theme_4546dc(void)
{
    uint8_t *root=audio_uart_display_lv_root;
    uint32_t count=*(uint32_t *)(void *)(root+0x58u);
    *(void **)(void *)(root+0x5cu)=audio_uart_lv_malloc(count<<3u);
    audio_uart_lv_theme_default_48ba64();
    audio_uart_lv_theme_basic_48ca26();
}
