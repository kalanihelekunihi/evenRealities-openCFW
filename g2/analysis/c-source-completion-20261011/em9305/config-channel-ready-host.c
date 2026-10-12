#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_auxiliary_guard_interval(void){uintptr_t p=*(volatile uint32_t*)(uintptr_t)0x805c18;return *(volatile uint16_t*)(p+6);}
static inline uint32_t opencfw_em9305_config_ready_mpyuw(uint32_t a)
{return (a&65535u)*1250u;}
/* Native3186a0..318708: captured policy overhead, preceding active channels and unsigned readiness. */
uint32_t opencfw_em9305_config_channel_ready_3186a0(uintptr_t channel)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t overhead=*(volatile uint16_t *)(config+50u);
 overhead+=opencfw_em9305_auxiliary_guard_interval();
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c64u;
 int32_t difference=(int32_t)((uint32_t)channel-(uint32_t)base);
 uint32_t index=(uint8_t)(difference/140);
 for(uint32_t i=0u;i<index;++i){
  if(*(volatile uint8_t *)(base+4u+i*140u)){
   uint32_t unused=*(volatile uint32_t *)(base+52u+i*140u);(void)unused;
   uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
   overhead+=guard;
   base=*(volatile uint32_t *)(uintptr_t)0x805c64u;
   overhead+=guard;
  }
 }
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uint32_t baseline=*(volatile uint32_t *)(channel+12u);
 uint32_t interval=*(volatile uint16_t *)(channel+20u);
 uint32_t required=guard+baseline;
 uint32_t available=opencfw_em9305_config_ready_mpyuw(interval)-overhead;
 return available>=required;
}

int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x813000;*(uint32_t*)0x805c18=0x814000;*(uint32_t*)0x805c64=0x820000;unsigned cases=0;unsigned indices[]={0,1,127,255};uint32_t baselines[]={0,1,0x7fffffffu,0xffffffffu};
for(unsigned ix=0;ix<4;++ix)for(unsigned pattern=0;pattern<3;++pattern){unsigned n=indices[ix],active=0;for(unsigned i=0;i<256;++i){unsigned on=pattern==0?0:pattern==1?1:i&1;*(uint8_t*)(uintptr_t)(0x820004+i*140)=on;if(i<n)active+=on;}uintptr_t channel=0x820000+n*140;*(uint16_t*)0x813032=12345;*(uint16_t*)0x814006=pattern?65535:0;
for(unsigned b=0;b<4;++b)for(unsigned interval=0;interval<65536;++interval){*(uint32_t*)(channel+12)=baselines[b];*(uint16_t*)(channel+20)=interval;uint32_t guard=pattern?65535:0;uint32_t threshold=12345+guard+2*active*guard;uint32_t expected=(uint32_t)(interval*1250-threshold)>=(uint32_t)(guard+baselines[b]);if(opencfw_em9305_config_channel_ready_3186a0(channel)!=expected)return 3;++cases;}}
printf("PASS %u\n",cases);}
