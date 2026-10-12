/* Native LV startup children from pinned LVGL v9.3 root layout. Every
 * address below is an authenticated offset within RAM0x2006f548. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_array_init_482b00(uint8_t *,uint32_t);
extern void audio_uart_lv_memory_pool_init_48aa80(void *);
extern void audio_uart_lv_async_init_4d465c(void *);
extern void audio_uart_lv_display_init_4645d8(uint32_t);
extern void audio_uart_lv_anim_init_4d46de(void *);
extern void audio_uart_lv_font_init_4d4ad4(uint32_t);
extern void audio_uart_lv_font_deinit_4d4bdc(uint32_t);

void audio_uart_lv_init_memory_48aa60(void)
{
    uint8_t *root=audio_uart_display_lv_root;
    audio_uart_lv_memory_pool_init_48aa80(root+0xc8u);
    audio_uart_lv_memory_pool_init_48aa80(root+0xe8u);
    audio_uart_lv_memory_pool_init_48aa80(root+0x108u);
}
void audio_uart_lv_init_async_49acb0(void)
{
    audio_uart_lv_async_init_4d465c(audio_uart_display_lv_root+0x1d0u);
}
void audio_uart_lv_init_display_464330(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x74u,0x18u);
    audio_uart_lv_display_init_4645d8(1u);
}
void audio_uart_lv_init_indev_4c6d8c(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x180u,4u);
}
void audio_uart_lv_init_style_44d32c(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x34u,0x20u);
}
void audio_uart_lv_init_anim_48438c(void)
{
    audio_uart_lv_anim_init_4d46de(audio_uart_display_lv_root+0x148u);
}
void audio_uart_lv_init_cache_44b90c(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x18u,0x14u);
}
void audio_uart_lv_init_font_488f4c(uint32_t primary,uint32_t secondary)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x128u,0x1cu);
    audio_uart_lv_font_init_4d4ad4(primary);
    audio_uart_lv_font_deinit_4d4bdc(secondary);
}
