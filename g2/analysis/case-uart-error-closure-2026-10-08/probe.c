/* Compiled synthetic RX ISR; no UART data/IRQ scheduling model. */
#include "uart.h"
void case_uart_rx_probe(case_uart *h) {
 volatile uint32_t *p=(volatile uint32_t *)0x20003000u;p[0]++;p[1]=h->ErrorCode;
 if(p[2]==1)h->ErrorCode=0;
 if(p[2]==2)h->ErrorCode|=8;
}
void case_uart_other_irq(case_uart *h){(void)h;*(volatile uint32_t *)0x2000300cu=1;}
void case_uart_dma_boundary(case_uart *h){(void)h;*(volatile uint32_t *)0x2000300cu=2;}
