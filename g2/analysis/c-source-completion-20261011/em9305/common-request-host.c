#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned calls,mutate;
static uint32_t opencfw_em9305_auxiliary_select_314d94(uint32_t index){calls++;if(mutate)*(uint32_t *)(uintptr_t)(0x801658+index*24)=99;*(uint8_t *)0x8016bd=1;return index;}
/* Native request30455c..304588, pure no-op30fd2c and exact scaled count. */
uint32_t opencfw_em9305_pal_request_noop_30fd2c(uint32_t incoming)
{return incoming;}
uint32_t opencfw_em9305_common_request_30455c(uint32_t index)
{
 uint32_t selected=*(volatile uint8_t *)(uintptr_t)0x8016bdu;
 if(selected==0u){
  (void)opencfw_em9305_pal_request_noop_30fd2c(index);
  (void)opencfw_em9305_auxiliary_select_314d94(index);
 }
 uint32_t offset;
 offset=index*24u;
 uintptr_t slot=0x801658u+offset;
 uint32_t count=*(volatile uint32_t *)slot;
 *(volatile uint32_t *)slot=count+1u;
 return (uint32_t)slot;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uint32_t values[]={0,1,0x7fffffff,0xffffffff};for(unsigned index=0;index<8;index++)for(unsigned selected=0;selected<3;selected++)for(unsigned ci=0;ci<4;ci++)for(mutate=0;mutate<2;mutate++){uintptr_t slot=0x801658+24*index;*(uint32_t *)slot=values[ci];*(uint8_t *)0x8016bd=selected;calls=0;uint32_t expected=selected==0&&mutate?100:values[ci]+1;assert(opencfw_em9305_common_request_30455c(index)==slot&&calls==(selected==0)&&*(uint32_t *)slot==expected);assert(opencfw_em9305_pal_request_noop_30fd2c(values[ci])==values[ci]);cases++;}
printf("PASS %u\n",cases);}
