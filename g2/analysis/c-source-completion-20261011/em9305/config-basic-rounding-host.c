#include <stdint.h>
#include <stdio.h>
static uint32_t opencfw_em9305_config_limit_divu(uint32_t a,uint32_t b){return b?a/b:1u;}
static uint32_t opencfw_em9305_config_update_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static inline uint32_t opencfw_em9305_config_round_mpyw(uint32_t a,uint32_t b)
{return (uint32_t)((int32_t)(int16_t)a*(int32_t)(int16_t)b);}
static inline uint32_t opencfw_em9305_config_round_mpyuw(uint32_t a,uint32_t b)
{return (a&65535u)*(b&65535u);}
/* Native317efc..317f2c: byte-wrapped numerator/divisor and ceiling quotient. */
uint32_t opencfw_em9305_config_basic_rounding_317efc(uint32_t first,uint32_t second,uint32_t third)
{
 uint32_t product=opencfw_em9305_config_round_mpyw(third-1u,first);
 uint32_t numerator=opencfw_em9305_config_round_mpyuw(first,second+1u)&255u;
 uint32_t divisor=(product&255u)+1u;
 uint32_t raw_divisor=divisor;
 if((divisor&255u)!=divisor)divisor=1u;
 divisor&=255u;
 uint32_t quotient=opencfw_em9305_config_limit_divu(numerator,divisor);
 uint32_t reproduced=quotient;
 if(raw_divisor==divisor)reproduced=opencfw_em9305_config_update_mpywhl(quotient,raw_divisor);
 reproduced&=255u;
 return (quotient+(numerator!=reproduced))&255u;
}

int main(void){unsigned cases=0;for(unsigned a=0;a<256;++a)for(unsigned b=0;b<256;++b)for(unsigned c=0;c<256;++c){unsigned raw=((a*(c-1))&255)+1,den=raw==256?1:raw,num=(a*(b+1))&255;unsigned expected=(num+den-1)/den;if(opencfw_em9305_config_basic_rounding_317efc(a,b,c)!=expected)return 3;++cases;}uint32_t values[]={0,255,256,65535,65536,0x80000000u,0xffffffffu};for(unsigned x=0;x<7;++x)for(unsigned y=0;y<7;++y)for(unsigned z=0;z<7;++z){uint32_t a=values[x],b=values[y],c=values[z],raw=((a*(c-1))&255)+1,den=raw==256?1:raw,num=(a*(b+1))&255;if(opencfw_em9305_config_basic_rounding_317efc(a,b,c)!=(num+den-1)/den)return 4;++cases;}printf("PASS %u\n",cases);}
