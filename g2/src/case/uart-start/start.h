#ifndef CASE_UART_START_OFFLINE_H
#define CASE_UART_START_OFFLINE_H
#include <stdint.h>
typedef struct {volatile uint32_t CR1,CR2,CR3;} case_start_regs;
typedef struct {uint32_t BaudRate,WordLength,StopBits,Parity;uint8_t pad[24];} case_uart_init;
typedef struct case_start_handle case_start_handle;
struct case_start_handle {case_start_regs *Instance;case_uart_init Init;uint8_t pad[44];uint8_t *pRxBuffPtr;uint16_t RxXferSize,RxXferCount,Mask;uint8_t pad2[2];uint32_t FifoMode;uint16_t NbRxDataToProcess,NbTxDataToProcess;uint32_t ReceptionType,RxEventType;void (*RxISR)(case_start_handle *);uint8_t tail[20];uint32_t RxState,ErrorCode;};
uint32_t case_uart_start_api(case_start_handle *,uint8_t *,uint16_t);
/* Internal helper assumes validated caller/context, unlike public API. */
uint32_t case_uart_begin_rx(case_start_handle *,uint8_t *,uint16_t);
#endif
