#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
/* Native332f80..332fa8: combined PHY2/PHY4 capability guard; full-width args retained. */
uint32_t opencfw_em9305_config_phy_pair_valid_332f80(uint32_t first,uint32_t second)
{
 uint32_t capability=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t combined=first|second;
 if((capability&256u)==0u&&(combined&2u)!=0u)return 0u;
 if((capability&2048u)==0u&&(combined&4u)!=0u)return 0u;
 return 1u;
}

int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
 for(unsigned cap=0;cap<4;++cap)for(unsigned a=0;a<256;++a)for(unsigned bv=0;bv<256;++bv){*(uint32_t*)0x805a94=((cap&1)?256:0)|((cap&2)?2048:0);unsigned want=(((a|bv)&2)==0||(cap&1))&&(((a|bv)&4)==0||(cap&2));if(opencfw_em9305_config_phy_pair_valid_332f80(a,bv)!=want)return 3;++cases;}
 printf("PASS %u\n",cases);return 0;}
