#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned row_present,keymatch,keycalls,callbacks;
uintptr_t opencfw_em9305_radio_identity_find_31441c(uint32_t k,uint32_t l,uint32_t h){assert(k==3&&l==300&&h==400);return row_present?0x830000:0;}
uint32_t opencfw_em9305_radio_key_match_315640(uintptr_t k,uint32_t l,uint32_t h){assert(k==0x830010&&l==100&&h==200);keycalls++;return keymatch;}
static uint32_t cb(uint32_t l,uint32_t h,uint32_t z,uint32_t k,uint32_t il,uint32_t ih){assert(l==100&&h==200&&z==0&&k==3&&il==300&&ih==400);callbacks++;return 999;}
/* Authenticated address projection303b7c and association303844.
 * Both preserve the stock zero return after recording/callback notification;
 * association's callback R4/R5 survive identity-find unchanged natively. */
uint32_t opencfw_em9305_radio_address_project_303b7c(uint32_t low,uint32_t high,uintptr_t kind_cell,uintptr_t identity)
{
 uint32_t identity_high=*(volatile uint32_t *)(identity+4u);
 uint32_t identity_low=*(volatile uint32_t *)identity;
 uint32_t kind=*(volatile uint8_t *)kind_cell;
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,identity_low,identity_high);
 if(row!=0u&&*(volatile uint8_t *)(row+65u)==0u){
  uint32_t stored_high=*(volatile uint32_t *)(row+60u);
  uint32_t stored_low=*(volatile uint32_t *)(row+56u);
  if(((stored_high^high)|(stored_low^low))==0u)return 1u;
  if(opencfw_em9305_radio_key_match_315640(row+16u,low,high)!=0u){
   *(volatile uint32_t *)(row+56u)=low;
   *(volatile uint32_t *)(row+60u)=high;
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
uint32_t opencfw_em9305_radio_address_associate_303844(uint32_t low,uint32_t high,uint32_t kind,uint32_t identity_low,uint32_t identity_high)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,identity_low,identity_high);
 if(row==0u||*(volatile uint8_t *)(row+65u)!=0u)return 0u;
 uint32_t stored_high=*(volatile uint32_t *)(row+60u);
 uint32_t stored_low=*(volatile uint32_t *)(row+56u);
 if(((stored_high^high)|(stored_low^low))==0u)return 1u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x80160cu;
 if(callback==0u)return 0u;
 (void)((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)
   (low,high,0u,kind,identity_low,identity_high);
 return 0u;
}


static void reset(unsigned present,unsigned disabled,unsigned direct,unsigned match,unsigned callback,unsigned slot){memset((void *)0x800000,0,0x100000);row_present=present;keymatch=match;keycalls=callbacks=0;*(uint8_t *)0x820000=3;*(uint32_t *)0x821000=300;*(uint32_t *)0x821004=400;*(uint8_t *)0x830041=disabled;*(uint32_t *)0x830038=direct?100:101;*(uint32_t *)0x83003c=200;*(uint8_t *)0x801638=slot;*(uint32_t *)0x80160c=callback?(uint32_t)(uintptr_t)cb:0;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned present=0;present<2;present++)for(unsigned disabled=0;disabled<2;disabled++)for(unsigned direct=0;direct<2;direct++)for(unsigned match=0;match<2;match++)for(unsigned callback=0;callback<2;callback++)for(unsigned slot=0;slot<4;slot++){reset(present,disabled,direct,match,callback,slot);unsigned expected=present&&!disabled&&(direct||match);assert(opencfw_em9305_radio_address_project_303b7c(100,200,0x820000,0x821000)==expected);assert(keycalls==(present&&!disabled&&!direct));if(expected){assert(*(uint32_t *)0x830038==100&&*(uint32_t *)0x83003c==200&&*(uint8_t *)0x801638==slot);}else{uintptr_t p=0x801618+slot*8;assert(*(uint32_t *)p==100&&*(uint32_t *)(p+4)==200&&*(uint8_t *)0x801638==((slot+1)&3));}cases++;reset(present,disabled,direct,match,callback,slot);unsigned r=opencfw_em9305_radio_address_associate_303844(100,200,3,300,400);assert(r==(present&&!disabled&&direct)&&callbacks==(present&&!disabled&&!direct&&callback)&&keycalls==0&&*(uint8_t *)0x801638==slot);cases++;}printf("PASS %u\n",cases);}
