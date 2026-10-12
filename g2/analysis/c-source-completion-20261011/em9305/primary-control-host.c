#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
static unsigned calls,result;static uint32_t argument;
uint32_t opencfw_em9305_radio_primary_value_313744(uint32_t v){calls++;argument=v;return 77;}
uint32_t opencfw_em9305_radio_primary_pair_310664(int32_t a,int32_t b){if(a!=-123||b!=456)abort();return result;}
/* Native30d528..30d548: fullword input, wrapped halfword validation. */
extern uint32_t opencfw_em9305_radio_primary_value_313744(uint32_t);
uint32_t opencfw_em9305_command_primary_30d528(uint32_t value)
{
 if((uint16_t)(value-0x7df1u)<0x8211u)return 18u;
 (void)opencfw_em9305_radio_primary_value_313744(value);
 return 0u;
}
/* Native30e3ec..30e3fa: child zero/nonzero projected to18/0. */
extern uint32_t opencfw_em9305_radio_primary_pair_310664(int32_t,int32_t);
uint32_t opencfw_em9305_command_primary_30e3ec(int32_t first,int32_t second)
{
 return opencfw_em9305_radio_primary_pair_310664(first,second)==0u?18u:0u;
}
/* Native30d8a0..30d8f8, authenticated 3027c8 six-bit shift semantics.
 * Capability loaded before busy gate; fullword enable shifted unchanged. */
uint32_t opencfw_em9305_command_primary_30d8a0(uint32_t index,uint32_t enable)
{
 uint32_t shift=index&63u;
 uint64_t bit=UINT64_C(1)<<shift;
 uint32_t low=(uint32_t)bit,high=(uint32_t)(bit>>32u);
 uint32_t supported_high=*(volatile uint32_t *)(uintptr_t)0x805b54u;
 uint32_t supported_low=*(volatile uint32_t *)(uintptr_t)0x805b50u;
 if(((high&supported_high)|(low&supported_low))==0u)return 17u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a70u!=0u)return 12u;
 uint64_t value=(uint64_t)enable<<shift;
 uint32_t old_low=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t old_high=*(volatile uint32_t *)(uintptr_t)0x805a98u;
 low=(old_low&~low)|(uint32_t)value;
 high=(old_high&~high)|(uint32_t)(value>>32u);
 *(volatile uint32_t *)(uintptr_t)0x805a94u=low;
 *(volatile uint32_t *)(uintptr_t)0x805a98u=high;
 return 0u;
}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned n=0;for(unsigned i=0;i<65536;i++){calls=0;unsigned error=(uint16_t)(i-0x7df1)<0x8211?18:0;if(opencfw_em9305_command_primary_30d528(i)!=error||calls!=!error||(!error&&argument!=i))abort();n++;}for(result=0;result<256;result++){if(opencfw_em9305_command_primary_30e3ec(-123,456)!=(result?0:18))abort();n++;}unsigned enables[]={0,1,2,0xffffffff};for(unsigned idx=0;idx<256;idx++)for(unsigned sc=0;sc<4;sc++)for(unsigned busy=0;busy<2;busy++)for(unsigned e=0;e<4;e++){uint64_t supported=sc==0?0:sc==1?UINT64_C(0xffffffff):sc==2?UINT64_C(0xffffffff00000000):UINT64_MAX;*(uint32_t*)0x805b50=supported;*(uint32_t*)0x805b54=supported>>32;*(uint8_t*)0x805a70=busy;uint64_t old=UINT64_C(0xa5a5a5a55a5a5a5a);*(uint32_t*)0x805a94=old;*(uint32_t*)0x805a98=old>>32;uint64_t bit=UINT64_C(1)<<(idx&63);unsigned error=!(supported&bit)?17:busy?12:0;if(opencfw_em9305_command_primary_30d8a0(idx,enables[e])!=error)abort();uint64_t actual=*(uint32_t*)0x805a94|((uint64_t)*(uint32_t*)0x805a98<<32);uint64_t expect=error?old:(old&~bit)|((uint64_t)enables[e]<<(idx&63));if(actual!=expect)abort();n++;}printf("PASS %u control fixtures\n",n);}
