/* Independent observed STM32G0 UART RX/error prefix and EndRxTransfer. */
#include "uart.h"
#include <stddef.h>
_Static_assert(offsetof(case_uart,RxISR)==0x74,"RxISR");
_Static_assert(offsetof(case_uart,ErrorCode)==0x90,"ErrorCode");
extern void HAL_UART_ErrorCallback(case_uart *);
extern void case_uart_other_irq(case_uart *);
extern void case_uart_dma_boundary(case_uart *);
static void atomic_clear(volatile uint32_t *r,uint32_t mask) {
 uint32_t saved,one=1;
 __asm volatile("mrs %0, primask\nmsr primask, %1":"=r"(saved):"r"(one):"memory");
 *r &= ~mask;
 __asm volatile("msr primask, %0"::"r"(saved):"memory");
}
void case_uart_end_rx(case_uart *h) {
 atomic_clear(&h->Instance->CR1,0x120);
 atomic_clear(&h->Instance->CR3,0x10000001);
 if(h->ReceptionType==1)atomic_clear(&h->Instance->CR1,0x10);
 h->RxState=0x20;h->ReceptionType=0;h->RxISR=NULL;
}
void case_uart_error_irq(case_uart *h) {
 uint32_t isr=h->Instance->ISR,cr1=h->Instance->CR1,cr3=h->Instance->CR3;
 uint32_t errors=isr&0x80f;
 if(!errors && (isr&0x20) && ((cr1&0x20)||(cr3&0x10000000))) {
  if(h->RxISR)h->RxISR(h);return;
 }
 if(errors && ((cr3&0x10000001)||(cr1&0x4000120))) {
  if((isr&1)&&(cr1&0x100)){h->Instance->ICR=1;h->ErrorCode|=1;}
  if((isr&2)&&(cr3&1)){h->Instance->ICR=2;h->ErrorCode|=4;}
  if((isr&4)&&(cr3&1)){h->Instance->ICR=4;h->ErrorCode|=2;}
  if((isr&8)&&((cr1&0x20)||(cr3&0x10000001))){h->Instance->ICR=8;h->ErrorCode|=8;}
  if((isr&0x800)&&(cr1&0x4000000)){h->Instance->ICR=0x800;h->ErrorCode|=0x20;}
  if(h->ErrorCode) {
   if((isr&0x20)&&((cr1&0x20)||(cr3&0x10000000))&&h->RxISR)h->RxISR(h);
   uint32_t error=h->ErrorCode;
   if((h->Instance->CR3&0x40)||(error&0x28)) {
    case_uart_end_rx(h);
    if(h->Instance->CR3&0x40){case_uart_dma_boundary(h);return;}
    HAL_UART_ErrorCallback(h);
   }else {HAL_UART_ErrorCallback(h);h->ErrorCode=0;}
  }
  return;
 }
 case_uart_other_irq(h);
}
