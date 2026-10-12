#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n,elapsed_calls,fail;static char trace[32];static uintptr_t source=0x840000;static uint32_t reason_expected;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_pal_current_time(void){mark('T');return 300;}
uint32_t opencfw_em9305_auxiliary_guard_interval(void){mark('G');return scenario==8?0xffffffff:200;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t timestamp,uint32_t reference){assert(reference==77);mark('E');elapsed_calls++;if(timestamp==300)return scenario==2?2051:scenario==3?2050:100;if(elapsed_calls==1){assert(timestamp==11);*(uint32_t *)(source+20)=0x820000;return scenario==6?2600:scenario==7?2500:1000;}assert(timestamp==1234);return scenario==5?500:scenario==7?550:600;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes){assert(bytes==4);mark('A');*(uint32_t *)0x805c70=source-912*3-42;*(uint8_t *)0x805b18=77;return fail?0:0x850000;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t message){assert(handler==77&&message==0x850000);assert(*(uint16_t *)message==3&&*(uint8_t *)(message+2)==1&&*(uint8_t *)(message+3)==(uint8_t)reason_expected);mark('S');return 0x55;}
/* Authenticated receive time check319838..319890 and termination325c08..325c40. */
uint32_t opencfw_em9305_receive_check_319838(uintptr_t source,uint32_t reference,uint32_t length)
{
 uint32_t flags=*(volatile uint8_t *)(source+4u);
 if((flags&4u)!=0u)return 0u;
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uint32_t interval=*(volatile uint16_t *)(source+266u),limit;
 uintptr_t object=*(volatile uint32_t *)(source+20u);
 limit=interval*1250u;
 if(object!=0u){
  uint32_t timestamp=*(volatile uint32_t *)(object+8u);
  uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(timestamp,reference);
  if(limit>=elapsed){
   object=*(volatile uint32_t *)(source+20u);
   timestamp=*(volatile uint32_t *)(object+8u);
   limit=opencfw_em9305_auxiliary_elapsed_303f8c(timestamp,reference);
  }
 }
 uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(now,reference);
 uint32_t required=elapsed+(guard+length)+150u;
 return limit<required;
}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,uint32_t reason)
{
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 *(volatile uint8_t *)(message+3u)=(uint8_t)reason;
 uint32_t delta=(uint32_t)(source-base),index;
 index=delta/912u;
 *(volatile uint8_t *)(message+2u)=1u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)message=(uint8_t)index;
 return opencfw_em9305_wsf_task_message_send(handler,message);
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<9;scenario++){memset((void *)0x800000,0,0x100000);n=elapsed_calls=0;memset(trace,0,sizeof(trace));*(uint16_t *)(source+266)=scenario==8?0:2;*(uint8_t *)(source+4)=scenario==0?4:0;if(scenario>=4&&scenario<=7)*(uint32_t *)(source+20)=0x830000;*(uint32_t *)(0x830000+8)=11;*(uint32_t *)(0x820000+8)=1234;unsigned result=opencfw_em9305_receive_check_319838(source,77,100);assert(result==(scenario==2||scenario==5||scenario==8));assert(strcmp(trace,scenario==0?"":scenario>=4&&scenario<=7?scenario==6?"TGEE":"TGEEE":"TGE")==0);cases++;}
for(fail=0;fail<2;fail++){for(unsigned reason=0;reason<256;reason++){n=0;memset(trace,0,sizeof(trace));memset((void *)0x850000,0xa5,4);reason_expected=reason|0xffffff00;unsigned result=opencfw_em9305_receive_terminate_325c08(source,reason_expected);assert(result==(fail?0:0x55)&&strcmp(trace,fail?"A":"AS")==0);if(fail)assert(*(uint32_t *)0x850000==0xa5a5a5a5);cases++;}}printf("PASS %u\n",cases);}
