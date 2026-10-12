#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned allocs,fills,sends,fail;
static uintptr_t packet_seen;
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t size){assert(type==62&&size==29);allocs++;return fail?0:0x820002;}
static uint32_t opencfw_em9305_packet_event_fill_330e78(uintptr_t event,uintptr_t packet){assert(event==0x820002);fills++;packet_seen=packet;return 77;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t event){assert(event==0x820000&&fills==1);sends++;return 99;}
/* Native event330400..33043e; guarded packet type39 projection. */
uint32_t opencfw_em9305_dispatch_330400(uintptr_t packet)
{
 if(*(volatile uint8_t *)(packet+2u)!=39u)return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056fbu&1u)==0u)return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(62u,29u);
 if(event==0u)return 0u;
 (void)opencfw_em9305_packet_event_fill_330e78(event,packet);
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t packet=0x810000;
for(unsigned type=0;type<256;type++)for(unsigned gates=0;gates<4;gates++)for(fail=0;fail<2;fail++){*(uint8_t *)(packet+2)=type;*(uint8_t *)0x8056fb=0xa4|(gates&1);*(uint8_t *)0x8056ef=0xc3|((gates&2)?32:0);allocs=fills=sends=0;packet_seen=0;unsigned guard=type==39&&gates==3;unsigned ok=guard&&!fail;assert(opencfw_em9305_dispatch_330400(packet)==ok);assert(allocs==guard&&fills==ok&&sends==ok);assert(packet_seen==(ok?packet:0));cases++;}
printf("PASS %u\n",cases);}
