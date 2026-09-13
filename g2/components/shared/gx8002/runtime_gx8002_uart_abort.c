/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];
extern int open_cfw_gx8002_dma_abort(uint32_t);

/* Recovered package 0xc7a8/0xc7c0; valid allocated channels are 0/1. */
int open_cfw_gx8002_uart_transmit_abort_dma(volatile uint32_t *descriptor)
{
    uint32_t channel=descriptor[31];
    if ((int32_t)channel>=0) {
        (void)open_cfw_gx8002_dma_abort(channel);
        descriptor[31]=UINT32_MAX;
    }
    return 0;
}
int open_cfw_gx8002_uart_receive_abort_dma(volatile uint32_t *descriptor)
{
    uint32_t channel=descriptor[26];
    if ((int32_t)channel>=0) {
        (void)open_cfw_gx8002_dma_abort(channel);
        descriptor[26]=UINT32_MAX;
    }
    return 0;
}

/* Recovered package 0xcc74/0xcc90. Caller supplies a valid UART port. */
int open_cfw_gx8002_uart_transmit_abort(uint32_t port)
{
    volatile uint32_t *descriptor=open_cfw_gx8002_uart_descriptors[port];
    if (descriptor[11]) (void)open_cfw_gx8002_uart_transmit_abort_dma(descriptor);
    return 0;
}
int open_cfw_gx8002_uart_receive_abort(uint32_t port)
{
    volatile uint32_t *descriptor=open_cfw_gx8002_uart_descriptors[port];
    if (descriptor[11]) (void)open_cfw_gx8002_uart_receive_abort_dma(descriptor);
    return 0;
}
