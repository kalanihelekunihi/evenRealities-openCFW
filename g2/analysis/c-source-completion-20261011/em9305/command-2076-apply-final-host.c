#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocation,mutate,sends,events;static uint8_t captured[8];
static uint32_t host_mpy(uint32_t id){assert(id<8);return id*912;}
static uint32_t host_div(uint32_t d){assert((int32_t)d%912==0);return (uint32_t)((int32_t)d/912);}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);if(mutate)*(uint32_t *)0x805c70=0x820000+912;*(uint8_t *)0x805b18=71;return allocation?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==71&&m==0x840000);sends++;return 123;}
static uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){memcpy(captured,(void *)p,8);events++;return 85;}
/* Authenticated command apply32754c and derive/refresh317b80/317ba8/323268.
 * Native query helper preserves R3/R12; C makes those row/base captures explicit. */
uint32_t opencfw_em9305_command_delta_317b80(uintptr_t row)
{
 uint32_t selector=*(volatile uint8_t *)(row+766u);
 int32_t baseline=*(volatile int8_t *)(row+268u);
 int32_t current=*(volatile int8_t *)(row+selector+553u);
 int32_t difference=baseline<=current?current-baseline:baseline-current;
 uint32_t magnitude=(uint32_t)(difference<0?-difference:difference);
 return (uint8_t)magnitude;
}
uint32_t opencfw_em9305_command_derive_317ba8(uintptr_t row)
{
 uint32_t delta=opencfw_em9305_command_delta_317b80(row);
 uint32_t fourth=*(volatile uint8_t *)(row+779u);
 uint32_t third=*(volatile uint8_t *)(row+778u);
 uint32_t state=*(volatile uint8_t *)(row+782u);
 uint32_t second=*(volatile uint8_t *)(row+777u);
 uint32_t first=*(volatile uint8_t *)(row+776u);
 uint32_t lower=(uint8_t)(third-fourth),upper=(uint8_t)(second+first);
 if(state==2u){
  if(delta<lower)return 0u;
  return 1u+(delta>=(uint8_t)(first-second));
 }
 if(state==1u){
  if(upper<delta)return 2u;
  return delta>=lower;
 }
 if(state!=0u)return 1u;
 if(upper<delta)return 2u;
 return (uint8_t)(fourth+third)<delta;
}
uint32_t opencfw_em9305_command_refresh_323268(uintptr_t row)
{
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t delta=opencfw_em9305_command_delta_317b80(row);
 uint32_t difference=(uint32_t)(row-base),quotient;
 quotient=host_div(difference);
 _Alignas(4) uint8_t event[8];
 *(volatile uint8_t *)(event+6u)=(uint8_t)delta;
 uint32_t state=*(volatile uint8_t *)(row+782u);
 *(volatile uint16_t *)(event+2u)=48u;
 *(volatile uint8_t *)(event+7u)=(uint8_t)state;
 *(volatile uint16_t *)(event+4u)=(uint8_t)quotient;
 *(volatile uint16_t *)event=(uint8_t)quotient;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
uint32_t opencfw_em9305_command_apply_32754c(uint32_t id,uint32_t unused)
{
 (void)unused;
 uint32_t offset;
 offset=host_mpy(id);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t row=base+offset;
 uintptr_t selector=row+(*(volatile uint8_t *)(row+2u)!=0u?197u:189u);
 if(*(volatile uint8_t *)(row+770u)!=2u)return 12u;
 uint32_t mode=*(volatile uint8_t *)(row+77u);
 uint32_t selected=*(volatile uint8_t *)selector;
 uint32_t second_offset;
 second_offset=host_mpy(id);
 uint32_t extra=(mode==3u)&(selected==1u);
 uint32_t effective=mode+extra;
 uint32_t low_effective=(uint8_t)effective;
 uint32_t status=*(volatile uint8_t *)(row+low_effective+553u);
 uintptr_t captured_row=base+second_offset;
 if(status==0x7fu){
  *(volatile uint8_t *)(captured_row+771u)=1u;
  *(volatile uint8_t *)(captured_row+784u)=1u;
  uint32_t reduced=mode-(1u&~extra);
  uint32_t query=*(volatile uint8_t *)(captured_row+reduced+332u);
  if(query==0x7eu){
   uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   uint32_t fallback=*(volatile uint8_t *)(config+40u);
   *(volatile uint8_t *)(captured_row+low_effective+331u)=(uint8_t)fallback;
  }
  uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
  if(message==0u)return 7u;
  *(volatile uint16_t *)(message+2u)=0x2801u;
  uintptr_t fresh_base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  *(volatile uint8_t *)(message+5u)=(uint8_t)effective;
  uint32_t difference=(uint32_t)(row-fresh_base),quotient;
  quotient=host_div(difference);
  *(volatile uint8_t *)(message+4u)=0u;
  uint32_t short_id=(uint8_t)quotient;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint16_t *)message=(uint16_t)short_id;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }else{
  uint32_t derived=opencfw_em9305_command_derive_317ba8(row);
  *(volatile uint8_t *)(captured_row+782u)=(uint8_t)derived;
  (void)opencfw_em9305_command_refresh_323268(row);
 }
 *(volatile uint8_t *)(row+770u)=1u;
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t row=0x820000+912;unsigned cases=0;
for(int baseline=-128;baseline<128;baseline++)for(int current=-128;current<128;current++){*(uint8_t *)(row+766)=5;*(int8_t *)(row+268)=baseline;*(int8_t *)(row+558)=current;int diff=baseline-current;unsigned expected=(uint8_t)(diff<0?-diff:diff);assert(opencfw_em9305_command_delta_317b80(row)==expected);cases++;}
for(unsigned state=0;state<4;state++)for(unsigned delta=0;delta<128;delta++)for(unsigned first=0;first<260;first+=13)for(unsigned second=0;second<260;second+=17){*(uint8_t *)(row+766)=5;*(int8_t *)(row+268)=0;*(int8_t *)(row+558)=delta;*(uint8_t *)(row+776)=first;*(uint8_t *)(row+777)=second;*(uint8_t *)(row+778)=23;*(uint8_t *)(row+779)=7;*(uint8_t *)(row+782)=state;unsigned upper=(uint8_t)((uint8_t)first+(uint8_t)second);unsigned expected=state==2?(delta<16?0:1+(delta>=(uint8_t)((uint8_t)first-(uint8_t)second))):state==1?(upper<delta?2:delta>=16):state==0?(upper<delta?2:30<delta):1;assert(opencfw_em9305_command_derive_317ba8(row)==expected);cases++;}
*(uint32_t *)0x805c70=0x820000;*(uint8_t *)(row+766)=15;*(int8_t *)(row+268)=0;*(int8_t *)(row+568)=11;*(uint8_t *)(row+782)=2;events=0;assert(opencfw_em9305_command_refresh_323268(row)==85);assert(events==1&&*(uint16_t *)captured==1&&*(uint16_t *)(captured+2)==48&&*(uint16_t *)(captured+4)==1&&captured[6]==11&&captured[7]==2);cases++;
for(unsigned state=0;state<4;state++)for(unsigned role=0;role<2;role++)for(unsigned mode=1;mode<6;mode++)for(unsigned select=0;select<3;select++)for(unsigned sentinel=0;sentinel<2;sentinel++)for(unsigned alloc=0;alloc<2;alloc++)for(unsigned change=0;change<2;change++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805c70=0x820000;*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810028=0x49;*(uint8_t *)(row+2)=role;*(uint8_t *)(row+770)=state;*(uint8_t *)(row+77)=mode;*(uint8_t *)(row+(role?197:189))=select;unsigned extra=mode==3&&select==1,effective=mode+extra;*(uint8_t *)(row+effective+553)=sentinel?127:20;*(uint8_t *)(row+mode-(1-extra)+332)=126;*(uint8_t *)(row+766)=15;*(int8_t *)(row+268)=0;*(int8_t *)(row+568)=11;*(uint8_t *)(row+776)=30;*(uint8_t *)(row+777)=5;*(uint8_t *)(row+778)=23;*(uint8_t *)(row+779)=7;allocation=alloc;mutate=change;sends=events=0;unsigned expected=state!=2?12:sentinel&&!alloc?7:0;assert(opencfw_em9305_command_apply_32754c(1,0xabcdef)==expected);assert(sends==(state==2&&sentinel&&alloc)&&events==(state==2&&!sentinel));assert(*(uint8_t *)(row+770)==(expected==0?1:state));if(state==2&&sentinel){assert(*(uint8_t *)(row+771)==1&&*(uint8_t *)(row+784)==1&&*(uint8_t *)(row+effective+331)==0x49);if(alloc)assert(*(uint16_t *)0x840000==(change?0:1)&&*(uint16_t *)0x840002==0x2801&&*(uint8_t *)0x840004==0&&*(uint8_t *)0x840005==effective);}cases++;}
printf("PASS %u\n",cases);}
