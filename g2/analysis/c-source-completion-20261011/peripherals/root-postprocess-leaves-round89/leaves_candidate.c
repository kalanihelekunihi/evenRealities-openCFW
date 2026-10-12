#include <stdint.h>
/* Full native 440fc4..440fde: enum ABI is reduced to its low byte. */
uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t format)
{
    uint32_t cf=(uint8_t)format;
    return (cf-7u<=7u || cf==16u || cf-19u<=5u) ? 1u : 0u;
}
/* Full native 48b73c..48b750: only header flags bits 16..31 participate. */
uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *buffer,uint32_t mask)
{
    return ((*(const volatile uint32_t *)buffer >> 16u)&mask)!=0u;
}
