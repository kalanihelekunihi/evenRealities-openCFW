/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_dma_release(uint32_t);
extern void open_cfw_gx8002_dma_complete_cache(uint32_t,uint32_t);
/* Stock assumes a registered callback; no added null guard or DMA result. */
void open_cfw_gx8002_uart_receive_complete(volatile uint32_t *descriptor)
{
    open_cfw_gx8002_dma_release(descriptor[26]);
    descriptor[26]=UINT32_MAX;
    uint32_t length=descriptor[25];
    uint32_t buffer=descriptor[24];
    open_cfw_gx8002_dma_complete_cache(buffer,length);
    uint32_t callback=descriptor[22];
    uint32_t private_data=descriptor[23];
    uint32_t port=descriptor[0];
    ((void (*)(uint32_t,uint32_t))(uintptr_t)callback)(port,private_data);
}
