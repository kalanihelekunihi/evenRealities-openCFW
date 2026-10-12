#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned derives,refreshes,allocation,mutate,sends;
static uint32_t host_mpy(uint32_t id){assert(id<8);return id*912;}
static uint32_t host_div(uint32_t d){assert((int32_t)d%912==0);return (uint32_t)((int32_t)d/912);}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);if(mutate)*(uint32_t *)0x805c70=0x820000+912;*(uint8_t *)0x805b18=71;return allocation?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==71&&m==0x840000);sends++;return 123;}
/* Authenticated command apply327630/327694. Native indexed word stores
 * 194/195 are scaled by four; captured base survives allocator mutation. */
extern uint32_t opencfw_em9305_command_derive_317ba8(uintptr_t);
extern uint32_t opencfw_em9305_command_refresh_323268(uintptr_t);
uint32_t opencfw_em9305_command_apply_327630(uint32_t id,uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t last)
{
 uint32_t offset;
 offset=host_mpy(id);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t row=base+offset;
 uint32_t state=*(volatile uint8_t *)(row+769u);
 *(volatile uint32_t *)(row+776u)=0u;
 *(volatile uint32_t *)(row+780u)=0u;
 *(volatile uint8_t *)(row+779u)=(uint8_t)fourth;
 *(volatile uint8_t *)(row+778u)=(uint8_t)third;
 *(volatile uint8_t *)(row+777u)=(uint8_t)second;
 *(volatile uint8_t *)(row+776u)=(uint8_t)first;
 *(volatile uint8_t *)(row+782u)=1u;
 *(volatile uint8_t *)(row+780u)=(uint8_t)last;
 *(volatile uint8_t *)(row+784u)=0u;
 if(state==1u&&*(volatile uint8_t *)(row+770u)==1u){
  uint32_t derived=opencfw_em9305_command_derive_317ba8(row);
  *(volatile uint8_t *)(row+782u)=(uint8_t)derived;
  (void)opencfw_em9305_command_refresh_323268(row);
 }else{
  *(volatile uint8_t *)(row+770u)=2u;
  *(volatile uint8_t *)(row+769u)=1u;
 }
 return 0u;
}
uint32_t opencfw_em9305_command_apply_327694(uint32_t id,uint32_t first,uint32_t second)
{
 uint32_t offset;
 offset=host_mpy(id);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t row=base+offset;
 *(volatile uint8_t *)(row+768u)=(uint8_t)(second!=0u);
 *(volatile uint8_t *)(row+767u)=(uint8_t)(first!=0u);
 if(second!=0u){
  *(volatile uint8_t *)(row+771u)=1u;
  uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
  if(message!=0u){
   *(volatile uint16_t *)(message+2u)=0x2801u;
   uintptr_t fresh_base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
   uint32_t fresh_offset;
   fresh_offset=host_mpy(id);
   *(volatile uint8_t *)(message+4u)=0u;
   uint32_t difference=(uint32_t)(row-fresh_base),quotient;
   quotient=host_div(difference);
   uintptr_t captured_row=base+fresh_offset;
   *(volatile uint16_t *)message=(uint8_t)quotient;
   uint32_t mode=*(volatile uint8_t *)(captured_row+77u);
   uint32_t extra=0u;
   if(mode==3u)extra=*(volatile uint8_t *)(captured_row+78u)==1u;
   uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
   *(volatile uint8_t *)(message+5u)=(uint8_t)(mode+extra);
   (void)opencfw_em9305_wsf_task_message_send(handler,message);
  }
 }
 return 0u;
}


uint32_t opencfw_em9305_command_derive_317ba8(uintptr_t row){assert(row==0x820000+912);derives++;*(uint32_t *)0x805c70=0x830000;return 0x145;}
uint32_t opencfw_em9305_command_refresh_323268(uintptr_t row){assert(row==0x820000+912&&*(uint8_t *)(row+782)==0x45);refreshes++;return 99;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t row=0x820000+912;
for(unsigned state=0;state<4;state++)for(unsigned ready=0;ready<4;ready++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805c70=0x820000;memset((void *)(row+776),0xaa,12);*(uint8_t *)(row+769)=state;*(uint8_t *)(row+770)=ready;derives=refreshes=0;assert(opencfw_em9305_command_apply_327630(1,0x123,0x234,0x345,0x456,0x567)==0);unsigned call=state==1&&ready==1;assert(derives==call&&refreshes==call);assert(*(uint32_t *)(row+776)==0x56453423&&*(uint8_t *)(row+780)==0x67&&*(uint8_t *)(row+781)==0&&*(uint8_t *)(row+782)==(call?0x45:1)&&*(uint8_t *)(row+783)==0&&*(uint8_t *)(row+784)==0&&*(uint8_t *)(row+785)==0xaa);if(!call)assert(*(uint8_t *)(row+769)==1&&*(uint8_t *)(row+770)==2);cases++;}
for(unsigned first=0;first<3;first++)for(unsigned second=0;second<3;second++)for(unsigned alloc=0;alloc<2;alloc++)for(unsigned change=0;change<2;change++)for(unsigned mode=0;mode<256;mode++)for(unsigned extra=0;extra<3;extra++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805c70=0x820000;*(uint8_t *)(row+77)=mode;*(uint8_t *)(row+78)=extra;*(uint8_t *)(row+771)=0xaa;allocation=alloc;mutate=change;sends=0;assert(opencfw_em9305_command_apply_327694(1,first,second)==0);assert(*(uint8_t *)(row+767)==(first!=0)&&*(uint8_t *)(row+768)==(second!=0)&&*(uint8_t *)(row+771)==(second?1:0xaa));assert(sends==(second!=0&&alloc));if(sends)assert(*(uint16_t *)0x840000==(change?0:1)&&*(uint16_t *)0x840002==0x2801&&*(uint8_t *)0x840004==0&&*(uint8_t *)0x840005==(uint8_t)(mode+(mode==3&&extra==1)));cases++;}
printf("PASS %u\n",cases);}
