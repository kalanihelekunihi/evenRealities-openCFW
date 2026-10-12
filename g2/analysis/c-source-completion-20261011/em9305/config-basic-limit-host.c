#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
static inline uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t factor)
{return (a&65535u)*factor;}
static inline uint32_t opencfw_em9305_config_limit_divu(uint32_t a,uint32_t b)
{return b?a/b:1u;}
/* Native31855c..3185a8: full limit computation, full-width selector, unsigned quotient and low-byte return. */
uint32_t opencfw_em9305_config_basic_limit_31855c(uintptr_t link,uintptr_t input,uint32_t selector)
{
 uint32_t policy=*(volatile uint16_t *)(input+(selector?16u:18u));
 uint32_t interval=*(volatile uint16_t *)(link+500u);
 uint32_t budget=opencfw_em9305_config_limit_mpyuw(policy,1000u);
 uint32_t mode=*(volatile uint8_t *)(link+484u);
 uint32_t baseline=*(volatile uint32_t *)(link+20u);
 uint32_t period=opencfw_em9305_config_limit_mpyuw(interval,1250u);
 uint32_t time=*(volatile uint32_t *)(link+(selector?492u:496u));
 uint32_t value=budget-baseline;
 if(mode==1u)value-=time;else value+=time;
 uint32_t result=1u;
 if(value>=period)result=opencfw_em9305_config_limit_divu(value,period);
 return result&255u;
}

int main(void){if(mmap((void*)0x810000,0x4000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;uint32_t selectors[]={0,1,2,0xffffffffu},bases[]={0,0x80000000u,0xffffffffu};unsigned periods[]={0,1,65535};
for(unsigned v=0;v<65536;++v)for(unsigned k=0;k<4;++k)for(unsigned m=0;m<3;++m)for(unsigned b=0;b<3;++b)for(unsigned n=0;n<3;++n){*(uint16_t*)0x812010=v;*(uint16_t*)0x812012=65535-v;*(uint16_t*)0x8101f4=periods[n];*(uint8_t*)0x8101e4=m;*(uint32_t*)0x810014=bases[b];*(uint32_t*)0x8101ec=v*3971;*(uint32_t*)0x8101f0=~(v*811);uint32_t budget=(selectors[k]?v:65535-v)*1000;uint32_t time=selectors[k]?v*3971:~(v*811);uint32_t numerator=budget-bases[b];numerator=m==1?numerator-time:numerator+time;uint32_t denom=periods[n]*1250;uint32_t expected=numerator<denom?1:denom?numerator/denom:1;if(opencfw_em9305_config_basic_limit_31855c(0x810000,0x812000,selectors[k])!=(expected&255))return 3;++cases;}
printf("PASS %u\n",cases);}
