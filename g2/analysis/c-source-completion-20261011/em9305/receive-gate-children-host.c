#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t source=0x840000;static unsigned advance_result,calls;
uint32_t opencfw_em9305_radio_packet_advance_32d738(uintptr_t p){assert(p==source&&*(uint8_t *)(p+341)==0);calls++;return advance_result;}
uint32_t opencfw_em9305_radio_packet_complete_32d790(uintptr_t p){assert(p==source);return 0x55;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==0x850000-2);return 0x56;}
/* Authenticated receive gate children324f68/324fb0/3253bc/32d5ac.
 *32d5ac tests callback presence but does not call it; return is the native
 * incidental R0 (advance, pointer, mode or updated high counter word). */
uint32_t opencfw_em9305_receive_advance_32d5ac(uintptr_t source)
{
 *(volatile uint8_t *)(source+341u)=0u;
 uint32_t result=opencfw_em9305_radio_packet_advance_32d738(source);
 if(result==0u)return result;
 result=*(volatile uint32_t *)(uintptr_t)0x8052d0u;
 if(result==0u)return result;
 result=*(volatile uint8_t *)(source+108u);
 if(result==0u)return result;
 result=*(volatile uint8_t *)(source+111u);
 if(result!=0u)return result;
 uint32_t low=*(volatile uint32_t *)(source+456u);
 uint32_t high=*(volatile uint32_t *)(source+460u);
 uint32_t next=low+1u;
 result=high+(next<low);
 *(volatile uint32_t *)(source+456u)=next;
 *(volatile uint32_t *)(source+460u)=result;
 return result;
}
uint32_t opencfw_em9305_receive_gate_324f68(uintptr_t source)
{
 uint32_t decoded=*(volatile uint8_t *)(source+345u);
 uint32_t previous=*(volatile uint8_t *)(source+338u);
 uint32_t result=(decoded^previous)&1u;
 if(result==0u)return result;
 uint32_t mode=*(volatile uint8_t *)(source+341u);
 *(volatile uint8_t *)(source+338u)=(uint8_t)(previous+1u);
 if(mode!=0u){
  uint32_t kind=*(volatile uint8_t *)(source+336u);
  if(kind==3u){
   uint32_t remaining=*(volatile uint8_t *)(source+378u);
   if(remaining!=0u)*(volatile uint8_t *)(source+378u)=(uint8_t)(remaining-1u);
  }
  (void)opencfw_em9305_receive_advance_32d5ac(source);
 }else *(volatile uint8_t *)(source+379u)=0u;
 return result;
}
uint32_t opencfw_em9305_receive_finish_324fb0(uintptr_t source)
{ return opencfw_em9305_radio_packet_complete_32d790(source); }
uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t packet)
{ return opencfw_em9305_wsf_event_release(packet-2u); }


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++)for(unsigned mode=0;mode<2;mode++){memset((void *)source,0,1024);*(uint8_t *)(source+345)=a;*(uint8_t *)(source+338)=c;*(uint8_t *)(source+341)=mode;*(uint8_t *)(source+336)=3;*(uint8_t *)(source+378)=1;*(uint8_t *)(source+379)=1;advance_result=0;calls=0;unsigned gate=opencfw_em9305_receive_gate_324f68(source);assert(gate==((a^c)&1));assert(*(uint8_t *)(source+338)==(gate?(uint8_t)(c+1):c));assert(calls==(gate&&mode));assert(*(uint8_t *)(source+378)==(gate&&mode?0:1));assert(*(uint8_t *)(source+379)==(gate&&!mode?0:1));cases++;}
for(unsigned scenario=0;scenario<7;scenario++){memset((void *)source,0,1024);*(uint8_t *)(source+341)=1;advance_result=scenario!=0;*(uint32_t *)0x8052d0=scenario==1?0:0x123456;*(uint8_t *)(source+108)=scenario==2?0:1;*(uint8_t *)(source+111)=scenario==3?7:0;uint32_t low=scenario==4||scenario==5?0xffffffff:0,high=scenario==4?0xffffffff:7;*(uint32_t *)(source+456)=low;*(uint32_t *)(source+460)=high;unsigned result=opencfw_em9305_receive_advance_32d5ac(source);assert(*(uint8_t *)(source+341)==0);if(scenario<3)assert(result==0&&*(uint32_t *)(source+456)==low&&*(uint32_t *)(source+460)==high);else if(scenario==3)assert(result==7&&*(uint32_t *)(source+456)==low);else assert(result==high+(low==0xffffffff)&&*(uint32_t *)(source+456)==low+1&&*(uint32_t *)(source+460)==result);cases++;}
assert(opencfw_em9305_receive_finish_324fb0(source)==0x55);assert(opencfw_em9305_receive_packet_release_3253bc(0x850000)==0x56);cases+=2;printf("PASS %u\n",cases);}
