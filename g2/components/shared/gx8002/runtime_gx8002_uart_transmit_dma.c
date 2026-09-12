/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "gx_dma_ahb.h"
extern void open_cfw_gx8002_uart_transmit_complete(volatile uint32_t *);
extern void open_cfw_gx8002_dcache_clean_range(uint32_t, uint32_t);
extern int open_cfw_gx8002_dma_select(void);
extern void open_cfw_gx8002_dma_release(uint32_t);
extern uint32_t open_cfw_gx8002_uart_dma_burst(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_dma_callback(uint32_t, uint32_t, uint32_t);
extern int open_cfw_gx8002_dma_transfer(uint32_t, uint32_t, uint32_t, uint32_t, GX_DMA_AHB_CH_CONFIG *);

/* Recovered codec 0xc694. Valid ports preserve stock setup order.
 * Explicit repair: stock uses an uninitialized dst_hs_per for other ports;
 * release the allocation and return an error instead of submitting it. */
int open_cfw_gx8002_uart_transmit_dma(volatile uint32_t *descriptor,
                                    uint32_t buffer, uint32_t length)
{
    uint32_t device=descriptor[1];
    open_cfw_gx8002_dcache_clean_range(buffer,length);
    int channel=open_cfw_gx8002_dma_select();
    if (channel<0) return -1;
    descriptor[31]=(uint32_t)channel;
    GX_DMA_AHB_CH_CONFIG config;
    config.trans_width=GX_DMA_AHB_TRANS_WIDTH_8;
    config.src_addr_update=GX_DMA_AHB_CH_CTL_L_INC;
    config.src_hs_select=GX_DMA_AHB_HS_SEL_HW;
    config.src_master_select=GX_DMA_AHB_MASTER_1;
    config.src_msize=open_cfw_gx8002_uart_dma_burst(descriptor,1);
    config.src_hs_per=0;
    config.dst_addr_update=GX_DMA_AHB_CH_CTL_L_NOINC;
    config.dst_hs_select=GX_DMA_AHB_HS_SEL_HW;
    config.dst_master_select=GX_DMA_AHB_MASTER_2;
    config.dst_msize=open_cfw_gx8002_uart_dma_burst(descriptor,1);
    uint32_t port=descriptor[0];
    if (port==0) config.dst_hs_per=7;
    else if (port==1) config.dst_hs_per=5;
    else {
        open_cfw_gx8002_dma_release((uint32_t)channel);
        descriptor[31]=UINT32_MAX;
        return -1;
    }
    config.flow_ctrl=GX_DMA_AHB_TT_FC_MEM_TO_PER_DMAC;
    open_cfw_gx8002_dma_callback(channel,(uint32_t)(uintptr_t)open_cfw_gx8002_uart_transmit_complete,(uint32_t)(uintptr_t)descriptor);
    (void)open_cfw_gx8002_dma_transfer(device,buffer,length,channel,&config);
    return 0;
}
