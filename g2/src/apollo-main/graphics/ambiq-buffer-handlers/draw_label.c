/* Apollo Ambiq label dispatch at native 0x53faa6. */
#include <stdint.h>
extern void audio_uart_lv_draw_label_48a0be(void *,const void *,void *,void *);
extern void audio_uart_ambiq_label_pixel_53fcc4(void);
void audio_uart_ambiq_draw_label_53faa6(void *unit,const void *descriptor,
                                        void *area) {
    if(((const uint8_t *)descriptor)[0x50u]>=3u)
        audio_uart_lv_draw_label_48a0be(
            unit,descriptor,area,(void *)&audio_uart_ambiq_label_pixel_53fcc4);
}
