/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "gx_dma_ahb.h"
/* Both descriptor words are read, including the unselected direction. */
uint32_t open_cfw_gx8002_uart_dma_burst(volatile uint32_t *descriptor, uint32_t transmit)
{
    uint32_t tx=descriptor[13];
    uint32_t rx=descriptor[14];
    switch (transmit ? tx : rx) {
    case 4: return GX_DMA_AHB_BURST_TRANS_LEN_4;
    case 8: return GX_DMA_AHB_BURST_TRANS_LEN_8;
    case 16: return GX_DMA_AHB_BURST_TRANS_LEN_16;
    case 32: return GX_DMA_AHB_BURST_TRANS_LEN_32;
    case 64: return GX_DMA_AHB_BURST_TRANS_LEN_64;
    case 128: return GX_DMA_AHB_BURST_TRANS_LEN_128;
    case 256: return GX_DMA_AHB_BURST_TRANS_LEN_256;
    case 512: return GX_DMA_AHB_BURST_TRANS_LEN_512;
    case 1024: return GX_DMA_AHB_BURST_TRANS_LEN_1024;
    default: return GX_DMA_AHB_BURST_TRANS_LEN_1;
    }
}
