#include "recovery.h"
#define W(a) (*(volatile uint32_t *)(a))
#define HAS(bit) ((W(0x40008858)>>(bit))&1)
extern void stock_delay(uint32_t);
extern uint32_t stock_wait5(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t stock_mcuctrl(uint32_t,uint8_t*);
extern uint32_t stock_pin_get(uint32_t,uint32_t*);
extern uint32_t stock_pin_set(uint32_t,uint32_t);
extern void stock_syspll_enable(void),stock_syspll_disable(void);
extern uint32_t stock_enable(uint32_t),stock_disable(uint32_t);
extern void stock_bus_flush(uint32_t,uint32_t);
static void flush_sysbus(void){(void)W(0x47ff0000);}
static uint32_t needs_xtal(void){return HAS(3)||(HAS(5)&&!HAS(6));}
static uint32_t needs_ext(void){return HAS(4)||(HAS(5)&&HAS(6));}
void clock_reset_recover(uint32_t incoming_r5){
 uint32_t saved_pin=0;
 if(!(W(0x4000885c)&2)&&(W(0x40008858)>>16)==0x5af0&&(W(0x40008858)&63)){
  if(HAS(0)||HAS(1)) W(0x400200c0)|=1;
  if(HAS(0)){W(0x400204e8)=(W(0x400204e8)&~12)|4;flush_sysbus();stock_delay(1);}
  if(HAS(2)){W(0x40004044)|=32;(void)stock_wait5(200,0x40004030,0x1000000,0x1000000,1);stock_delay(5);}
  if(needs_xtal()){uint8_t no=0;(void)stock_mcuctrl(2,&no);stock_delay(1500);}
  if(needs_ext()){(void)stock_pin_get(15,&saved_pin);(void)stock_pin_set(15,(incoming_r5&~15u)|10);}
  if(HAS(5)){
   stock_syspll_enable();W(0x400204d8)&=~2u;W(0x400204d8)&=~4u;
   W(0x400204d8)=(W(0x400204d8)&~32u)|(HAS(6)<<5);
   W(0x400204d8)|=256;W(0x400204d8)|=0x20000000;
  }
  (void)stock_enable(30);(void)stock_enable(31);(void)stock_enable(32);(void)stock_enable(33);(void)stock_enable(26);(void)stock_enable(27);
  flush_sysbus();stock_delay(5);
  W(0x40201000)|=1;W(0x40208100)|=1;W(0x40209100)|=1;W(0x400b2000)&=~1u;
  W(0x40210000)&=~0x7000000u;stock_bus_flush(0,1);stock_delay(1);
  if(HAS(0)){W(0x400204e8)=(W(0x400204e8)&~12u)|8;flush_sysbus();}
  stock_delay(20);
  W(0x40201000)|=1;W(0x40208100)|=1;W(0x40209100)|=1;W(0x400b2000)&=~1u;
  (void)stock_disable(30);(void)stock_disable(31);(void)stock_disable(32);(void)stock_disable(33);(void)stock_disable(26);(void)stock_disable(27);
  if(HAS(5)){
   W(0x400204d8)&=~0x20000000u;W(0x400204d8)&=~256u;W(0x400204d8)&=~32u;
   W(0x400204d8)|=4;W(0x400204d8)|=2;stock_syspll_disable();
  }
  if(needs_ext())(void)stock_pin_set(15,saved_pin);
  if(needs_xtal()){uint8_t no=0;(void)stock_mcuctrl(4,&no);}
  if(HAS(2))W(0x40004044)&=~32u;
  if(HAS(0)||HAS(1))W(0x400200c0)&=~1u;
 }
 W(0x40008858)=0;W(0x40008858)=(W(0x40008858)&65535)|0x5af00000;
}
