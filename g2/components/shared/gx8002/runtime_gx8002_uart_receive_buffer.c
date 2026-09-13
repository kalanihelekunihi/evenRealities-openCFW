/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];
extern uint32_t open_cfw_gx8002_irq_save(void);
extern void open_cfw_gx8002_irq_restore(uint32_t);
extern int open_cfw_gx8002_uart_receive_dma(volatile uint32_t *, uint32_t, uint32_t);

/* Recovered from codec package 0xcd0c. Port validity is a caller contract. */
int open_cfw_gx8002_uart_receive_buffer(uint32_t port, uint32_t buffer,
                                      uint32_t length, uint32_t callback,
                                      uint32_t private_data)
{
    /* Materialize the fifth argument in a compact-addressable register.
     * The empty constraint emits no instructions; it avoids wide context
     * loads/stores with the pinned C-SKY compiler and fits the stock slot. */
    register uint32_t context __asm__("r5")=private_data;
    __asm__("" : "+r"(context));
    volatile uint32_t *descriptor=open_cfw_gx8002_uart_descriptors[port];
    if (!buffer || !callback) return -1;
    descriptor[22]=callback;
    uint32_t dma=descriptor[11];
    descriptor[16]=2;
    descriptor[24]=buffer;
    descriptor[25]=length;
    descriptor[23]=context;
    descriptor[26]=UINT32_MAX;
    if (dma) {
        *(volatile uint32_t *)(uintptr_t)(descriptor[1]+0xa8)=1;
        return open_cfw_gx8002_uart_receive_dma(descriptor, buffer, length);
    }
    uint32_t irq=open_cfw_gx8002_irq_save();
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)(descriptor[1]+4);
    *enable |= 1;
    open_cfw_gx8002_irq_restore(irq);
    return 0;
}
