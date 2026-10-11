/* Fixture-only lower-entry boundaries for the local-body oracle. */
#include <stdint.h>
#define B __attribute__((naked,noinline,used))
B void uart_irq_rx_abort(void *h){__asm__("bx lr");}
B void uart_irq_dma_abort(void *h){__asm__("bx lr");}
B uint32_t uart_irq_get_int_err(uint32_t m,uint32_t s){__asm__("bx lr");}
B void uart_irq_dma_complete(void *h){__asm__("bx lr");}
B void uart_irq_read_sm(void *h){__asm__("bx lr");}
B void uart_irq_write_sm(void *h){__asm__("bx lr");}
B uint32_t uart_irq_fifo_drain(void *h){__asm__("bx lr");}
B uint32_t uart_irq_read_abort(void *h){__asm__("bx lr");}
B void uart_irq_delay_us(uint32_t n){__asm__("bx lr");}
