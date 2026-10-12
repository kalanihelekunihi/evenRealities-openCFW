#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocation,sends,allocs;static uint32_t code,length;
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t c,uint32_t n){code=c;length=n;allocs++;*(uint8_t *)0x805718=100;return allocation?0x820000:0;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==0x81fffe);sends++;return 99;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
static uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){memcpy((void *)d,(void *)s,6);return d;}
/* Authenticated dispatch330ce0: native extended-report rejection returns1;
 * legacy rejection returns0. Allocation length wraps through low byte. */
uint32_t opencfw_em9305_dispatch_330ce0(uintptr_t input)
{
 uint32_t type=*(volatile uint8_t *)(input+2u);
 uintptr_t event;
 if(type==4u){
  event=opencfw_em9305_ll_event_allocate(14u,4u);
  if(event==0u)return 0u;
  *(volatile uint8_t *)(event+1u)=12u;
  *(volatile uint8_t *)event=1u;
  *(volatile uint8_t *)(event+2u)=32u;
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+3u);
 }else if(type==2u){
  uint32_t kind=*(volatile uint8_t *)(input+18u);
  uint32_t mask=*(volatile uint32_t *)(uintptr_t)0x8056f8u;
  uint32_t extended=kind!=255u;
  uint32_t rejected=extended;
  if((mask&(extended?1024u:2u))==0u)return rejected;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return rejected;
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  if(count>=*(volatile uint8_t *)(config+14u))return rejected;
  uint32_t length=18u;
  if(!extended)length=(uint8_t)(*(volatile uint8_t *)(input+8u)+12u);
  event=opencfw_em9305_ll_event_allocate(62u,length);
  if(event==0u)return rejected;
  *(volatile uint8_t *)(event+1u)=1u;
  *(volatile uint8_t *)event=(uint8_t)(extended?11u:2u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+10u);
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+11u);
  (void)opencfw_em9305_radio_address_copy_304604(event+4u,input+12u);
  if(extended){
   *(volatile uint8_t *)(event+10u)=*(volatile uint8_t *)(input+18u);
   (void)opencfw_em9305_radio_address_copy_304604(event+11u,input+19u);
   *(volatile uint8_t *)(event+17u)=*(volatile uint8_t *)(input+9u);
  }else{
   *(volatile uint8_t *)(event+10u)=*(volatile uint8_t *)(input+8u);
   uint32_t bytes=*(volatile uint8_t *)(input+8u);
   uintptr_t data=*(volatile uint32_t *)(input+4u);
   (void)opencfw_em9305_memcpy((void *)(event+11u),(const void *)data,bytes);
   uint32_t fresh_bytes=*(volatile uint8_t *)(input+8u);
   uint32_t tail=*(volatile uint8_t *)(input+9u);
   *(volatile uint8_t *)(event+fresh_bytes+11u)=(uint8_t)tail;
  }
  count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)(count+1u);
 }else return 0u;
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t input=0x810000;
for(unsigned type=0;type<256;type++){if(type==2||type==4)continue;*(uint8_t *)(input+2)=type;assert(opencfw_em9305_dispatch_330ce0(input)==0);cases++;}
for(unsigned alloc=0;alloc<2;alloc++){*(uint8_t *)(input+2)=4;*(uint8_t *)(input+3)=0x79;allocation=alloc;sends=allocs=0;assert(opencfw_em9305_dispatch_330ce0(input)==alloc);assert(allocs==1&&code==14&&length==4&&sends==alloc);if(alloc)assert(*(uint32_t *)0x820000==0x79200c01);cases++;}
for(unsigned extended=0;extended<2;extended++)for(unsigned mask=0;mask<4;mask++)for(unsigned feature=0;feature<2;feature++)for(unsigned count=0;count<3;count++)for(unsigned alloc=0;alloc<2;alloc++)for(unsigned bytes=0;bytes<256;bytes++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805cac=0x840000;*(uint8_t *)0x84000e=2;*(uint32_t *)0x8056f8=(mask&1?2:0)|(mask&2?1024:0);*(uint8_t *)0x8056ef=feature?32:0;*(uint8_t *)0x805718=count;*(uint8_t *)(input+2)=2;*(uint32_t *)(input+4)=0x830000;*(uint8_t *)(input+8)=bytes;*(uint8_t *)(input+9)=0xf0;*(uint8_t *)(input+10)=0x11;*(uint8_t *)(input+11)=0x22;for(unsigned n=0;n<6;n++){*(uint8_t *)(input+12+n)=n+1;*(uint8_t *)(input+19+n)=n+11;}*(uint8_t *)(input+18)=extended?7:255;for(unsigned n=0;n<256;n++)*(uint8_t *)(uintptr_t)(0x830000+n)=n;allocation=alloc;sends=allocs=0;unsigned eligible=(mask&(extended?2:1))&&feature&&count<2;unsigned expected=eligible&&alloc?1:extended;assert(opencfw_em9305_dispatch_330ce0(input)==expected);assert(allocs==eligible&&sends==(eligible&&alloc));if(eligible){assert(code==62&&length==(extended?18:(uint8_t)(bytes+12)));if(alloc){uint8_t *e=(uint8_t *)0x820000;assert(e[0]==(extended?11:2)&&e[1]==1&&e[2]==0x11&&e[3]==0x22&&!memcmp(e+4,(void *)(input+12),6));if(extended)assert(e[10]==7&&!memcmp(e+11,(void *)(input+19),6)&&e[17]==0xf0);else assert(e[10]==bytes&&!memcmp(e+11,(void *)0x830000,bytes)&&e[11+bytes]==0xf0);assert(*(uint8_t *)0x805718==101);}}cases++;}
printf("PASS %u\n",cases);}
