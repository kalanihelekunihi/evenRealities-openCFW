/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_DMA_LAYOUT_H
#define OPEN_CFW_GX8002_DMA_LAYOUT_H
#include <stdint.h>
#include <stddef.h>
/* Layout inferred from stock initialization and channel consumers.
 * Storage ownership outside this structure has not yet been established. */
struct open_cfw_gx8002_dma_layout {
    uint32_t device;
    uint32_t channel_count;
    uint8_t descriptor_storage[2][432];
    uint32_t descriptor_address[2];
    uint8_t allocated[2];
};
_Static_assert(offsetof(struct open_cfw_gx8002_dma_layout,device)==0,"DMA device");
_Static_assert(offsetof(struct open_cfw_gx8002_dma_layout,channel_count)==4,"DMA count");
_Static_assert(offsetof(struct open_cfw_gx8002_dma_layout,descriptor_storage)==8,"DMA storage");
_Static_assert(offsetof(struct open_cfw_gx8002_dma_layout,descriptor_address)==0x368,"DMA lists");
_Static_assert(offsetof(struct open_cfw_gx8002_dma_layout,allocated)==0x370,"DMA allocations");
_Static_assert(sizeof(struct open_cfw_gx8002_dma_layout)==884,"DMA inferred size");
#endif
