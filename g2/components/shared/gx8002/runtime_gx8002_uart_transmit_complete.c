/* SPDX-License-Identifier: MIT */
/* Recovered codec 0xc650..0xc670. Callback fields are reloaded after drain. */
#include <stdint.h>
extern void open_cfw_gx8002_dma_release(uint32_t);
extern void open_cfw_gx8002_uart_flush(uint32_t);
void open_cfw_gx8002_uart_transmit_complete(volatile uint32_t *descriptor)
{
    open_cfw_gx8002_dma_release(descriptor[31]);
    descriptor[31]=UINT32_MAX;
    open_cfw_gx8002_uart_flush(descriptor[0]);
    uint32_t callback=descriptor[27];
    uint32_t private_data=descriptor[28];
    uint32_t port=descriptor[0];
    ((void (*)(uint32_t,uint32_t))(uintptr_t)callback)(port,private_data);
}
