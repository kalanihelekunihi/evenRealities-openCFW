#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,calls;static char trace[16];static void mark(char c){trace[calls++]=c;}
uint32_t opencfw_em9305_radio_prepare_state_32d694(uintptr_t p,uintptr_t state,uintptr_t flag){assert(p==0x860000&&*(uint8_t *)(p+336)==255);*(uint32_t *)(state+4)=0x850000;*(uint8_t *)flag=scenario==5||scenario==6?0:1;mark('F');return scenario<=3?0:1;}
uintptr_t opencfw_em9305_ll_segment_header_323d70(uintptr_t out,uintptr_t p){assert(out==0x802808&&p==0x860000+336&&*(uint8_t *)p==1&&*(uint8_t *)(p+5)==0);mark('H');return 2;}
uint32_t opencfw_em9305_radio_request_current_303d58(uint32_t unused,uint32_t selector){(void)unused;assert(selector==1);*(uint8_t *)(0x850000+1)=9;mark('R');return 0;}
static uint32_t gate_callback(uint32_t id){assert(id==3);mark('I');return scenario==2?0:1;}
static uint32_t payload_callback(uint32_t low,uint32_t high){if(scenario==8)assert(low==55&&high==0);else assert(low==0x12345678&&high==0xabcdef01);*(uint8_t *)0x850000&=~32;mark('T');return 0;}
/* Authenticated stock334464..33446c. Runtime request template only. */
_Alignas(4) static const uint8_t opencfw_em9305_prepare_template_334464[8]={2u,0u,0u,0u,8u,40u,128u,0u};
/* Native32780c..3279a4: complete preparation graph. Native scratch is
 * intentionally uninitialized before true state provider writes it. */
uint32_t opencfw_em9305_radio_prepare_32780c(uintptr_t source,uint32_t force,uint32_t gate)
{
 _Alignas(4) uint8_t scratch[36];
 if(force==0u&&*(volatile uint8_t *)(source+347u)==0u&&
    *(volatile uint8_t *)(source+339u)==0u&&gate==0u) return 0u;
 *(volatile uint8_t *)(source+336u)=255u;
 uint32_t count=opencfw_em9305_radio_prepare_state_32d694(source,(uintptr_t)(scratch+8u),(uintptr_t)(scratch+35u));
 if(*(volatile uint8_t *)(source+379u)!=0u||count==0u){
  if(force==0u&&*(volatile uint8_t *)(source+344u)==0u){
   uintptr_t owner=*(volatile uint32_t *)(uintptr_t)0x805cd8u;
   if(owner!=0u){
    uintptr_t callback=*(volatile uint32_t *)(owner+12u);
    if(callback!=0u){
     uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
     uint32_t delta=(uint32_t)source-(uint32_t)base,index;
     index=delta/912u;
     if(((uint32_t (*)(uint32_t))callback)((uint8_t)index)==0u) return 0u;
    }
   }
  }
  *(volatile uint8_t *)(source+339u)=(uint8_t)(count!=0u);
  *(volatile uint8_t *)(source+336u)=1u;
  *(volatile uint8_t *)(source+341u)=0u;
  (void)opencfw_em9305_ll_segment_header_323d70(0x802808u,source+336u);
  uint32_t high=*(const uint32_t *)(const void *)(opencfw_em9305_prepare_template_334464+4u);
  uint32_t low=*(const uint32_t *)(const void *)opencfw_em9305_prepare_template_334464;
  *(volatile uint32_t *)(scratch+4u)=high;
  *(volatile uint32_t *)scratch=low;
  (void)opencfw_em9305_radio_request_current_303d58((uint32_t)(uintptr_t)scratch,1u);
  uint32_t prior=*(volatile uint8_t *)(source+379u);
  uint32_t result=*(volatile uint16_t *)scratch;
  *(volatile uint8_t *)(source+379u)=1u;
  *(volatile uint8_t *)(source+380u)=(uint8_t)(prior^1u);
  return (uint16_t)result;
 }
 uint32_t active=1u;
 if(*(volatile uint8_t *)(scratch+35u)==0u){
  uint32_t flags=*(volatile uint8_t *)(source+4u);
  active=0u;
  if((flags&2u)!=0u) active=*(volatile uint8_t *)(source+2u)==1u;
 }
 uintptr_t payload=*(volatile uint32_t *)(scratch+12u);
 *(volatile uint8_t *)(source+339u)=(uint8_t)active;
 *(volatile uint8_t *)(scratch+35u)=(uint8_t)active;
 uint32_t length=*(volatile uint8_t *)(payload+1u);
 *(volatile uint8_t *)(source+341u)=(uint8_t)length;
 uint32_t type=*(volatile uint8_t *)payload&3u;
 *(volatile uint8_t *)(source+336u)=(uint8_t)type;
 uint32_t bypass=0u;
 if(type==0u){
  uintptr_t owner=*(volatile uint32_t *)(uintptr_t)0x805cd8u;
  if(owner!=0u){
   uintptr_t callback=*(volatile uint32_t *)(owner+8u);
   if(callback!=0u){
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint32_t delta=(uint32_t)source-(uint32_t)base,index;
    index=delta/912u;
    (void)((uint32_t (*)(uint32_t))callback)((uint8_t)index);
    bypass=1u;
   }
  }
 }
 if(bypass==0u){
  uint32_t flags=*(volatile uint8_t *)payload&~28u;
  *(volatile uint8_t *)payload=(uint8_t)flags;
  uint32_t byte=*(volatile uint8_t *)(source+337u);
  flags|=(byte<<2)&4u;
  *(volatile uint8_t *)payload=(uint8_t)flags;
  byte=*(volatile uint8_t *)(source+338u);
  flags|=(byte<<3)&8u;
  *(volatile uint8_t *)payload=(uint8_t)flags;
  byte=*(volatile uint8_t *)(source+339u);
  flags|=(byte<<4)&16u;
  *(volatile uint8_t *)payload=(uint8_t)flags;
 }
 payload=*(volatile uint32_t *)(scratch+12u);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8052d0u;
 uint32_t captured=*(volatile uint8_t *)payload;
 if(callback!=0u&&*(volatile uint8_t *)(source+108u)!=0u){
  uint32_t mode=*(volatile uint8_t *)(source+111u);
  if(mode==1u){
   uint32_t value=*(volatile uint16_t *)(source+262u);
   (void)((uint32_t (*)(uint32_t,uint32_t))callback)(value,0u);
  }else if(mode==0u){
   uint32_t high=*(volatile uint32_t *)(source+460u);
   uint32_t low=*(volatile uint32_t *)(source+456u);
   (void)((uint32_t (*)(uint32_t,uint32_t))callback)(low,high);
  }
 }
 (void)opencfw_em9305_radio_request_current_303d58((uint32_t)(uintptr_t)(scratch+8u),count);
 payload=*(volatile uint32_t *)(scratch+12u);
 uint32_t result=*(volatile uint8_t *)(payload+1u);
 return (uint16_t)(result+((captured&32u)!=0u?3u:2u));
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<11;scenario++){memset((void *)0x800000,0,0x100000);calls=0;memset(trace,0,16);uintptr_t p=0x860000;unsigned force=scenario==1||scenario==7,gate=scenario!=0&&scenario!=10;*(uint32_t *)0x805c70=p-912*3;*(uint8_t *)(p+347)=scenario==10;*(uint8_t *)(p+379)=scenario==7;*(uint8_t *)(p+337)=1;*(uint8_t *)(p+2)=1;*(uint8_t *)(p+4)=scenario==5?2:0;*(uint8_t *)0x850000=scenario==5?0xa0:scenario==6?1:0xa1;*(uint8_t *)(0x850000+1)=7;
if(scenario==2||scenario==3||scenario==5){*(uint32_t *)0x805cd8=0x830000;*(uint32_t *)(uintptr_t)(0x830000+(scenario==5?8:12))=(uint32_t)(uintptr_t)gate_callback;}
if(scenario==8||scenario==9){*(uint32_t *)0x8052d0=(uint32_t)(uintptr_t)payload_callback;*(uint8_t *)(p+108)=1;*(uint8_t *)(p+111)=scenario==8?1:0;*(uint16_t *)(p+262)=55;*(uint32_t *)(p+456)=0x12345678;*(uint32_t *)(p+460)=0xabcdef01;}
unsigned result=opencfw_em9305_radio_prepare_32780c(p,force,gate);if(scenario==0){assert(result==0&&calls==0&&*(uint8_t *)(p+336)==0);}else if(scenario==2){assert(result==0&&strcmp(trace,"FI")==0);}else if(scenario==1||scenario==3||scenario==7){assert(result==2&&strcmp(trace,scenario==3?"FIHR":"FHR")==0);assert(*(uint8_t *)(p+339)==(scenario==7)&&*(uint8_t *)(p+379)==1&&*(uint8_t *)(p+380)==(scenario==7?0:1));}else{assert(result==(scenario==6?11:12));assert(strcmp(trace,scenario==5?"FIR":scenario==8||scenario==9?"FTR":"FR")==0);assert(*(uint8_t *)(p+341)==7&&*(uint8_t *)(p+339)==(scenario!=6));if(scenario==5)assert(*(uint8_t *)0x850000==0xa0);else if(scenario==6)assert(*(uint8_t *)0x850000==5);else assert(*(uint8_t *)0x850000==(scenario==8||scenario==9?0x95:0xb5));}cases++;}printf("PASS %u\n",cases);}
