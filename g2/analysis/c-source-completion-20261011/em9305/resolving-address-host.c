#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned childmatch,calls,mutate;
uint32_t opencfw_em9305_radio_key_match_315640(uintptr_t row,uint32_t low,uint32_t high){assert(row>=0x810000&&row<0x8100d8&&low==100&&high==200);calls++;if(mutate){*(uint8_t *)0x801610=0;*(uint32_t *)0x805c00=0x840000;*(uint32_t *)(row+32)=999;}return childmatch;}
/* Authenticated resolving address lookup303bdc..303c9c. Table base
 * refreshes per row; count refreshes after key match child; captured row
 * survives that child even if the global table changes. */
extern uint32_t opencfw_em9305_radio_key_match_315640(uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_radio_resolve_303bdc(uint32_t low,uint32_t high,uintptr_t kind_cell,uintptr_t output)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x801610u;
 for(uint32_t index=0u;index<count;index++){
  uintptr_t table=*(volatile uint32_t *)(uintptr_t)0x805c00u;
  uintptr_t row=table+index*72u;
  uint32_t disabled=*(volatile uint8_t *)(row+64u);
  if(disabled!=0u)continue;
  uint32_t stored_high=*(volatile uint32_t *)(row+44u);
  uint32_t stored_low=*(volatile uint32_t *)(row+40u);
  uint32_t matched=((stored_high^high)|(stored_low^low))==0u;
  if(matched==0u){
   matched=opencfw_em9305_radio_key_match_315640(row,low,high)!=0u;
   count=*(volatile uint8_t *)(uintptr_t)0x801610u;
   if(matched!=0u){
    *(volatile uint32_t *)(row+40u)=low;
    *(volatile uint32_t *)(row+44u)=high;
    *(volatile uint8_t *)(row+66u)=0u;
   }
  }
  if(matched!=0u){
   uint32_t kind=*(volatile uint8_t *)(row+38u)&1u;
   *(volatile uint8_t *)kind_cell=(uint8_t)kind;
   uint32_t translated_high=*(volatile uint16_t *)(row+36u);
   uint32_t translated_low=*(volatile uint32_t *)(row+32u);
   *(volatile uint32_t *)(output+4u)=translated_high;
   *(volatile uint32_t *)output=translated_low;
   return 1u;
  }
 }
 uint32_t slot=*(volatile uint8_t *)(uintptr_t)0x801638u;
 uintptr_t record=0x801618u+slot*8u;
 uint32_t next=(slot+1u)&3u;
 *(volatile uint32_t *)(record+4u)=high;
 *(volatile uint32_t *)record=low;
 *(volatile uint8_t *)(uintptr_t)0x801638u=(uint8_t)next;
 return 0u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned count=0;count<4;count++)for(unsigned disabled=0;disabled<8;disabled++)for(unsigned direct=0;direct<4;direct++)for(childmatch=0;childmatch<2;childmatch++)for(unsigned slot=0;slot<4;slot++){memset((void *)0x800000,0,0x100000);calls=mutate=0;*(uint8_t *)0x801610=count;*(uint32_t *)0x805c00=0x810000;*(uint8_t *)0x801638=slot;*(uint8_t *)0x820000=7;*(uint32_t *)0x821000=300;unsigned found=99,expectedcalls=0;for(unsigned i=0;i<3;i++){uintptr_t row=0x810000+i*72;*(uint8_t *)(row+64)=(disabled>>i)&1;*(uint32_t *)(row+40)=direct==i?100:101;*(uint32_t *)(row+44)=200;*(uint32_t *)(row+32)=500+i;*(uint16_t *)(row+36)=600+i;*(uint8_t *)(row+38)=i+2;*(uint8_t *)(row+66)=9;if(i<count&&!((disabled>>i)&1)&&found==99){if(direct!=i)expectedcalls++;if(direct==i||childmatch)found=i;}}unsigned r=opencfw_em9305_radio_resolve_303bdc(100,200,0x820000,0x821000);assert(r==(found!=99)&&calls==expectedcalls);if(found!=99){uintptr_t row=0x810000+found*72;assert(*(uint8_t *)0x820000==((found+2)&1)&&*(uint32_t *)0x821000==500+found&&*(uint32_t *)0x821004==600+found&&*(uint8_t *)0x801638==slot);assert(*(uint8_t *)(row+66)==(direct==found?9:0));}else{uintptr_t rec=0x801618+slot*8;assert(*(uint32_t *)rec==100&&*(uint32_t *)(rec+4)==200&&*(uint8_t *)0x801638==((slot+1)&3)&&*(uint8_t *)0x820000==7&&*(uint32_t *)0x821000==300);}cases++;}
for(childmatch=0;childmatch<2;childmatch++){memset((void *)0x800000,0,0x100000);calls=0;mutate=1;*(uint8_t *)0x801610=3;*(uint32_t *)0x805c00=0x810000;*(uint32_t *)0x810028=101;*(uint32_t *)0x81002c=200;*(uint16_t *)0x810024=55;assert(opencfw_em9305_radio_resolve_303bdc(100,200,0x820000,0x821000)==childmatch&&calls==1);if(childmatch)assert(*(uint32_t *)0x821000==999&&*(uint32_t *)0x821004==55&&*(uint32_t *)0x810028==100);cases++;}printf("PASS %u\n",cases);}
