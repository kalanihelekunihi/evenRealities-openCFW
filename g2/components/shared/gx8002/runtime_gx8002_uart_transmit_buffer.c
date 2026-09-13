/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];
extern uint32_t open_cfw_gx8002_irq_save(void);
extern void open_cfw_gx8002_irq_restore(uint32_t);
extern int open_cfw_gx8002_uart_transmit_dma(volatile uint32_t *, uint32_t, uint32_t);

/* Recovered from codec package 0xccac. Port validity is a caller contract. */
int open_cfw_gx8002_uart_transmit_buffer(uint32_t port, uint32_t buffer,
                                      uint32_t length, uint32_t callback,
                                      uint32_t private_data)
{
    /* Empty register constraint selects compact fifth-argument accesses
     * with the pinned C-SKY compiler; no instructions are injected. */
    register uint32_t context __asm__("r5")=private_data;
    __asm__("" : "+r"(context));
    volatile uint32_t *descriptor=open_cfw_gx8002_uart_descriptors[port];
    if (!buffer || !callback) return -1;
    descriptor[27]=callback;
    uint32_t dma=descriptor[11];
    descriptor[17]=2;
    descriptor[29]=buffer;
    descriptor[30]=length;
    descriptor[28]=context;
    descriptor[31]=UINT32_MAX;
    if (dma) {
        *(volatile uint32_t *)(uintptr_t)(descriptor[1]+0xa8)=1;
        return open_cfw_gx8002_uart_transmit_dma(descriptor, buffer, length);
    }
    uint32_t irq=open_cfw_gx8002_irq_save();
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)(descriptor[1]+4);
    *enable |= 2;
    open_cfw_gx8002_irq_restore(irq);
    return 0;
}
