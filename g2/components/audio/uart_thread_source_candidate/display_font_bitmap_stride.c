/* Native LV image stride dispatch 0x48aad8->0x48aaea. The selected RAM
 * descriptor is at 0x2006f610, within the authenticated LV state region. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_state[]; /* stock RAM0x2006f548 */
uint32_t audio_uart_font_bitmap_stride(uint32_t width,uint8_t format) {
    uint8_t *descriptor=audio_uart_display_lv_state+0xc8u;
    typedef uint32_t (*stride_fn)(uint32_t,uint8_t);
    stride_fn callback=(stride_fn)(uintptr_t)
        *(uint32_t *)(void *)(descriptor+0x14u);
    if(callback==0) return 0u;
    return callback(width,format);
}
