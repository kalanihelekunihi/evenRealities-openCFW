/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "gx_dma_ahb.h"
extern void open_cfw_gx8002_uart_receive_complete(volatile uint32_t *);
extern void open_cfw_gx8002_uart_dma_cache(uint32_t, uint32_t);
extern int open_cfw_gx8002_dma_select(void);
extern uint32_t open_cfw_gx8002_uart_dma_burst(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_dma_callback(uint32_t, uint32_t, uint32_t);
extern int open_cfw_gx8002_dma_transfer(uint32_t, uint32_t, uint32_t, uint32_t, GX_DMA_AHB_CH_CONFIG *);

/* Stock 0xc71c: helper results are deliberately ignored where stock ignores them. */
int open_cfw_gx8002_uart_receive_dma(volatile uint32_t *descriptor,
                                   uint32_t buffer, uint32_t length)
{
    uint32_t device=descriptor[1];
    uint32_t cache_length=descriptor[25];
    uint32_t cache_buffer=descriptor[24];
    open_cfw_gx8002_uart_dma_cache(cache_buffer, cache_length);
    int channel=open_cfw_gx8002_dma_select();
    if (channel<0) return -1;
    descriptor[26]=(uint32_t)channel;
    GX_DMA_AHB_CH_CONFIG config;
    config.src_addr_update=GX_DMA_AHB_CH_CTL_L_NOINC;
    config.src_master_select=GX_DMA_AHB_MASTER_2;
    config.trans_width=GX_DMA_AHB_TRANS_WIDTH_8;
    config.src_hs_select=GX_DMA_AHB_HS_SEL_HW;
    config.src_msize=open_cfw_gx8002_uart_dma_burst(descriptor,0);
    uint32_t port=descriptor[0];
    if (port==0) config.src_hs_per=6;
    else if (port==1) config.src_hs_per=4;
    else return -1;
    config.dst_addr_update=GX_DMA_AHB_CH_CTL_L_INC;
    config.dst_hs_select=GX_DMA_AHB_HS_SEL_HW;
    config.dst_master_select=GX_DMA_AHB_MASTER_1;
    config.dst_msize=open_cfw_gx8002_uart_dma_burst(descriptor,0);
    config.flow_ctrl=GX_DMA_AHB_TT_FC_PER_TO_MEM_DMAC;
    config.dst_hs_per=0;
    open_cfw_gx8002_dma_callback(channel,(uint32_t)(uintptr_t)open_cfw_gx8002_uart_receive_complete,(uint32_t)(uintptr_t)descriptor);
    (void)open_cfw_gx8002_dma_transfer(buffer,device,length,channel,&config);
    return 0;
}
