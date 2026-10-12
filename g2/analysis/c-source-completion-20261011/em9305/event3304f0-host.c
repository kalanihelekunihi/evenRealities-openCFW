#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned allocs,sends,fallbacks,fail,status;
static unsigned char storage[6];
static uintptr_t packet_seen;
static uint32_t opencfw_em9305_dispatch_32f0a0(uintptr_t p){fallbacks++;packet_seen=p;return 0x87654321;}
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t t,uint32_t n){assert(t==14&&n==4);allocs++;return fail?0:(uintptr_t)(storage+2);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)storage);assert(storage[0]==0xa5&&storage[1]==0xa5&&storage[2]==1&&storage[3]==14&&storage[4]==32&&storage[5]==status);sends++;return 77;}
/* Native3304f0..33052c. Prepared while selected snapshot runs. Native32f0a0 saves r0 and reads packet+2; native3304f0 forwards packet and returns its r0. */

uint32_t opencfw_em9305_dispatch_3304f0(uintptr_t packet)
{
 if(*(volatile uint8_t *)(packet+2u)!=8u)
  return opencfw_em9305_dispatch_32f0a0(packet);
 uintptr_t event=opencfw_em9305_ll_event_allocate(14u,4u);
 if(event==0u)return 0u;
 *(volatile uint8_t *)(event+1u)=14u;
 *(volatile uint8_t *)(event+2u)=32u;
 /* Native STB.AB stores before subtracting2 from r0. */
 *(volatile uint8_t *)event=1u;
 uint32_t status=*(volatile uint8_t *)(packet+4u);
 *(volatile uint8_t *)(event+3u)=(uint8_t)status;
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}


int main(void){unsigned char packet[8]={0};unsigned cases=0;
for(unsigned type=0;type<256;type++)for(status=0;status<256;status++)for(fail=0;fail<2;fail++){packet[2]=type;packet[4]=status;memset(storage,0xa5,6);allocs=sends=fallbacks=0;packet_seen=0;uint32_t v=opencfw_em9305_dispatch_3304f0((uintptr_t)packet);if(type==8){assert(v==!fail&&allocs==1&&sends==!fail&&!fallbacks);}else{assert(v==0x87654321&&!allocs&&!sends&&fallbacks==1&&packet_seen==(uintptr_t)packet);}cases++;}
printf("PASS %u\n",cases);}
