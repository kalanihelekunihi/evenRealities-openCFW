/* Native LV color_make helper 0x441068..0x44107b. The high byte of the
 * returned stack word is unspecified in stock; only RGB888 is owned here. */
#include <stdint.h>

uint32_t audio_uart_page_441068(uint32_t red, uint32_t green, uint32_t blue) {
    return ((red & 0xffu) << 16) | ((green & 0xffu) << 8) | (blue & 0xffu);
}
