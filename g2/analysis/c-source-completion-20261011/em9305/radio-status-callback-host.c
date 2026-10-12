#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,code,second,kind,fourth;
uint32_t opencfw_em9305_pal_hook_three(uint32_t a){assert(a==16);return a;}
uint32_t opencfw_em9305_common_activate_310580(uint32_t a){(void)a;return 0;}
uint32_t opencfw_em9305_radio_measured_level_311a40(void){return (uint32_t)-123;}
static uint32_t cb(uint32_t a,uint32_t b,uint32_t c,uint32_t d){calls++;code=a;second=b;kind=c;fourth=d;return 789;}
/* Authenticated radio status callback333480..33354c. The measured signed
 * level provider311a40 remains a genuine import pending its FPU contract. */
extern uint32_t opencfw_em9305_radio_measured_level_311a40(void);
uint32_t opencfw_em9305_radio_status_ready_311ddc(void)
{ return (*(volatile uint32_t *)(uintptr_t)0xf04054u&0x20u)==0u; }
uint32_t opencfw_em9305_radio_status_valid_311df0(void)
{ return (*(volatile uint32_t *)(uintptr_t)0xf040a8u&6u)!=2u; }
uint32_t opencfw_em9305_radio_callback_333480(uint32_t event)
{
 (void)opencfw_em9305_pal_hook_three(16u);
 uintptr_t root=0x805e78u;
 uint32_t state=*(volatile uint8_t *)root;
 uint32_t adjusted=event-8u;
 if(state==1u)return adjusted;
 uint32_t code,second=0u,kind,fourth=0u;
 if(adjusted<4u){
  (void)opencfw_em9305_common_activate_310580(adjusted);
  kind=*(volatile uint8_t *)(root+33u);code=1u;
 }else if(event==5u){
  (void)opencfw_em9305_common_activate_310580(adjusted);
  kind=*(volatile uint8_t *)(root+33u);code=2u;
 }else if(event==3u){
  uint32_t first=*(volatile uint16_t *)(root+36u);
  uint32_t extra=*(volatile uint16_t *)(root+38u);
  uint32_t time=*(volatile uint32_t *)(uintptr_t)0xf01854u;
  uint32_t value=time-(first+extra);
  *(volatile uint32_t *)(root+24u)=value;
  return value;
 }else{
  uint32_t offset=*(volatile uint16_t *)(root+36u);
  uint32_t time=*(volatile uint32_t *)(uintptr_t)0xf0184cu;
  *(volatile uint32_t *)(root+20u)=time-offset;
  uint32_t ready=opencfw_em9305_radio_status_ready_311ddc();
  uintptr_t owner=*(volatile uint32_t *)(root+28u);
  uint32_t enabled=*(volatile uint8_t *)(owner+1u);
  uint32_t level=opencfw_em9305_radio_measured_level_311a40();
  kind=*(volatile uint8_t *)(root+33u);
  if(kind==2u){
   uint32_t flags=*(volatile uint32_t *)(uintptr_t)0xf04054u;
   kind=(flags&768u)==0u?4u:3u;
  }
  uint32_t quotient;
  quotient=(uint32_t)((int32_t)level/10);
  fourth=(uint32_t)(int32_t)(int8_t)quotient;
  code=3u;
  if(ready!=0u){
   uint32_t check=*(volatile uint8_t *)(uintptr_t)0x805ea5u;
   code=0u;
   if(check!=0u&&enabled!=0u&&opencfw_em9305_radio_status_valid_311df0()==0u)code=4u;
  }
  second=*(volatile uint32_t *)(root+24u);
 }
 uintptr_t callback=*(volatile uint32_t *)(root+4u);
 return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t))callback)(code,second,kind,fourth);
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);assert(mmap((void *)0xf00000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0xf00000);unsigned cases=0;for(unsigned event=0;event<16;event++)for(unsigned state=0;state<3;state++)for(unsigned bits=0;bits<8;bits++)for(unsigned valid=0;valid<4;valid++){memset((void *)0x800000,0,0x100000);memset((void *)0xf00000,0,0x10000);calls=0;*(uint8_t *)0x805e78=state;*(uint32_t *)0x805e7c=(uint32_t)(uintptr_t)cb;*(uint32_t *)0x805e94=0x830000;*(uint8_t *)0x830001=1;*(uint8_t *)0x805e99=2;*(uint16_t *)0x805e9c=10;*(uint16_t *)0x805e9e=20;*(uint32_t *)0x805e90=42;*(uint8_t *)0x805ea5=1;*(uint32_t *)0xf01854=1000;*(uint32_t *)0xf0184c=2000;*(uint32_t *)0xf04054=((bits&1)?32:0)|((bits&6)<<7);*(uint32_t *)0xf040a8=valid<<1;unsigned result=opencfw_em9305_radio_callback_333480(event);if(state==1){assert(result==event-8&&calls==0);}else if(event==3){assert(result==970&&calls==0&&*(uint32_t *)0x805e90==970);}else{assert(result==789&&calls==1);if(event>=8&&event<12){assert(code==1&&second==0&&kind==2&&fourth==0);}else if(event==5){assert(code==2&&second==0&&kind==2&&fourth==0);}else{assert(code==((bits&1)?3:valid==1?4:0)&&second==42&&kind==((bits&6)?3:4)&&fourth==(uint32_t)-12&&*(uint32_t *)0x805e8c==1990);}}cases++;}printf("PASS %u\n",cases);}
