#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include "init-channel-selector-prepared.c"
static uint16_t reverse_bytes(uint16_t value){uint16_t out=0;for(unsigned byte=0;byte<2;byte++)for(unsigned bit=0;bit<8;bit++)out|=((value>>(byte*8+bit))&1u)<<(byte*8+7-bit);return out;}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;uintptr_t record=0x804000;
 uint16_t seeds[]={0,1,0x1234,65535};for(unsigned s=0;s<4;s++)for(unsigned input=0;input<65536;input++){
 uint16_t seed=seeds[s],value=(uint16_t)input^seed;for(unsigned i=0;i<3;i++)value=(uint16_t)(reverse_bytes(value)*17u+seed);value^=seed;unsigned channel=value%37u;
 *(uint16_t*)(record+262)=input;*(uint16_t*)(record+322)=seed;*(uint32_t*)(record+276)=0xffffffff;*(uint32_t*)(record+280)=0xffffffff;
 if(opencfw_em9305_init_callback_325898(record)!=channel)abort();
 cases++;
 *(uint32_t*)(record+276)=0;*(uint32_t*)(record+280)=0;*(uint8_t*)(record+272)=37;for(unsigned i=0;i<37;i++)*(uint8_t*)(record+284+i)=(uint8_t)(36-i);/* list excludes seed halfword at322 */
 unsigned index=37u*value/65536u;if(opencfw_em9305_init_callback_325898(record)!=36-index)abort();
 cases++;
 }
 for(unsigned feature=0;feature<256;feature++){*(uint32_t*)0x805cac=0x804000;*(uint8_t*)0x804004=feature;*(uint32_t*)0x805b30=0xabcdef;
 uint32_t r=opencfw_em9305_init_lower_306ab4(0xdeadbeefu);if(r!=(feature<9?feature:0x805b30u)||*(uint32_t*)0x805b30!=(0xabcdefu|(feature<9?0u:1u<<14))||*(uint32_t*)0x8027e4!=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_325898)abort();
 cases++;}
 printf("PASS %u isolated canonical channel-selector cases\n",cases);return 0;}
