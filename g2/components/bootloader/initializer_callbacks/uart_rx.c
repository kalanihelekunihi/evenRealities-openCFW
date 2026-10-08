/* Independent locked f89a4c46 UART receive reconstruction.
 * Borrowed destination/count/callback pointers; no allocation or drain claim. */
#include "uart_rx.h"
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_critical_save(void);
extern void opencfw_boot_delay_us_math(uint32_t);
extern uint32_t opencfw_boot_uart_tx_ring_add(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_boot_uart_tx_ring_get(uint32_t,uint32_t,uint32_t);
static void restore(uint32_t mask){__asm__ volatile("msr primask,%0"::"r"(mask):"memory");}
uint32_t opencfw_boot_uart_rx_claim(uint32_t context,uint32_t descriptor){
 uint32_t irq=opencfw_bl_critical_save(),status=0;
 if(B(context+0x11a))status=0x08000005;
 else{
  B(context+0x11a)=1;B(context+0x98)=B(descriptor+0x34);
  for(unsigned i=0;i<7;i++)W(context+0x64+4*i)=W(descriptor+4*i);
  W(context+0x9c)=0;
 }
 restore(irq);return status;
}
uint32_t opencfw_boot_uart_rx_cancel(uint32_t context){
 uint32_t irq=opencfw_bl_critical_save(),status=0;
 if(B(context+0x11a)==1){
  B(context+0x11a)=0;
  for(unsigned i=0;i<56;i++)B(context+0x64+i)=0;
  W(context+0x9c)=0;
 }else status=7;
 restore(irq);return status;
}
uint32_t opencfw_boot_uart_rx_fifo(uint32_t context,uint32_t destination,
 uint32_t requested,uint32_t *transferred){
 uint32_t base=0x40039000+(W(context+0x28)<<12),n=0,status=0;
 while(n<requested&&!(W(base+0x18)&0x10)){
  uint32_t value=W(base);
  if(value&0xf00){status=0x08000000;break;}
  /* Stock NULL destination drains without incrementing n. */
  if(destination){B(destination+n)=(uint8_t)value;++n;}
 }
 if(transferred)*transferred=n;return status;
}
uint32_t opencfw_boot_uart_rx_collect(uint32_t context){
 uint8_t local[32];uint32_t n,irq=opencfw_bl_critical_save();
 uint32_t status=opencfw_boot_uart_rx_fifo(context,(uint32_t)(uintptr_t)local,32,&n);
 if(!status&&!opencfw_boot_uart_tx_ring_add(context+0x4c,(uint32_t)(uintptr_t)local,n))status=0x08000001;
 restore(irq);return status;
}
void opencfw_boot_uart_rx_pump(uint32_t context){
 if(B(context+0xdd))(void)opencfw_boot_uart_rx_collect(context);
 if(!B(context+0x11a))return;
 uint32_t irq=opencfw_bl_critical_save(),n=0,callback_failed=0;
 uint32_t remaining=W(context+0x68)-W(context+0x9c);
 uint32_t destination=W(context+0x64)+W(context+0x9c);
 if(B(context+0xdd)){
  uint32_t available=W(context+0x54);n=remaining<available?remaining:available;
  if(!(uint8_t)opencfw_boot_uart_tx_ring_get(context+0x4c,destination,n)){
   B(context+0x11a)=0;
   if(W(context+0x74)){
    ((void(*)(uint32_t,uint32_t))(uintptr_t)W(context+0x74))(1,W(context+0x78));
    callback_failed=1;
   }
  }
 }else (void)opencfw_boot_uart_rx_fifo(context,destination,remaining,&n);
 if(!callback_failed)W(context+0x9c)+=n;
 restore(irq);
 if(callback_failed)return;
 if(W(context+0x6c))W(W(context+0x6c))=W(context+0x9c);
 if(W(context+0x9c)==W(context+0x68)){
  B(context+0x11a)=0;
  if(W(context+0x74))((void(*)(uint32_t,uint32_t))(uintptr_t)W(context+0x74))(0,W(context+0x78));
 }
}
uint32_t opencfw_boot_uart_rx_start(uint32_t context,uint32_t descriptor){
 if(W(descriptor+8))W(W(descriptor+8))=0;
 uint32_t status=opencfw_boot_uart_rx_claim(context,descriptor);
 if(!status)opencfw_boot_uart_rx_pump(context);return status;
}
uint32_t opencfw_boot_uart_rx_blocking(uint32_t context,uint32_t descriptor){
 uint32_t status=opencfw_boot_uart_rx_start(context,descriptor),polls=0;
 if(status)return status;
 for(;;){
  if(!B(context+0x11a))return 0;
  opencfw_boot_uart_rx_pump(context);opencfw_boot_delay_us_math(1000);
  if(W(descriptor+12)!=0xffffffff&&++polls==W(descriptor+12)){
   B(context+0x11a)=0;return 4;
  }
 }
}
