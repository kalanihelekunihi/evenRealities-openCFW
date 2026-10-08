/* Locked G2 f89a4c46 UART log TX reconstruction. Byte consumption is distinct
 * from hardware drain. RX dispatch remains an explicit lower dependency. */
#include <stdint.h>
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern uint32_t opencfw_bl_critical_save(void);
extern void opencfw_boot_delay_raw(uint32_t);
extern void opencfw_boot_delay_us_math(uint32_t);
extern uint32_t opencfw_boot_uart_rx_blocking(uint32_t,uint32_t);
extern uint32_t opencfw_boot_uart_rx_start(uint32_t,uint32_t);
extern void *memset(void *,int,size_t);
static void restore(uint32_t mask){__asm__ volatile("msr primask, %0"::"r"(mask):"memory");}
NI uint32_t opencfw_boot_uart_tx_ring_add(uint32_t p,uint32_t src,uint32_t count){
 uint32_t bytes=W(p+16)*count,mask=opencfw_bl_critical_save(),ok=0;
 if(W(p+12)-W(p+8)>=bytes){for(uint32_t i=0;i<bytes;i++){if(src)B(W(p+20)+W(p))=B(src+i);uint32_t n=W(p)+1;W(p)=n-W(p+12)*(n/W(p+12));}W(p+8)+=bytes;ok=1;}
 restore(mask);return ok;
}
NI uint32_t opencfw_boot_uart_tx_ring_get(uint32_t p,uint32_t dst,uint32_t count){
 uint32_t bytes=W(p+16)*count,mask=opencfw_bl_critical_save(),ok=0;
 if(W(p+8)>=bytes){for(uint32_t i=0;i<bytes;i++){if(dst)B(dst+i)=B(W(p+20)+W(p+4));uint32_t n=W(p+4)+1;W(p+4)=n-W(p+12)*(n/W(p+12));}W(p+8)-=bytes;ok=1;}
 restore(mask);return ok;
}
NI uint32_t opencfw_boot_uart_tx_fifo(uint32_t p,uint32_t bytes,uint32_t count,uint32_t *out){
 uint32_t n=0,base=0x40039000+(W(p+0x28)<<12);
 while(n<count&&!(W(base+0x18)&0x20)){W(base)=B(bytes+n);n++;}
 if(out)*out=n;return 0;
}
NI void opencfw_boot_uart_tx_drain_ring(uint32_t p){
 uint32_t base=0x40039000+(W(p+0x28)<<12),mask=opencfw_bl_critical_save(),status=0;uint8_t byte;
 while(!(W(base+0x18)&0x20)&&opencfw_boot_uart_tx_ring_get(p+0x34,(uint32_t)(uintptr_t)&byte,1)){uint32_t n;status=opencfw_boot_uart_tx_fifo(p,(uint32_t)(uintptr_t)&byte,1,&n);if(status)break;}
 restore(mask);
}
NI uint32_t opencfw_boot_uart_tx_claim(uint32_t p,uint32_t descriptor){
 uint32_t mask=opencfw_bl_critical_save(),status=0x08000004;
 if(!B(p+0x119)){B(p+0x119)=1;B(p+0xd4)=B(descriptor+0x34);for(uint32_t i=0;i<7;i++)W(p+0xa0+4*i)=W(descriptor+4*i);W(p+0xd8)=0;B(p+0xde)=0;status=0;}
 restore(mask);return status;
}
NI void opencfw_boot_uart_tx_pump(uint32_t p){
 if(B(p+0x119)){
  uint32_t mask=opencfw_bl_critical_save(),remaining=W(p+0xa4)-W(p+0xd8),src=W(p+0xa0)+W(p+0xd8),n,failed_callback=0;
  if(B(p+0xdc)){
   uint32_t free=W(p+0x40)-W(p+0x3c);n=remaining<free?remaining:free;
   if(!(uint8_t)opencfw_boot_uart_tx_ring_add(p+0x34,src,n)){B(p+0x119)=0;if(W(p+0xb0)){((void(*)(uint32_t,uint32_t))(uintptr_t)W(p+0xb0))(1,W(p+0xb4));failed_callback=1;}}
  }else (void)opencfw_boot_uart_tx_fifo(p,src,remaining,&n);
  if(!failed_callback)W(p+0xd8)+=n;
  restore(mask);if(failed_callback)return;
  if(W(p+0xa8))W(W(p+0xa8))=W(p+0xd8);
  if(W(p+0xd8)==W(p+0xa4)&&B(p+0x119)){B(p+0x119)=0;if(W(p+0xb0))((void(*)(uint32_t,uint32_t))(uintptr_t)W(p+0xb0))(0,W(p+0xb4));}
 }
 if(B(p+0xdc))opencfw_boot_uart_tx_drain_ring(p);
}
NI uint32_t opencfw_boot_uart_tx_start(uint32_t p,uint32_t descriptor){
 if(W(descriptor+8))W(W(descriptor+8))=0;
 uint32_t status=opencfw_boot_uart_tx_claim(p,descriptor);if(!status)opencfw_boot_uart_tx_pump(p);return status;
}
NI uint32_t opencfw_boot_uart_tx_blocking(uint32_t p,uint32_t descriptor){
 uint32_t status=opencfw_boot_uart_tx_start(p,descriptor),elapsed=0;if(status)return status;
 for(;;){if(!B(p+0x119))return 0;opencfw_boot_uart_tx_pump(p);opencfw_boot_delay_us_math(1000);if(W(descriptor+12)!=0xffffffff&&++elapsed==W(descriptor+12)){B(p+0x119)=0;return 4;}}
}
NI uint32_t opencfw_boot_uart_transfer(uint32_t p,uint32_t descriptor){
 if(!p||(W(p)&0x01ffffff)!=0x01ea9e06)return 2;
 switch(B(descriptor+0x34)){case 0:return opencfw_boot_uart_tx_blocking(p,descriptor);case 1:return opencfw_boot_uart_rx_blocking(p,descriptor);case 2:return opencfw_boot_uart_tx_start(p,descriptor);case 3:return opencfw_boot_uart_rx_start(p,descriptor);default:return 1;}
}
NI uint32_t opencfw_boot_uart_log_send(uint32_t row,uint32_t borrowed,uint32_t length){
 uint32_t descriptor[14];memset(descriptor,0,sizeof descriptor);row=(uint8_t)row;uint32_t r=0x20000454+28*row;
 if(row>=4||B(r+24)!=1)return 1;
 descriptor[0]=borrowed;descriptor[1]=length;B(r+25)=0;
 uint32_t status=opencfw_boot_uart_transfer(W(r+4),(uint32_t)(uintptr_t)descriptor);
 for(uint32_t i=0;i<1000&&B(r+25)!=1;i++)opencfw_boot_delay_raw(10);
 return status!=0;
}
NI void opencfw_boot_elog_uart_output(const char *buffer,size_t length,uint32_t level){(void)level;(void)opencfw_boot_uart_log_send(1,(uint32_t)(uintptr_t)buffer,length);}
