#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b){uint32_t d=a-b;return (int32_t)d<0?0:d;}
static uint32_t opencfw_em9305_associated_packet_high_product(uint32_t a,uint32_t b){return (uint32_t)(((uint64_t)a*b)>>32);}
struct opencfw_em9305_native_product_pair{uint32_t low,high;};
static struct opencfw_em9305_native_product_pair opencfw_em9305_native_mpydu_329154(uint32_t a,uint32_t b){uint64_t v=(uint64_t)a*b;return (struct opencfw_em9305_native_product_pair){(uint32_t)v,(uint32_t)(v>>32)};}
#include "compose-aux-prepared.c"
int main(void){if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)0x800000)abort();
 uintptr_t record=0x802000,output=0x804000;*(uint32_t *)(uintptr_t)0x805c18=0x804100;
 unsigned values[]={0,300,301,245699,245700,245701,2457599,2457600};unsigned periods[]={30,300,600,300000,0xffffffffu};unsigned slots[]={0,1,128,255};unsigned cases=0;
 for(unsigned metric=0;metric<256;metric++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned si=0;si<4;si++)for(unsigned pi=0;pi<5;pi++)for(unsigned vi=0;vi<8;vi++){
  unsigned slot=slots[si],period=periods[pi],requested=values[vi];if(period==0xffffffffu&&requested<301)continue;
  memset((void *)record,0,2900);memset((void *)output,0xa5,32);*(uint16_t *)(uintptr_t)0x804100=metric;*(uint8_t *)(uintptr_t)0x805aa8=5;
  *(uint8_t *)(record+2809)=enabled;*(uint8_t *)(record+799)=slot;*(uint32_t *)(record+792)=16;*(uint32_t *)(record+700)=period;
  uint32_t next=requested;if(enabled&&(slot&127))next=requested+16*slot-period;*(uint32_t *)(record+388)=next;
  *(uint32_t *)(record+720)=0x76543210;*(uint32_t *)(record+724)=17;*(uint32_t *)(record+432)=0x12345678;*(uint32_t *)(record+436)=0xabcdef01;*(uint16_t *)(record+376)=0xffff;
  uint32_t result=opencfw_em9305_compose_aux_encode_324438(record,output);uint8_t *o=(uint8_t *)output;
  uint32_t elapsed=requested;while(elapsed<301)elapsed+=period;uint32_t q,sel=0;
  if(elapsed<245700){q=(uint32_t)(((uint64_t)elapsed*0x11111112)>>32)>>1;}
  else{sel=elapsed<2457600;if(elapsed>=2457600)elapsed=0;q=(3*elapsed+(uint32_t)(((uint64_t)elapsed*0x69d0369e)>>32))>>10;}
  uint64_t scaled=(uint64_t)period*0x1a36e3;unsigned accuracy=(metric<21?7:metric<31?6:metric<51?5:metric<76?4:metric<101?3:metric<151?2:metric<251?1:0)+5;
  uint8_t expected[18]={(uint8_t)q,(uint8_t)((q|(sel<<13))>>8),(uint8_t)(scaled>>31),(uint8_t)(scaled>>39),0x10,0x32,0x54,0x76,(uint8_t)((accuracy<<5)+17),0x78,0x56,0x34,0x12,0x01,0xef,0xcd,0xff,0xff};
  if(enabled&&(slot&127)){expected[16]=0;expected[17]=0;if(result!=256)abort();}else if(result!=255)abort();
  if(memcmp(o,expected,18))abort();
  for(unsigned i=18;i<32;i++)if(o[i]!=0xa5)abort();
  cases++;
 }printf("PASS %u controlled auxiliary descriptor cases\n",cases);return 0;}
