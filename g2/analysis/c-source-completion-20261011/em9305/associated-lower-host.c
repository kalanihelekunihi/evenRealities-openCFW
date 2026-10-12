#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_radio_primary_timer_333bec(uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
/* Native3136ac..3136fa: exclude removed ID, recalculate strict maximum,
 * then retain callback-fresh counter and full decrement return. */
uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t id)
{
 uintptr_t root=0x805f28u;
 uint32_t existing=*(volatile uint32_t *)(root+8u);
 uint32_t selected=*(volatile uint32_t *)(root+(id&65535u)*12u+52u);
 if(selected==existing){
  uint32_t maximum=0u;
  for(uint32_t index=0u;index<8u;++index){
   if(index==id)continue;
   uint32_t candidate=*(volatile uint32_t *)(root+16u+index*4u);
   if(candidate!=0u&&candidate>maximum)maximum=candidate;
  }
  (void)opencfw_em9305_radio_primary_timer_333bec(maximum);
 }
 uint32_t count=*(volatile uint8_t *)root;
 *(volatile uint32_t *)(root+id*4u)=0u;
 count-=1u;*(volatile uint8_t *)root=(uint8_t)count;
 return count;
}
/* Native3266d0..3266f6: cleanup event4B actual byte order and R0 send return. */
uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t record,uint32_t action)
{
 uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
 if(event==0u)return 0u;
 uint32_t id=*(volatile uint8_t *)(record+1u),handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(event+3u)=(uint8_t)action;
 *(volatile uint16_t *)event=(uint16_t)id;
 *(volatile uint8_t *)(event+2u)=10u;
 return opencfw_em9305_wsf_task_message_send(handler,event);
}

static unsigned calls,value,allocation;static uint8_t event[4] __attribute__((aligned(4))),row[4];
uint32_t opencfw_em9305_radio_primary_timer_333bec(uint32_t n){calls++;value=n;*(volatile uint8_t*)0x805f28=222;return 18;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=4)abort();row[1]=93;*(volatile uint8_t*)0x805b18=72;return allocation?(uintptr_t)event:0;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p){if(handler!=72||p!=(uintptr_t)event||event[0]!=93||event[1]||event[2]!=10)abort();return 0xfeec;}
int main(void){if(mmap((void*)0x805000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned id=0;id<8;id++)for(unsigned seed=0;seed<256;seed++)for(unsigned same=0;same<2;same++){
 memset((void*)0x805f28,0,192);uint32_t maximum=0;
 for(unsigned i=0;i<8;i++){uint32_t n=((seed+i*17)&255)*0x1020304u;*(volatile uint32_t*)(uintptr_t)(0x805f38+i*4)=n;if(i!=id&&n>maximum)maximum=n;}
 *(volatile uint32_t*)(uintptr_t)(0x805f28+(id&65535)*12+52)=0x7823;*(volatile uint32_t*)0x805f30=same?0x7823:0x7824;*(volatile uint8_t*)0x805f28=seed;calls=0;
 if(opencfw_em9305_associated_schedule_drop_3136ac(id)!=(uint32_t)((same?222:seed)-1u)||calls!=same||(same&&value!=maximum)||*(volatile uint8_t*)0x805f28!=(uint8_t)((same?222:seed)-1u)||(id!=0&&*(volatile uint32_t*)(uintptr_t)(0x805f28+id*4)))abort();
 cases++;
}
for(allocation=0;allocation<2;allocation++)for(unsigned action=0;action<256;action++){
 memset(event,0x91,4);row[1]=37;*(volatile uint8_t*)0x805b18=17;
 if(opencfw_em9305_associated_cleanup_3266d0((uintptr_t)row,action)!=(allocation?0xfeec:0)||(allocation&&event[3]!=action)||(!allocation&&event[0]!=0x91))abort();
 cases++;
}
printf("PASS %u scheduler/cleanup cases\n",cases);return 0;}
