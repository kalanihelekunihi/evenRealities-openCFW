/* Fixture-only RX boundaries for the TX joint oracle. */
#include <stdint.h>
#define B __attribute__((naked,noinline,used))
B void uart_irq_rx_abort(void *h){__asm__("bx lr");}
B void uart_irq_read_sm(void *h){__asm__("bx lr");}
B uint32_t uart_irq_fifo_drain(void *h){__asm__("bx lr");}
B uint32_t uart_irq_read_abort(void *h){__asm__("bx lr");}
