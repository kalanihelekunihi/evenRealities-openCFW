#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t b){return (uint16_t)a*(uint16_t)b;}
/* Native ROM3357e0/335800: eight exact paired words, reader333bec
 * establishes extent through lp_count8. Source/table SHA in evidence receipt. */
static const uint32_t opencfw_em9305_primary_timer_thresholds[8]={2000000u,1000000u,500000u,160000u,80000u,40000u,5000u,0u};
static const uint32_t opencfw_em9305_primary_timer_quanta[8]={1000000u,100000u,50000u,10000u,5000u,2500u,1250u,625u};
/* Native333bec..333c20: strict unsigned threshold, first hit, no-hit R0 unchanged. */
uint32_t opencfw_em9305_radio_primary_timer_333bec(uint32_t value)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805f34u!=0u)return value;
 *(volatile uint32_t *)(uintptr_t)0x805f30u=value;
 for(uint32_t i=0u;i<8u;i++){
  if(opencfw_em9305_primary_timer_thresholds[i]<value){
   uint32_t quantum=opencfw_em9305_primary_timer_quanta[i];
   *(volatile uint32_t *)(uintptr_t)0x805f2cu=quantum;
   return quantum;
  }
 }
 return value;
}
/* Native313744..31375c: authentic 16x16 unsigned DSP multiply, flag clear
 * in call delay slot, flag publish after child; R0 is child result. */
uint32_t opencfw_em9305_radio_primary_value_313744(uint32_t value)
{
 uint32_t scaled=opencfw_em9305_config_limit_mpyuw(value,1250u);
 *(volatile uint8_t *)(uintptr_t)0x805f34u=0u;
 uint32_t result=opencfw_em9305_radio_primary_timer_333bec(scaled);
 *(volatile uint8_t *)(uintptr_t)0x805f34u=1u;
 return result;
}
static unsigned reference(uint32_t v){if(v>2000000)return 1000000;if(v>1000000)return 100000;if(v>500000)return 50000;if(v>160000)return 10000;if(v>80000)return 5000;if(v>40000)return 2500;if(v>5000)return 1250;if(v>0)return 625;return 0;}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned n=0;uint32_t bounds[]={0,1,4999,5000,5001,39999,40000,40001,79999,80000,80001,159999,160000,160001,499999,500000,500001,999999,1000000,1000001,1999999,2000000,2000001,0xffffffff};for(unsigned g=0;g<256;g++)for(unsigned i=0;i<24;i++){uint32_t v=bounds[i];*(uint8_t*)0x805f34=g;*(uint32_t*)0x805f30=0x1234;*(uint32_t*)0x805f2c=0x5678;uint32_t got=opencfw_em9305_radio_primary_timer_333bec(v);if(got!=(g?v:reference(v))||*(uint32_t*)0x805f30!=(g?0x1234:v)||*(uint32_t*)0x805f2c!=(g||!v?0x5678:reference(v)))abort();n++;}for(unsigned v=0;v<65536;v++){*(uint8_t*)0x805f34=255;*(uint32_t*)0x805f2c=0x5678;unsigned scaled=v*1250;if(opencfw_em9305_radio_primary_value_313744(v)!=reference(scaled)||*(uint8_t*)0x805f34!=1||*(uint32_t*)0x805f30!=scaled||*(uint32_t*)0x805f2c!=(scaled?reference(scaled):0x5678))abort();n++;}printf("PASS %u timer fixtures\n",n);}
