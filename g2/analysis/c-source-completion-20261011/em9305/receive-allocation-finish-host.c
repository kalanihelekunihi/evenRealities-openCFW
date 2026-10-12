#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n,phase;static char trace[32];static uintptr_t source=0x840000,packet=0x850002;static uint32_t chosen_expected,size_expected;
static void mark(char c){trace[n++]=c;}
static uint32_t id_callback(uint32_t id){assert(id==3);mark('I');*(uint16_t *)(source+566)=17;return scenario==0?7:0;}
uint32_t opencfw_em9305_radio_query_3253a4(uint32_t size){assert(size==(scenario==1?17:10));mark('A');if(scenario==7)return 0;*(uint8_t *)0x805ab5=9;*(uint8_t *)(source+337)=255;return 0x820002;}
uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t id,uintptr_t event){assert(phase==1&&queue==0x805abc&&id==3&&event==packet-2);assert(*(uint8_t *)(packet-2)==0x34&&*(uint8_t *)(packet-1)==0x12);mark('E');*(uint8_t *)0x805b18=99;return 0;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t events){assert(handler==99&&events==2);mark('P');return 0x31;}
uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t p){assert(p==chosen_expected);mark('R');return 0x32;}
static uint32_t payload_callback(uint32_t low,uint32_t high){if(scenario==4)assert(low==0x1234&&high==0);else assert(low==0x12345678&&high==0xabcdef01);mark('C');*(uint16_t *)(source+566)=65535;return 0;}
uint32_t opencfw_em9305_radio_request_start_303cd8(uint32_t chosen,uint32_t size){assert(chosen==chosen_expected&&size==size_expected);mark('Q');return 0x33;}
/* Authenticated receive allocation/finalization324ea4,325374,3253c4.
 * Preserve callback-presence tests, credit decrements, fresh counter reads
 * and partial effects even when a later provider fails. */
uint32_t opencfw_em9305_receive_state_324ea4(uintptr_t source)
{
 uint32_t kind=*(volatile uint8_t *)(source+344u);
 if(kind==0u){
  uintptr_t owner=*(volatile uint32_t *)(uintptr_t)0x805cd8u;
  if(owner!=0u){
   uintptr_t callback=*(volatile uint32_t *)(owner+16u);
   if(callback!=0u){
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint32_t delta=(uint32_t)(source-base),index;
    index=delta/912u;
    uint32_t response=((uint32_t (*)(uint32_t))callback)((uint8_t)index);
    if(response!=0u)return 0u;
    uint32_t size=*(volatile uint16_t *)(source+566u);
    return opencfw_em9305_radio_query_3253a4(size);
   }
  }
 }
 uint32_t decoded=*(volatile uint8_t *)(source+346u);
 uint32_t previous=*(volatile uint8_t *)(source+337u);
 if(((decoded^previous)&1u)!=0u)return 0u;
 uint32_t size=*(volatile uint16_t *)(source+566u);
 uint32_t length=*(volatile uint8_t *)(source+349u);
 if(size+4u<length||length==0u||kind-1u>=3u){
  *(volatile uint8_t *)(source+337u)=(uint8_t)(previous+1u);
  return 0u;
 }
 uint32_t credits=*(volatile uint8_t *)(uintptr_t)0x805ab5u;
 if(credits==0u)return 0xffffffffu;
 uint32_t allocation=opencfw_em9305_radio_query_3253a4(size);
 if(allocation==0u)return 0xffffffffu;
 credits=*(volatile uint8_t *)(uintptr_t)0x805ab5u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8052ccu;
 *(volatile uint8_t *)(uintptr_t)0x805ab5u=(uint8_t)(credits-1u);
 if(callback!=0u&&*(volatile uint8_t *)(source+109u)!=0u&&*(volatile uint8_t *)(source+111u)==0u){
  uint32_t low=*(volatile uint32_t *)(source+464u);
  uint32_t high=*(volatile uint32_t *)(source+468u);
  uint32_t next=low+1u;
  *(volatile uint32_t *)(source+464u)=next;
  *(volatile uint32_t *)(source+468u)=high+(next<low);
 }
 previous=*(volatile uint8_t *)(source+337u);
 *(volatile uint8_t *)(source+337u)=(uint8_t)(previous+1u);
 return allocation;
}
uint32_t opencfw_em9305_receive_packet_publish_325374(uintptr_t packet,uint32_t value,uint32_t id)
{
 packet-=2u;
 *(volatile uint8_t *)packet=(uint8_t)value;
 *(volatile uint8_t *)(packet+1u)=(uint8_t)(value>>8);
 (void)opencfw_em9305_ll_event_enqueue(0x805abcu,(uint8_t)id,packet);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 return opencfw_em9305_wsf_event_post(handler,2u);
}
uint32_t opencfw_em9305_receive_packet_finish_3253c4(uintptr_t source,uintptr_t packet,uint32_t data,uint32_t success)
{
 uintptr_t chosen=data!=0u?data:packet;
 if(data!=0u){
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uint32_t value=*(volatile uint16_t *)(source+262u);
  uint32_t delta=(uint32_t)(source-base),index;
  index=delta/912u;
  (void)opencfw_em9305_receive_packet_publish_325374(packet,value,(uint8_t)index);
 }
 if(success==0u){
  if(chosen!=0u)return opencfw_em9305_receive_packet_release_3253bc(chosen);
  return (uint32_t)source;
 }
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8052ccu;
 if(callback!=0u&&*(volatile uint8_t *)(source+109u)!=0u){
  uint32_t mode=*(volatile uint8_t *)(source+111u);
  if(mode==1u){
   uint32_t value=*(volatile uint16_t *)(source+262u);
   (void)((uint32_t (*)(uint32_t,uint32_t))callback)(value,0u);
  }else if(mode==0u){
   uint32_t high=*(volatile uint32_t *)(source+468u);
   uint32_t low=*(volatile uint32_t *)(source+464u);
   (void)((uint32_t (*)(uint32_t,uint32_t))callback)(low,high);
  }
 }
 uint32_t size=*(volatile uint16_t *)(source+566u);
 return opencfw_em9305_radio_request_start_303cd8((uint32_t)chosen,(uint16_t)(size+6u));
}

static void reset(void){memset((void *)0x800000,0,0x100000);n=0;memset(trace,0,sizeof(trace));*(uint32_t *)0x805c70=source-912*3;*(uint16_t *)(source+566)=10;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;phase=0;for(scenario=0;scenario<12;scenario++){reset();*(uint8_t *)(source+344)=scenario<2||scenario==10?0:scenario==5?4:scenario==11?3:1;*(uint8_t *)(source+346)=scenario==2?1:0;*(uint8_t *)(source+349)=scenario==3?15:scenario==4?0:7;*(uint8_t *)0x805ab5=scenario==6?0:2;*(uint8_t *)(source+109)=1;*(uint8_t *)(source+111)=scenario==11?2:0;*(uint32_t *)(source+464)=0xffffffff;*(uint32_t *)(source+468)=0xffffffff;*(uint32_t *)0x8052cc=scenario==9?0:0x1234;if(scenario<2){*(uint32_t *)0x805cd8=0x830000;*(uint32_t *)(0x830000+16)=(uint32_t)(uintptr_t)id_callback;}
unsigned result=opencfw_em9305_receive_state_324ea4(source);if(scenario==0)assert(result==0&&strcmp(trace,"I")==0);else if(scenario==1)assert(result==0x820002&&strcmp(trace,"IA")==0);else if(scenario==2)assert(result==0&&n==0&&*(uint8_t *)(source+337)==0);else if(scenario==3||scenario==4||scenario==5||scenario==10)assert(result==0&&n==0&&*(uint8_t *)(source+337)==1);else if(scenario==6)assert(result==0xffffffff&&n==0&&*(uint8_t *)(source+337)==0);else if(scenario==7)assert(result==0xffffffff&&strcmp(trace,"A")==0&&*(uint8_t *)0x805ab5==2);else{assert(result==0x820002&&strcmp(trace,"A")==0&&*(uint8_t *)0x805ab5==8&&*(uint8_t *)(source+337)==0);assert(*(uint32_t *)(source+464)==(scenario==8?0:0xffffffff)&&*(uint32_t *)(source+468)==(scenario==8?0:0xffffffff));}cases++;}
phase=1;for(scenario=0;scenario<8;scenario++){reset();*(uint16_t *)(source+262)=0x1234;*(uint8_t *)(source+109)=scenario==7?0:1;*(uint8_t *)(source+111)=scenario==4?1:scenario==6?2:0;*(uint32_t *)(source+464)=0x12345678;*(uint32_t *)(source+468)=0xabcdef01;if(scenario>=4)*(uint32_t *)0x8052cc=(uint32_t)(uintptr_t)payload_callback;uintptr_t input=scenario==0?0:packet;uint32_t data=scenario==2||scenario==4?0x820002:0;chosen_expected=data?data:input;size_expected=scenario==4||scenario==5?5:16;unsigned result=opencfw_em9305_receive_packet_finish_3253c4(source,input,data,scenario>=3);const char *expected=scenario==0?"":scenario==1?"R":scenario==2?"EPR":scenario==4?"EPCQ":scenario==5?"CQ":"Q";assert(strcmp(trace,expected)==0);assert(result==(scenario==0?source:scenario<=2?0x32:0x33));cases++;}printf("PASS %u\n",cases);}
