#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned callbacks;
static uint32_t cb(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f){assert(a==100&&b==200&&c==1&&d==7&&e==300&&f==400);callbacks++;return 999;}
/* Authenticated address-resolution lookup303890..30390c. Callback is
 * optional after an eligible nonmatching row, and its return is ignored. */
uint32_t opencfw_em9305_radio_resolve_303890(uint32_t low,uint32_t high,uintptr_t kind_cell,uintptr_t output)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x801610u;
 uint32_t eligible=0u;
 if(count!=0u){
  uintptr_t table=*(volatile uint32_t *)(uintptr_t)0x805c00u;
  for(uint32_t index=0u;index<count;index++){
   uintptr_t row=table+index*72u;
   uint32_t disabled=*(volatile uint8_t *)(row+64u);
   if(disabled==0u){
    uint32_t stored_high=*(volatile uint32_t *)(row+44u);
    uint32_t stored_low=*(volatile uint32_t *)(row+40u);
    eligible=1u;
    if(((stored_high^high)|(stored_low^low))==0u){
     uint32_t kind=*(volatile uint8_t *)(row+38u)&1u;
     *(volatile uint8_t *)kind_cell=(uint8_t)kind;
     uint32_t translated_high=*(volatile uint16_t *)(row+36u);
     uint32_t translated_low=*(volatile uint32_t *)(row+32u);
     *(volatile uint32_t *)(output+4u)=translated_high;
     *(volatile uint32_t *)output=translated_low;
     return 1u;
    }
   }
  }
 }
 if(eligible!=0u){
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x80160cu;
  if(callback!=0u){
   uint32_t translated_high=*(volatile uint32_t *)(output+4u);
   uint32_t translated_low=*(volatile uint32_t *)output;
   uint32_t kind=*(volatile uint8_t *)kind_cell;
   (void)((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)
      (low,high,1u,kind,translated_low,translated_high);
  }
 }
 return 0u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned count=0;count<4;count++)for(unsigned disabled=0;disabled<8;disabled++)for(unsigned match=0;match<4;match++)for(unsigned present=0;present<2;present++){memset((void *)0x800000,0,0x100000);callbacks=0;*(uint8_t *)0x801610=count;*(uint32_t *)0x805c00=0x810000;*(uint32_t *)0x80160c=present?(uint32_t)(uintptr_t)cb:0;*(uint8_t *)0x820000=7;*(uint32_t *)0x821000=300;*(uint32_t *)0x821004=400;unsigned found=99,eligible=0;for(unsigned i=0;i<3;i++){uintptr_t row=0x810000+i*72;*(uint8_t *)(row+64)=(disabled>>i)&1;*(uint32_t *)(row+40)=match==i?100:101;*(uint32_t *)(row+44)=200;*(uint32_t *)(row+32)=500+i;*(uint16_t *)(row+36)=600+i;*(uint8_t *)(row+38)=i+2;if(i<count&&!((disabled>>i)&1)){eligible=1;if(match==i)found=i;}}unsigned r=opencfw_em9305_radio_resolve_303890(100,200,0x820000,0x821000);assert(r==(found!=99));if(found!=99){assert(!callbacks&&*(uint8_t *)0x820000==((found+2)&1)&&*(uint32_t *)0x821000==500+found&&*(uint32_t *)0x821004==600+found);}else{assert(callbacks==(eligible&&present)&&*(uint8_t *)0x820000==7&&*(uint32_t *)0x821000==300&&*(uint32_t *)0x821004==400);}cases++;}
memset((void *)0x800000,0,0x100000);*(uint8_t *)0x801610=1;*(uint32_t *)0x805c00=0x810000;*(uint32_t *)0x810028=100;*(uint32_t *)0x81002c=200;*(uint32_t *)0x810020=0xaabbccdd;*(uint16_t *)0x810024=88;*(uint8_t *)0x810026=1;assert(opencfw_em9305_radio_resolve_303890(100,200,0x810020,0x821000)==1&&*(uint32_t *)0x821000==0xaabbcc01&&*(uint32_t *)0x821004==88);cases++;printf("PASS %u\n",cases);}
