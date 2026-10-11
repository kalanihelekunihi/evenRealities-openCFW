/* Native DMA channel descriptor initializer 0x53006c, six words. */
#include <stdint.h>

void audio_uart_dma_channel_create(void *descriptor,uint32_t address,
                                    uint32_t enable,uint32_t configuration) {
    uint32_t *d=(uint32_t *)descriptor;
    d[0]=0u;
    d[1]=0u;
    d[2]=0u;
    d[3]=configuration;
    d[4]=enable;
    d[5]=address;
}
