#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
/* Native307fa0..307fcc: id<=5 byte stride and genuine wide-accumulator multiply. */
uint32_t opencfw_em9305_command_pair_apply_307fa0(uint32_t id,uint32_t value)
{
 if(id>=6u)return 0u;
 uint32_t offset=id*784u; /* bounded id makes native MPYUW stride exact */
 uintptr_t row=0x803e74u+offset;
 uint32_t factor=*(volatile uint32_t *)row;
 *(volatile uint16_t *)(uintptr_t)(0x803fe0u+offset)=(uint16_t)value;
 uint32_t product;
 product=(uint32_t)((uint64_t)factor*(uint16_t)value); /* Host-only manual-backed arithmetic normalization, no accumulator proof. */
 *(volatile uint32_t *)(row+8u)=product;
 return 1u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uint32_t seed=0x12345678;
for(unsigned id=0;id<6;id++)for(unsigned j=0;j<10000;j++){seed=seed*1664525+1013904223;uint32_t factor=seed;seed=seed*1664525+1013904223;uint32_t value=seed;uintptr_t row=0x803e74+id*784,half=0x803fe0+id*784;*(uint32_t *)row=factor;*(uint32_t *)(row+8)=0xa5a5a5a5;*(uint32_t *)half=0xa5a5a5a5;assert(opencfw_em9305_command_pair_apply_307fa0(id,value)==1);uint64_t expected=(uint64_t)factor*(value&65535);assert(*(uint32_t *)row==factor&&*(uint32_t *)(row+8)==(uint32_t)expected&&*(uint16_t *)half==(value&65535)&&*(uint16_t *)(half+2)==0xa5a5);cases++;}
for(unsigned id=6;id<65536;id++){assert(opencfw_em9305_command_pair_apply_307fa0(id,0xffffffff)==0);cases++;}assert(opencfw_em9305_command_pair_apply_307fa0(0xffffffff,0)==0);cases++;printf("PASS %u\n",cases);}
