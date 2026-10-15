/* Apollo Ambiq layer wrapper at 0x53f400..0x53f429. */
#include <stdint.h>

extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 */
extern void audio_uart_ambiq_draw_image_53f42a(void *,const void *,void *);

void audio_uart_ambiq_draw_layer_53f400(void *unit,const void *descriptor,
                                         void *draw_area) {
    const uint8_t *source=(const uint8_t *)descriptor;
    uint32_t layer=*(const uint32_t *)(const void *)(source+28u);
    if (*(const uint32_t *)(uintptr_t)layer==0u) return;
    uint32_t image_descriptor[27];
    audio_uart_checksum_copy(image_descriptor,descriptor,108u);
    image_descriptor[7]=*(const uint32_t *)(uintptr_t)layer;
    audio_uart_ambiq_draw_image_53f42a(unit,image_descriptor,draw_area);
}
