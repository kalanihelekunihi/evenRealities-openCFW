/* LVGL style-property forwarding wrapper, stock 0x441262..0x44126f. */
#include <stdint.h>
extern void audio_uart_page_style_apply_44be4c(void *,uint8_t,uint32_t,uint32_t);
void audio_uart_page_441262(void *object,uint32_t value,uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object,0x19u,value,selector);
}
