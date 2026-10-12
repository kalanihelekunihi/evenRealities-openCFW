#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned raw,n;static char trace[8];static uintptr_t source=0x860000,packet=0x840008;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==(raw?packet:0x830008));assert(*(uint32_t *)0x805cd4==packet);mark('F');*(uint8_t *)0x805b18=23;return 11;}
uint32_t opencfw_em9305_wsf_queue_append(uintptr_t q,uintptr_t p){assert(q==0x8056dc&&p==packet-12);mark('Q');return 12;}
uint32_t opencfw_em9305_wsf_critical_enter(void){mark('E');return 0;}
uint32_t opencfw_em9305_wsf_critical_exit(void){mark('X');*(uint8_t *)(source+376)=255;return 0;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t flags){assert(handler==23&&flags==1&&*(uint32_t *)0x805cd4==0);mark('P');return 0x76543210;}
/* Authenticated packet completion 32d790..32d7f4. The event-post call's
 * delay slot clears the saved packet before the child executes. */
uint32_t opencfw_em9305_radio_packet_complete_32d790(uintptr_t source)
{
 uintptr_t packet=*(volatile uint32_t *)(uintptr_t)0x805cd4u;
 if(packet==0u)return (uint32_t)source;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x8056e4u;
 if(handler!=255u){
  uintptr_t payload=*(volatile uint32_t *)packet;
  (void)opencfw_em9305_wsf_event_release(payload);
  (void)opencfw_em9305_wsf_queue_append(0x8056dcu,packet-12u);
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805ab4u;
  *(volatile uint8_t *)(uintptr_t)0x805ab4u=(uint8_t)(count+1u);
  (void)opencfw_em9305_wsf_critical_exit();
  count=*(volatile uint8_t *)(source+376u);
  *(volatile uint8_t *)(source+376u)=(uint8_t)(count+1u);
 }else (void)opencfw_em9305_wsf_event_release(packet);
 handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint32_t *)(uintptr_t)0x805cd4u=0u;
 return opencfw_em9305_wsf_event_post(handler,1u);
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;assert(opencfw_em9305_radio_packet_complete_32d790(source)==source&&n==0);cases++;
for(raw=0;raw<2;raw++){for(unsigned count=0;count<256;count++){memset(trace,0,sizeof(trace));n=0;*(uint32_t *)0x805cd4=packet;*(uint8_t *)0x8056e4=raw?255:19;*(uint32_t *)packet=0x830008;*(uint8_t *)0x805ab4=count;*(uint8_t *)(source+376)=17;*(uint8_t *)0x805b18=22;assert(opencfw_em9305_radio_packet_complete_32d790(source)==0x76543210);assert(strcmp(trace,raw?"FP":"FQEXP")==0);assert(*(uint8_t *)0x805ab4==(raw?count:(uint8_t)(count+1)));assert(*(uint8_t *)(source+376)==(raw?17:0));cases++;}}printf("PASS %u\n",cases);}
