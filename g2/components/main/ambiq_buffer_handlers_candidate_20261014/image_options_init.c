/* LVGL image descriptor initializer, native 0x488918. */
#include <stdint.h>

void audio_uart_ambiq_image_options_init_488918(void *descriptor) {
    uint8_t *d=(uint8_t *)descriptor;
    for(unsigned i=0;i<0x6cu;i++) d[i]=0u;
    d[0x50u]=0xffu;
    *(uint32_t *)(void *)(d+0x34u)=0x100u;
    *(uint32_t *)(void *)(d+0x38u)=0x100u;
    *(uint16_t *)(void *)(d+0x50u)&=0xf7ffu;
    *(uint32_t *)(void *)(d+0x60u)=0xe0000001u;
    *(uint32_t *)(void *)(d+0x14u)=0x6cu;
}
