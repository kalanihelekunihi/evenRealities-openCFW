#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t duration_calls,last_args[8];
static uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t mode,uint32_t size){return phy*10000u+mode*1000u+size;}
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){return 5;}
static uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t value){return value+30;}
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static uint32_t opencfw_em9305_config_link_divu_prior(uint32_t a,uint32_t b,uint32_t prior){return b?a/b:prior;}
static uint32_t opencfw_em9305_radio_duration_312be4(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){uint32_t args[8]={a,b,c,d,e,f,g,h};memcpy(last_args,args,sizeof args);duration_calls++;return 0x87654321;}
#include "associated-object-init-prepared.c"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uintptr_t o=0x802000,p=0x804000,data=0x805000;unsigned cases=0;
 for(unsigned type=0;type<256;type++){
  if(type>=2&&type<=9&&type!=4&&type!=5)continue;
  memset((void *)p,0,160);memset((void *)o,0,160);*(uint32_t *)(o+44)=(uint32_t)p;*(uint8_t *)p=(uint8_t)type;
  if(opencfw_em9305_associated_object_init_312918(o,0)!=(uint32_t)(type-2)||*(uint32_t *)(o+12)!=0)abort();
  cases++;
 }
 for(unsigned type=8;type<=9;type++)for(unsigned size=0;size<128;size++)for(unsigned use=0;use<2;use++){
  memset((void *)p,0,160);memset((void *)o,0,160);*(uint32_t *)(o+44)=(uint32_t)p;*(uint8_t *)p=(uint8_t)type;
  *(uint8_t *)(p+12)=3;*(uint8_t *)(p+14)=2;*(uint32_t *)(o+40)=use?(uint32_t)data:0;*(uint16_t *)data=(uint16_t)size;duration_calls=0;
  if(opencfw_em9305_associated_object_init_312918(o,0)!=0x87654321||*(uint32_t *)(o+12)!=0x87654321||duration_calls!=1)abort();
  uint32_t expected=type==9?0:(use&&size>=64?size:64);
  if(last_args[0]!=3||last_args[1]||last_args[2]||last_args[3]||last_args[4]!=expected||last_args[5]||last_args[6]!=2||last_args[7])abort();
  cases++;
 }
 for(unsigned kind=0;kind<4;kind++){
  memset((void *)p,0,160);memset((void *)o,0,160);*(uint32_t *)(o+44)=(uint32_t)p;*(uint8_t *)p=6;
  *(uint8_t *)(p+132)=1;*(uint8_t *)(p+13)=(uint8_t)kind;*(uint8_t *)(p+12)=1;*(uint32_t *)(p+100)=1;
  uint32_t result=opencfw_em9305_associated_object_init_312918(o,0),base=kind==3?720:(kind==2?44:80),extra=kind==3?1916:(kind==2?400:492);
  if(result!=12036||*(uint32_t *)(o+12)!=base+extra+12036||(kind==3&&*(uint32_t *)(o+16)!=17040))abort();
  cases++;
 }
 for(unsigned flags=0;flags<256;flags++)for(unsigned kind=0;kind<4;kind++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned extra=0;extra<2;extra++){
  memset((void *)p,0,160);memset((void *)o,0,160);*(uint32_t *)(o+44)=(uint32_t)p;*(uint8_t *)p=3;
  *(uint8_t *)(p+12)=1;*(uint8_t *)(p+13)=(uint8_t)kind;*(uint8_t *)(p+14)=2;*(uint8_t *)(p+124)=9;*(uint8_t *)(p+127)=(uint8_t)flags;
  *(uint32_t *)(p+104)=enabled;*(uint32_t *)(p+108)=extra;*(uint8_t *)(p+149)=7;
  unsigned count=0;for(unsigned bit=0;bit<3;bit++)count+=(flags>>bit)&1;
  uint32_t expected=(count-1u)*12044u+12009u,ret=12044u;
  if(enabled){ret=(kind==3?3088u:376u)*count;expected+=ret+150u*count;if(extra){ret=10007u*count;expected+=ret+150u*count;}}
  uint32_t result=opencfw_em9305_associated_object_init_312918(o,0);
  if(result!=ret||*(uint32_t *)(o+12)!=expected)abort();
  cases++;
 }
 printf("PASS %u native-contract golden/argument cases; ARC runtime unqualified\n",cases);
}
