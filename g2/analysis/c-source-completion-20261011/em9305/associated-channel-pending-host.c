#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned notifications,transforms;
static uint32_t opencfw_em9305_associated_channel_notify_3279a4(uintptr_t r){notifications++;return (uint32_t)r;}
static uint32_t opencfw_em9305_associated_phy_notify_3279b4(uintptr_t r){return (uint32_t)r;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,(int)v,n);}
static uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t c){transforms++;*(uint8_t *)(c+45)=5;return 5;}
#include "associated-channel-pending-host-port.inc"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;uintptr_t r=0x802000,e=0x804000;
 for(unsigned count=0;count<65536;count++)for(unsigned same=0;same<2;same++){
  memset((void *)r,0,3000);notifications=transforms=0;*(uint32_t *)(uintptr_t)0x805c34=(uint32_t)e;
  *(uint32_t *)(e+4)=0x1223;*(uint32_t *)(e+8)=0x4567;*(uint16_t *)(r+752)=(uint16_t)count;
  if(opencfw_em9305_associated_channel_state_327aac(r,0)!=1)abort();
  if(*(uint16_t *)(r+92)!=(uint16_t)(count+6)||*(uint32_t *)(r+84)!=0x1223||*(uint32_t *)(r+88)!=0x4567)abort();
  if(!same)*(uint32_t *)(r+776)=0x7777;
  *(uint16_t *)(r+752)=(uint16_t)(count+6);*(uint8_t *)(r+272)=123;
  uint32_t result=opencfw_em9305_associated_channel_pending_327af4(r);
  if(result!=123||transforms!=1||notifications||*(uint32_t *)(r+128)!=0x1223||*(uint32_t *)(r+132)!=0x4567)abort();
  if(*(uint8_t *)(r+80)!=(same?0:1)||*(uint32_t *)(r+720)!=0x1223||*(uint32_t *)(r+724)!=0x4567)abort();
  if(!same&&*(uint16_t *)(r+92)!=(uint16_t)(count+12))abort();
  cases++;
 }
 for(unsigned event=2;event<6;event++)for(unsigned state=0;state<2;state++){
  memset((void *)r,0,3000);notifications=0;*(uint8_t *)(r+80+(event/2)*96)=(uint8_t)state;
  *(uint32_t *)(r+784)=0x12345678;*(uint8_t *)(r+788)=3;*(uint8_t *)(r+789)=4;*(uint8_t *)(r+796)=5;*(uint8_t *)(r+797)=6;
  uint32_t result=opencfw_em9305_associated_channel_state_327aac(r,event);
  if(result!=(event&1?0:1))abort();
  if(event==2&&notifications!=1)abort();
  if(event==4&&!state&&(*(uint32_t *)(r+276)!=0x12345678||*(uint8_t *)(r+280)!=3||*(uint8_t *)(r+281)!=4||*(uint8_t *)(r+282)!=5||*(uint8_t *)(r+283)!=6))abort();
  cases++;
 }
 printf("PASS %u controlled state/channel contract cases; ARC runtime unqualified\n",cases);
}
