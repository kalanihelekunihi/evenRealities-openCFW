/* Independent stock8998/8758; completion callbacks remain external boundaries. */
#include "receive.h"
#include <stddef.h>
_Static_assert(offsetof(case_uart_rx,pRxBuffPtr)==0x58,"buffer");
_Static_assert(offsetof(case_uart_rx,RxXferCount)==0x5e,"count");
_Static_assert(offsetof(case_uart_rx,Mask)==0x60,"mask");
_Static_assert(offsetof(case_uart_rx,RxState)==0x8c,"state");
extern void HAL_UART_RxCpltCallback(case_uart_rx *);
extern void HAL_UARTEx_RxEventCallback(case_uart_rx *,uint16_t);
static void clear(volatile uint32_t *p,uint32_t bits) {
 uint32_t saved,one=1;__asm volatile("mrs %0, primask\nmsr primask, %1":"=&r"(saved):"r"(one):"memory");*p &= ~bits;__asm volatile("msr primask, %0"::"r"(saved):"memory");
}
static void receive(case_uart_rx *h,uint32_t width) {
 uint16_t mask=h->Mask;
 if(h->RxState!=0x22){h->Instance->RQR|=8;return;}
 uint32_t value=h->Instance->RDR & mask;
 if(width==1)*h->pRxBuffPtr=(uint8_t)value;
 else *(uint16_t *)h->pRxBuffPtr=(uint16_t)value;
 h->pRxBuffPtr+=width;h->RxXferCount--;
 if(h->RxXferCount)return;
 clear(&h->Instance->CR1,0x120);clear(&h->Instance->CR3,1);
 h->RxState=0x20;h->RxISR=NULL;h->RxEventType=0;
 if(h->ReceptionType==1) {
  h->ReceptionType=0;clear(&h->Instance->CR1,0x10);
  if(h->Instance->ISR&0x10)h->Instance->ICR=0x10;
  HAL_UARTEx_RxEventCallback(h,h->RxXferSize);
 }else HAL_UART_RxCpltCallback(h);
}
void case_uart_rx8(case_uart_rx *h){receive(h,1);}
void case_uart_rx16(case_uart_rx *h){receive(h,2);}
