#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned clears,mutate;static uint32_t version;static uintptr_t selected;
static void *opencfw_em9305_memset(void *p,uint32_t value,uint32_t n){if(value)abort();clears++;memset(p,value,n);if(n==784){if((uintptr_t)p!=selected)abort();*(uint8_t*)0x805004=version;}else if(n==584){if((uintptr_t)p!=0x808000)abort();if(mutate){*(uint32_t*)(selected+780)=0x809000;*(uint32_t*)0x805cec=1234;}}else abort();return p;}
#include "init-secondary-allocator-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;uint32_t versions[]={0,12,13,255};
for(unsigned freeindex=0;freeindex<7;freeindex++)for(unsigned v=0;v<4;v++)for(unsigned extra=0;extra<2;extra++)for(mutate=0;mutate<2;mutate++){
memset((void*)0x800000,0,0x10000);version=versions[v];clears=0;selected=0x803d78+freeindex*784;for(unsigned i=0;i<6;i++){*(uint8_t*)(uintptr_t)(0x803d78+i*784)=i<freeindex;*(uint32_t*)(uintptr_t)(0x803d58+i*4)=100+i;*(uint32_t*)(uintptr_t)(0x805c44+i*4)=extra?0x808000:0;}
*(uint32_t*)0x805cac=0x805000;*(uint8_t*)0x805004=99;*(uint8_t*)0x805b18=9;*(uint8_t*)0x805aca=23;*(uint32_t*)0x805cec=4321;
uint32_t result=opencfw_em9305_init_secondary_allocate_316e74();if(freeindex==6){if(result||clears)abort();}else{if(result!=selected||clears!=(1u+(extra&&version>=13))||*(uint8_t*)selected!=1||*(uint16_t*)(selected+108)!=257||*(uint8_t*)(selected+712)!=9||*(uint16_t*)(selected+706)!=1037||*(uint16_t*)(selected+704)!=freeindex||*(uint8_t*)(selected+776)!=23||*(uint32_t*)(selected+40)!=100+freeindex||*(uint16_t*)(selected+600)||*(uint8_t*)(selected+602))abort();for(unsigned j=0;j<15;j++)if(*(uint16_t*)(selected+280+j*2)!=4095)abort();if(extra&&version>=13){uintptr_t e=mutate?0x809000:0x808000;if(*(uint32_t*)(selected+780)!=e||*(uint8_t*)(e+96)!=1||*(uint32_t*)(e+92)!=(mutate?1234u:4321u))abort();}}
cases++;
}
printf("PASS %u isolated secondary allocator cases\n",cases);return 0;}
