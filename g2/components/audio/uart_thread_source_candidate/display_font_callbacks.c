/* Native FreeType callback installation 0x4b20aa. */
#include <stdint.h>
extern void audio_uart_font_callbacks_common(void *); /* 0x529406 */
extern void audio_uart_font_callbacks_bitmap(void *); /* 0x5297f8 */
extern void audio_uart_font_callbacks_outline(void *); /* 0x529b7e */
void audio_uart_font_callbacks_attach(void *descriptor) {
    audio_uart_font_callbacks_common(descriptor);
    uint8_t mode=((const uint8_t *)descriptor)[0x2du];
    if(mode==0u) audio_uart_font_callbacks_bitmap(descriptor);
    else if(mode==1u) audio_uart_font_callbacks_outline(descriptor);
}
