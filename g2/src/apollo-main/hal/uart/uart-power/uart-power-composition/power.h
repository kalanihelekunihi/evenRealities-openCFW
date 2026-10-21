#ifndef UART_POWER_COMPOSITION_H
#define UART_POWER_COMPOSITION_H
#include <stdint.h>
uint32_t uart_peripheral_enable(uint32_t domain);
uint32_t uart_peripheral_disable(uint32_t domain);
uint32_t uart_save_irq(void);
#endif
