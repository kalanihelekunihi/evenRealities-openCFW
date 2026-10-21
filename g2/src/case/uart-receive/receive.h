#ifndef CASE_UART_RECEIVE_OFFLINE_H
#define CASE_UART_RECEIVE_OFFLINE_H
#include <stdint.h>
typedef struct {volatile uint32_t CR1,CR2,CR3,BRR,GTPR,RTOR,RQR,ISR,ICR,RDR;} case_uart_rx_regs;
typedef struct case_uart_rx case_uart_rx;
struct case_uart_rx {case_uart_rx_regs *Instance;uint8_t pad[84];uint8_t *pRxBuffPtr;uint16_t RxXferSize,RxXferCount,Mask;uint8_t pad2[10];uint32_t ReceptionType,RxEventType;void (*RxISR)(case_uart_rx *);uint8_t tail[20];uint32_t RxState,ErrorCode;};
void case_uart_rx8(case_uart_rx *h);
void case_uart_rx16(case_uart_rx *h);
#endif
