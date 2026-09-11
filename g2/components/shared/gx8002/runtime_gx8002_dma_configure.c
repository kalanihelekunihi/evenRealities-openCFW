/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
#include "gx_dma_ahb.h"
_Static_assert(sizeof(GX_DMA_AHB_CH_CONFIG)==48,"stock DMA config size");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,trans_width)==0,"stock DMA trans_width offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,src_msize)==4,"stock DMA src_msize offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,src_addr_update)==8,"stock DMA src_addr_update offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,src_hs_per)==12,"stock DMA src_hs_per offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,src_master_select)==16,"stock DMA src_master_select offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,src_hs_select)==20,"stock DMA src_hs_select offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,dst_msize)==24,"stock DMA dst_msize offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,dst_addr_update)==28,"stock DMA dst_addr_update offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,dst_hs_per)==32,"stock DMA dst_hs_per offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,dst_master_select)==36,"stock DMA dst_master_select offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,dst_hs_select)==40,"stock DMA dst_hs_select offset");
_Static_assert(offsetof(GX_DMA_AHB_CH_CONFIG,flow_ctrl)==44,"stock DMA flow_ctrl offset");
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern void open_cfw_gx8002_dma_clear(uint32_t);
extern uint32_t open_cfw_gx8002_dma_bus_address(uint32_t);
extern void open_cfw_gx8002_dma_descriptors(volatile uint32_t *,volatile uint32_t *,int32_t,int32_t,uint8_t);
/* Valid transfer-width/channel values remain caller contracts. Stock performs
 * register writes before rejecting an oversized descriptor list. */
int open_cfw_gx8002_dma_configure(uint32_t destination,uint32_t source,
                                int32_t length,uint32_t channel,
                                volatile GX_DMA_AHB_CH_CONFIG *config)
{
    uint32_t destination_burst=config->dst_msize;
    uint32_t source_burst=config->src_msize;
    uint32_t control=(destination_burst<<11)|(source_burst<<14)|0x18000001u;
    uint32_t width=config->trans_width;
    control|=(width<<1)|(width<<4);
    uint32_t value=config->dst_addr_update;
    if (value>1) return -1;
    control|=value<<8;
    value=config->src_addr_update;
    if (value>1) return -1;
    control|=value<<10;
    value=config->dst_master_select;
    if (value>3) return -1;
    control|=value<<23;
    value=config->src_master_select;
    if (value>3) return -1;
    control|=value<<25;
    control|=(uint32_t)config->flow_ctrl<<20;
    value=config->dst_hs_select;
    if (value>1) return -1;
    uint32_t low=value<<10;
    value=config->src_hs_select;
    if (value>1) return -1;
    low|=value<<11;
    uint32_t destination_signal=config->dst_hs_per;
    uint32_t source_signal=config->src_hs_per;
    uint32_t high=(destination_signal<<11)|(source_signal<<7);
    open_cfw_gx8002_dma_clear(channel);
    uint32_t offset=88u*channel;
    uint32_t base=open_cfw_gx8002_dma_state[0];
    uint32_t translated_source=open_cfw_gx8002_dma_bus_address(source);
    *(volatile uint32_t *)(uintptr_t)(base+offset)=translated_source;
    base=open_cfw_gx8002_dma_state[0];
    uint32_t translated_destination=open_cfw_gx8002_dma_bus_address(destination);
    uint32_t latest_base=open_cfw_gx8002_dma_state[0];
    *(volatile uint32_t *)(uintptr_t)(base+offset+8)=translated_destination;
    *(volatile uint32_t *)(uintptr_t)(latest_base+offset+0x18)=control;
    *(volatile uint32_t *)(uintptr_t)(latest_base+offset+0x40)=low;
    *(volatile uint32_t *)(uintptr_t)(latest_base+offset+0x44)=high|2u;
    int32_t quotient=length/4095;
    uint32_t count=(uint32_t)quotient+(length%4095!=0);
    if (count*24u>416u) return -1;
    uint32_t pattern[4];
    pattern[0]=translated_source;
    pattern[1]=translated_destination;
    /* pattern[2] is not consumed by the recovered descriptor builder. */
    pattern[3]=control;
    width=config->trans_width;
    uint32_t list=open_cfw_gx8002_dma_state[channel+218];
    open_cfw_gx8002_dma_descriptors(pattern,(volatile uint32_t *)(uintptr_t)list,
                                   (int32_t)count,length,(uint8_t)(1u<<width));
    base=open_cfw_gx8002_dma_state[0];
    list=open_cfw_gx8002_dma_state[channel+218];
    uint32_t translated_list=open_cfw_gx8002_dma_bus_address(list);
    *(volatile uint32_t *)(uintptr_t)(base+offset+0x10)=translated_list;
    return 0;
}
