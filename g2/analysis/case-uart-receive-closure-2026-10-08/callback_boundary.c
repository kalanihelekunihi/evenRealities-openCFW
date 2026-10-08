/* Synthetic boundary markers; actual product completion bodies are not tested. */
#include "receive.h"
void HAL_UART_RxCpltCallback(case_uart_rx *h){(void)h;*(volatile uint32_t *)0x20003000u=1;}
void HAL_UARTEx_RxEventCallback(case_uart_rx *h,uint16_t n){(void)h;*(volatile uint32_t *)0x20003000u=2;*(volatile uint32_t *)0x20003004u=n;}
