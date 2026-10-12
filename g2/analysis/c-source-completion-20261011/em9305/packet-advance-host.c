#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned removed;static uintptr_t expected;static uint8_t expectedhandler;
uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue,uintptr_t handler){uint32_t node=*(volatile uint32_t *)queue;if(!node)return 0;*(volatile uint8_t *)handler=*(volatile uint8_t *)(uintptr_t)(node+4);return node+8;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){assert(*(uint32_t *)0x805cd4==expected&&*(uint8_t *)0x8056e4==expectedhandler);assert(*(uint32_t *)queue==expected-8);removed++;*(uint32_t *)queue=0;*(uint8_t *)handler=19;*(uint32_t *)0x805cd4=0xabcdef;return 0;}
/* Authenticated packet advance 32d738..32d790.
 * The store at32d788 is the BL.D delay slot: publish the packet before
 * calling313ff0. Later child caller-saved register residue is unused. */
uint32_t opencfw_em9305_radio_packet_advance_32d738(uintptr_t source)
{
 uint8_t handler;
 uintptr_t queue=source+360u;
 uintptr_t packet=opencfw_em9305_wsf_event_peek(queue,(uintptr_t)&handler);
 if(packet==0u)return 0u;
 if(handler!=255u){
  uint32_t index=*(volatile uint8_t *)(packet+7u);
  uint32_t unit=*(volatile uint8_t *)(packet+6u);
  uint32_t length=*(volatile uint16_t *)(packet+4u);
  index+=1u;
  uint32_t product;
  product=unit*index;
  if(product<length){
   *(volatile uint8_t *)(packet+7u)=(uint8_t)index;
   return 1u;
  }
  *(volatile uint8_t *)(uintptr_t)0x8056e4u=handler;
 }else *(volatile uint8_t *)(uintptr_t)0x8056e4u=255u;
 *(volatile uint32_t *)(uintptr_t)0x805cd4u=(uint32_t)packet;
 (void)opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
 return 1u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t source=0x860000,node=0x840000,packet=node+8;unsigned cases=0;assert(opencfw_em9305_radio_packet_advance_32d738(source)==0&&removed==0);cases++;
for(unsigned handler=0;handler<256;handler++)for(unsigned index=0;index<256;index++)for(unsigned unit=0;unit<256;unit+=17)for(unsigned len=0;len<65536;len+=8191){*(uint32_t *)(source+360)=node;*(uint8_t *)(node+4)=handler;*(uint8_t *)(packet+7)=index;*(uint8_t *)(packet+6)=unit;*(uint16_t *)(packet+4)=len;*(uint32_t *)0x805cd4=0x123456;*(uint8_t *)0x8056e4=91;removed=0;expected=packet;expectedhandler=handler;assert(opencfw_em9305_radio_packet_advance_32d738(source)==1);unsigned take=handler==255||unit*(index+1)>=len;if(take){assert(removed==1&&*(uint32_t *)0x805cd4==0xabcdef&&*(uint8_t *)(packet+7)==index);}else{assert(removed==0&&*(uint8_t *)(packet+7)==(uint8_t)(index+1)&&*(uint32_t *)0x805cd4==0x123456&&*(uint8_t *)0x8056e4==91);}cases++;}
printf("PASS %u\n",cases);}
