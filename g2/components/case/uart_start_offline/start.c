/* Independent64ec/8d98; original ISR pointer values are ABI metadata only. */
#include "start.h"
#include <stddef.h>
_Static_assert(offsetof(case_start_handle,pRxBuffPtr)==0x58,"buffer");
_Static_assert(offsetof(case_start_handle,FifoMode)==0x64,"fifo");
_Static_assert(offsetof(case_start_handle,RxState)==0x8c,"state");
static void set(volatile uint32_t *r,uint32_t bits){uint32_t old,one=1;__asm volatile("mrs %0, primask\nmsr primask, %1":"=&r"(old):"r"(one):"memory");*r|=bits;__asm volatile("msr primask, %0"::"r"(old):"memory");}
uint32_t case_uart_begin_rx(case_start_handle *h,uint8_t *p,uint16_t n){
 h->pRxBuffPtr=p;h->RxXferSize=n;h->RxXferCount=n;h->RxISR=NULL;
 uint32_t word=h->Init.WordLength,parity=h->Init.Parity;
 h->Mask=word==0x1000?(parity?0xff:0x1ff):word==0?(parity?0x7f:0xff):word==0x10000000?(parity?0x3f:0x7f):0;
 h->ErrorCode=0;h->RxState=0x22;set(&h->Instance->CR3,1);
 if(h->FifoMode==0x20000000 && n>=h->NbRxDataToProcess){
  h->RxISR=(void (*)(case_start_handle *))(word==0x1000 && !parity?0x08008809u:0x08008a49u);
  if(parity)set(&h->Instance->CR1,0x100);set(&h->Instance->CR3,0x10000000);
 }else{
  h->RxISR=(void (*)(case_start_handle *))(word==0x1000 && !parity?0x08008759u:0x08008999u);
  set(&h->Instance->CR1,parity?0x120:0x20);
 }
 return 0;
}
uint32_t case_uart_start_api(case_start_handle *h,uint8_t *p,uint16_t n){
 if(h->RxState!=0x20)return 2;
 if(!p || !n || (h->Init.WordLength==0x1000 && !h->Init.Parity && ((uint32_t)p&1)))return 1;
 h->ReceptionType=0;
 if(h->Instance->CR2&0x800000)set(&h->Instance->CR1,0x4000000);
 return case_uart_begin_rx(h,p,n);
}
