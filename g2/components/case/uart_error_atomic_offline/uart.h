#ifndef CASE_UART_ERROR_OFFLINE_H
#define CASE_UART_ERROR_OFFLINE_H
#include <stdint.h>
typedef struct {volatile uint32_t CR1,CR2,CR3,BRR,GTPR,RTOR,RQR,ISR,ICR;} case_usart;
typedef struct case_uart case_uart;
struct case_uart {case_usart *Instance;uint8_t pad[104];uint32_t ReceptionType;uint32_t RxEventType;void (*RxISR)(case_uart *);uint32_t TxISR;void *hdmatx,*hdmarx;uint32_t Lock,gState,RxState,ErrorCode;};
/* Selected RX/error prefix; DMAR must be clear. Other IRQ events are a boundary. */
void case_uart_error_irq(case_uart *h);
void case_uart_end_rx(case_uart *h);
#endif
