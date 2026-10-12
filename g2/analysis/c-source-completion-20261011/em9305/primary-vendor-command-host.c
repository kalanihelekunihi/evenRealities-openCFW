#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
static uint32_t caparg,qarg;
uint32_t opencfw_em9305_rom_allocator_capacity_1030e8(uint32_t a){caparg=a;return a+0x12345u;}
static uint32_t opencfw_em9305_controller_allocator_query(uint32_t a){qarg=a;return a^0x87654321u;}
static uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t p){uint64_t a=0;for(unsigned i=0;i<8;i++)a|=(uint64_t)*(volatile uint8_t*)(p+i)<<(i*8);return a;}
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,uint32_t low,uint32_t high)
{
 *(volatile uint8_t *)(output+4u)=(uint8_t)high;
 *(volatile uint8_t *)output=(uint8_t)low;
 *(volatile uint8_t *)(output+5u)=(uint8_t)(high>>8u);
 *(volatile uint8_t *)(output+3u)=(uint8_t)(low>>24u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)(low>>16u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)(low>>8u);
 return output;
}

#include "primary-vendor-command-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned vectors=0;
for(uint32_t v=0;v<65536u;v++){
 if(opencfw_em9305_vendor_command_30cd5c(v)!=0x805bec||*(uint8_t*)0x805bec!=(v!=0)||opencfw_em9305_vendor_command_30db24(v)!=(v!=0)||*(uint8_t*)0x805bee!=(v!=0)||opencfw_em9305_vendor_command_30e034(v)||*(uint32_t*)0x8059a0!=v)abort();
 vectors++;
 uint8_t input[8];uint32_t low=v*0x10203u,high=v;for(unsigned i=0;i<4;i++){input[i]=low>>(i*8);input[i+4]=high>>(i*8);}*(uint32_t*)0x805a94=0xabc;*(uint32_t*)0x805a98=0xdef;
 uint32_t r=opencfw_em9305_vendor_command_30d87c((uintptr_t)input);if(r!=(high>=0x2000?18u:0u)||*(uint32_t*)0x805a94!=(high>=0x2000?0xabcu:low)||*(uint32_t*)0x805a98!=(high>=0x2000?0xdefu:high))abort();
 vectors++;
 uint32_t c=opencfw_em9305_vendor_allocator_second_313fa8(v);if(caparg!=v||qarg!=v+0x12345||c!=(v+0x12345)-((v+0x12345)^0x87654321))abort();
 vectors++;
 for(unsigned mode=0;mode<3;mode++){uint32_t l=mode==0?v:mode==1?(1u<<(v%32)):0,h=mode==2?(1u<<(v%32)):0;for(unsigned enable=0;enable<2;enable++){
 uint32_t ol=0x12345678,oh=0x89abcdef;*(uint32_t*)0x805a84=ol;*(uint32_t*)0x805a88=oh;unsigned reject=((l&0xc0010000)|(h&0x1ffffff))!=0;r=opencfw_em9305_vendor_command_30d9b4(l,h,enable);if(r!=(reject?18u:0u)||*(uint32_t*)0x805a84!=(reject?ol:enable?ol|l:ol&~l)||*(uint32_t*)0x805a88!=(reject?oh:enable?oh|h:oh&~h))abort();
 vectors++;}}
}
for(unsigned active=0;active<256;active++){uint8_t output[8];for(unsigned i=0;i<8;i++)output[i]=0xa5;*(uint8_t*)0x805a81=active;*(uint32_t*)0x805a8c=0x12345678;*(uint32_t*)0x805a90=0x89abcdef;uint32_t r=opencfw_em9305_vendor_command_30be48((uintptr_t)output);uint8_t expected[8]={0x78,0x56,0x34,0x12,0xef,0xcd,0xa5,0xa5};if(r!=(active?0u:18u))abort();for(unsigned i=0;i<8;i++)if(output[i]!=(active?expected[i]:0xa5))abort();
 vectors++;}
printf("PASS %u vendor provider projections; actual pack/serializer C, ROM contracts controlled\n",vectors);return 0;}
