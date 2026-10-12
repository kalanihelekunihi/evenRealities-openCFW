#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned clearcount,mutate;
static void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){clearcount++;if(n==5&&*(uint16_t*)0x805ab6!=27)abort();if(mutate)*(uint32_t*)0x805cac=0x806100;return memset(p,v,n);}
#include "radio-init-state-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned vectors=0;
for(unsigned v=0;v<65536;v++){*(uint32_t*)0x805cac=0x806000;*(uint8_t*)0x806023=v;*(uint8_t*)0x806024=v>>8;memset((void*)0x805ab4,0xa5,40);clearcount=0;uint32_t r=opencfw_em9305_init_lower_30e42c(v);uint8_t expected[40]={0};expected[0]=v;expected[1]=v>>8;expected[2]=27;expected[4]=0x48;expected[5]=1;expected[20]=3;expected[26]=10;expected[28]=1;expected[30]=1;expected[36]=0x80;expected[37]=12;if(r!=0x10001||clearcount!=2||memcmp((void*)0x805ab4,expected,40))abort();vectors++;
*(uint16_t*)0x80602a=v;memset((void*)0x805adc,0xa5,28);clearcount=0;r=opencfw_em9305_init_lower_30e538(v);uint8_t ex[28]={0};ex[0]=v;ex[1]=v>>8;ex[20]=3;ex[24]=0xa0;ex[25]=31;if(r!=v||clearcount!=1||memcmp((void*)0x805adc,ex,28))abort();vectors++;
}
for(unsigned v=0;v<256;v++){memset((void*)0x805af8,v,20);uint8_t ex[20]={0x10,0,0x10,0,0,0,0,0,7};if(opencfw_em9305_init_lower_30e564(v)!=0x805af8||memcmp((void*)0x805af8,ex,20))abort();vectors++;memset((void*)0x805b58,v,8);if(opencfw_em9305_init_lower_30e580(v)!=0x805b58||*(uint32_t*)0x805b58!=900||*(uint8_t*)0x805b5c||*(uint8_t*)0x805b5d!=v)abort();vectors++;memset((void*)0x805b80,v,4);if(opencfw_em9305_init_lower_30e594(v)!=0x805b80||*(uint16_t*)0x805b80||*(uint8_t*)0x805b82||*(uint8_t*)0x805b83!=v)abort();vectors++;}
mutate=1;*(uint32_t*)0x805cac=0x806000;*(uint16_t*)0x80612a=0x6789;if(opencfw_em9305_init_lower_30e538(0)!=0x6789)abort();vectors++;*(uint32_t*)0x805cac=0x806000;*(uint8_t*)0x806123=0x12;*(uint8_t*)0x806124=0x34;if(opencfw_em9305_init_lower_30e42c(0)!=0x10001||*(uint16_t*)0x805ab4!=0x3412)abort();vectors++;printf("PASS %u source state projections including post-clear config reload; no native/hardware claim\n",vectors);return 0;}
