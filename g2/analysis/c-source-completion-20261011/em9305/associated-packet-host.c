#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned refills,continues,starts,customs;
static uint32_t opencfw_em9305_associated_packet_refill_3259fc(uintptr_t r){refills++;*(uint32_t *)(r+692)=0;return 123;}
static uint32_t opencfw_em9305_associated_packet_continue_323ac8(uintptr_t r,uintptr_t p,uintptr_t size,uint32_t one){if(p!=r+1077||size!=r+1144||one!=1)abort();continues++;*(uint16_t *)(r+1154)=77;*(uint32_t *)(r+1148)=0x803000;return 0x12345;}
static uint32_t opencfw_em9305_associated_packet_start_3243e0(uintptr_t r,uintptr_t p,uintptr_t size,uint32_t one){if(p!=r+1077||size!=r+1144||one!=1)abort();starts++;*(uint16_t *)(r+1154)=88;*(uint32_t *)(r+1148)=0x803100;*(uint32_t *)(r+692)=0;return 0x56789;}
static uint32_t custom_callback(uintptr_t r,uintptr_t self){if(self!=(uintptr_t)custom_callback)abort();customs++;*(uint16_t *)(r+1154)=99;*(uint32_t *)(r+1148)=0x803200;*(uint32_t *)(r+692)=0;return 0;}
#include "associated-packet-host-port.inc"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;uintptr_t r=0x802000,o=0x804000;
 for(unsigned count=0;count<256;count++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned consumed=0;consumed<3;consumed++){
  memset((void *)r,0,3000);memset((void *)o,0,64);refills=continues=starts=customs=0;
  *(uint32_t *)(o+36)=(uint32_t)r;*(uint32_t *)(r+692)=0xface1234;*(uint8_t *)(r+697)=0x98;
  *(uint8_t *)(r+804)=(uint8_t)enabled;*(uint8_t *)(r+806)=(uint8_t)count;*(uint16_t *)(r+1144)=1;*(uint16_t *)(r+1154)=(uint16_t)consumed;
  uint32_t result=opencfw_em9305_associated_packet_callback_32c69c(o,1);
  unsigned remaining=enabled?(uint8_t)(count-1):count;
  if(result!=0xface1234||*(uint8_t *)(r+429)!=0x98||continues!=1||starts||customs||refills!=(consumed<1||remaining!=0))abort();
  if(*(uint8_t *)(r+806)!=remaining||*(uint16_t *)(r+564)!=0x2345||*(uint32_t *)(r+576)!=0x803000+consumed||*(uint16_t *)(r+572)!=(uint16_t)(77-consumed))abort();
  cases++;
 }
 uint32_t times[]={0,599,600,1250,491459,491460,0xffffffff};
 uint16_t periods[]={0,1,65535};
 for(unsigned custom=0;custom<2;custom++)for(unsigned active=0;active<2;active++)for(unsigned t=0;t<7;t++)for(unsigned p=0;p<3;p++){
  memset((void *)r,0,3000);memset((void *)o,0,64);refills=continues=starts=customs=0;
  *(uint32_t *)(o+36)=(uint32_t)r;*(uint32_t *)(o+8)=100;*(uint32_t *)(r+692)=0xface1234;
  *(uint8_t *)(r+2809)=(uint8_t)custom;*(uint32_t *)(r+2816)=(uint32_t)(uintptr_t)custom_callback;
  *(uint8_t *)(r+176)=(uint8_t)active;*(uint32_t *)(r+180)=100+times[t];*(uint16_t *)(r+190)=periods[p];
  *(uint8_t *)(r+193)=3;*(uint32_t *)(r+236)=0xfffffffe;*(uint32_t *)(r+240)=9;
  uint32_t result=opencfw_em9305_associated_packet_callback_32c69c(o,0);
  if(result!=0xface1234||continues||refills!=!custom||starts!=!custom||customs!=custom)abort();
  if(*(uint8_t *)(r+176)!=active||*(uint16_t *)(r+536)!=(custom?99:88)||*(uint32_t *)(r+540)!=(custom?0x803200:0x803100))abort();
  if(!custom&&*(uint16_t *)(r+528)!=0x6789)abort();
  if(active&&times[t]<=599&&(*(uint32_t *)(r+236)!=1||*(uint32_t *)(r+240)!=10))abort();
  cases++;
 }
 printf("PASS %u controlled packet callback cases; ARC runtime unqualified\n",cases);
}
