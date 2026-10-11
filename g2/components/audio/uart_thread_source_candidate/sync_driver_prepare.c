/* Ambiq UART DMA callback preparation, native 0x58ddd6. Both optional
 * channels retain the real 0x53006c child, with no synthetic DMA success. */
#include <stdint.h>
extern void audio_uart_dma_channel_create(void *,uint32_t,uint32_t,uint32_t); /* 0x53006c */
uint32_t audio_uart_sync_driver_prepare(void *handle,uint32_t rx_address,
                                        uint32_t rx_config,uint32_t tx_address,
                                        uint32_t tx_config) {
    if(handle==0 || (*(uint32_t *)handle&0x1ffffffu)!=0x1ea9e06u) return 2u;
    uint8_t *state=(uint8_t *)handle;
    state[0xdcu]=0u;state[0xddu]=0u;
    if(rx_address!=0u && rx_config!=0u) {
        state[0xdcu]=1u;
        audio_uart_dma_channel_create(state+0x34u,rx_address,1u,rx_config);
    }
    if(tx_address!=0u && tx_config!=0u) {
        state[0xddu]=1u;
        audio_uart_dma_channel_create(state+0x4cu,tx_address,1u,tx_config);
    }
    return 0u;
}
