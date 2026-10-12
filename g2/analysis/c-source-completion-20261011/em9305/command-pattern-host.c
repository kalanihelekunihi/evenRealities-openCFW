#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
/* Native pattern332b94..332be4 and PN9 loop332c50..332c84.
 * STB.AB writes selector at old+2 before advancing payload address+2. */
uintptr_t opencfw_em9305_command_pn9_332c50(uintptr_t output,uint32_t length)
{
 if(length==0u)return output;
 uint32_t count=(uint8_t)(length-1u)+1u,seed=511u;
 do {
  *(volatile uint8_t *)output=(uint8_t)seed;
  output++;
  for(uint32_t bit=0u;bit<8u;bit++){
   uint32_t feedback=((seed>>4u)^seed)<<8u;
   seed=(feedback&256u)|(seed>>1u);
  }
 }while(--count!=0u);
 return output;
}
uint32_t opencfw_em9305_command_pattern_332b94(uint32_t length,uint32_t selector,uintptr_t output)
{
 *(volatile uint8_t *)(output+1u)=(uint8_t)length;
 *(volatile uint8_t *)(output+2u)=(uint8_t)selector;
 output+=2u;
 if(selector>=8u||selector==3u)return length;
 if(selector==0u)return (uint32_t)opencfw_em9305_command_pn9_332c50(output,length);
 uint32_t value;
 switch(selector){
 case 1u:value=15u;break;
 case 2u:value=85u;break;
 case 4u:value=255u;break;
 case 5u:value=0u;break;
 case 6u:value=240u;break;
 default:value=170u;break;
 }
 return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)output,value,length);
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);static const uint8_t pn[]={0xff,0xc1,0xfb,0xe8,0x4c,0x90,0x72,0x8b,0xe7,0xb3,0x51,0x89,0x63,0xab,0x23,0x23};unsigned cases=0;uint8_t *p=(void *)0x840000;
for(unsigned n=0;n<256;n++)for(unsigned selector=0;selector<10;selector++){memset(p,0xa5,300);unsigned result=opencfw_em9305_command_pattern_332b94(n,selector,(uintptr_t)p);assert(p[0]==0xa5&&p[1]==n&&p[n+3]==0xa5);if(selector>=8||selector==3){assert(result==n&&p[2]==selector&&p[3]==0xa5);}else if(selector==0){assert(result==0x840002+n);if(!n)assert(p[2]==0);else assert(memcmp(p+2,pn,n<sizeof pn?n:sizeof pn)==0);}else{unsigned v=selector==1?15:selector==2?85:selector==4?255:selector==5?0:selector==6?240:170;assert(result==0x840002);for(unsigned j=0;j<n;j++)assert(p[j+2]==v);if(!n)assert(p[2]==selector);}cases++;}
assert(opencfw_em9305_command_pn9_332c50((uintptr_t)p,256)==0x840100);assert(opencfw_em9305_command_pn9_332c50((uintptr_t)p,257)==0x840001);cases+=2;printf("PASS %u\n",cases);}
