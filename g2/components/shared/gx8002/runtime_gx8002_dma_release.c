/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_dma_deallocate(uint32_t);
void open_cfw_gx8002_dma_release(uint32_t channel)
{
    open_cfw_gx8002_dma_deallocate(channel);
}
