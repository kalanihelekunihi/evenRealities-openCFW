/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];
extern uint32_t open_cfw_gx8002_irq_save(void);
extern void open_cfw_gx8002_irq_restore(uint32_t);

int open_cfw_gx8002_uart_transmit_start(uint32_t port, uint32_t callback, uint32_t private_data)
{
    volatile uint32_t *descriptor=(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)open_cfw_gx8002_uart_descriptors+(port<<7));
    if (!callback) return -1;
    descriptor[17]=1;
    descriptor[18]=callback;
    descriptor[19]=private_data;
    uint32_t irq=open_cfw_gx8002_irq_save();
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)(descriptor[1]+4);
    *enable |= 2;
    open_cfw_gx8002_irq_restore(irq);
    return 0;
}

int open_cfw_gx8002_uart_transmit_stop(uint32_t port)
{
    volatile uint32_t *descriptor=(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)open_cfw_gx8002_uart_descriptors+(port<<7));
    descriptor[18]=0;
    descriptor[19]=0;
    uint32_t irq=open_cfw_gx8002_irq_save();
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)(descriptor[1]+4);
    *enable &= ~2u;
    open_cfw_gx8002_irq_restore(irq);
    return 0;
}
