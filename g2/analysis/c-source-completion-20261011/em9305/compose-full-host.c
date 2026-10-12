#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned debug_case[5];
static _Noreturn void die(unsigned line){fprintf(stderr,"failure line%u case %u/%u/%u/%u/%u cursor%lx\n",line,debug_case[0],debug_case[1],debug_case[2],debug_case[3],debug_case[4],(unsigned long)*(uint32_t *)(uintptr_t)0x803000);exit(1);}
#define abort() die(__LINE__)
static uintptr_t finalized_cursor;static uint32_t finalized_present,finalized_type;
static uint32_t opencfw_em9305_auxiliary_ready_303f68(void){return 0x805000;}
static uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t out,uint32_t low,uint32_t high){for(unsigned i=0;i<4;i++)*(uint8_t *)(out+i)=(uint8_t)(low>>(8*i));for(unsigned i=0;i<2;i++)*(uint8_t *)(out+4+i)=(uint8_t)(high>>(8*i));return out;}
static uint32_t opencfw_em9305_compose_aux_encode_324438(uintptr_t r,uintptr_t out){(void)r;memset((void *)out,0xdd,18);return 18;}
static uint32_t opencfw_em9305_compose_finalize_32412c(uintptr_t r,uintptr_t cursor,uintptr_t header,uint32_t present,uint32_t type){(void)r;(void)header;finalized_cursor=cursor;finalized_present=present;finalized_type=type;return 0;}
static uint32_t opencfw_em9305_compose_action_3237e8(uintptr_t r,uintptr_t out){(void)r;(void)out;abort();}
static uint32_t opencfw_em9305_compose_action_32366c(uintptr_t r,uintptr_t out){(void)r;(void)out;abort();}
static uint32_t opencfw_em9305_compose_action_323820(uintptr_t r,uintptr_t out){(void)r;(void)out;abort();}
static uint32_t opencfw_em9305_command_radio_power_310230(int32_t x,uint32_t one){if(one!=1)abort();return (uint8_t)x;}
static uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t out,uintptr_t in){memcpy((void *)out,(void *)in,3);return 3;}
static void *opencfw_em9305_memcpy(void *out,const void *in,uint32_t n){return memcpy(out,in,n);}
#include "compose-full-prepared.c"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uintptr_t r=0x802000,source=0x803000,out=0x804000,header=0x804400;unsigned cases=0;
 for(unsigned total=0;total<256;total++)for(unsigned limit=0;limit<256;limit++)for(unsigned field=0;field<2;field++)for(unsigned enabled=0;enabled<2;enabled++){
  debug_case[0]=total;debug_case[1]=limit;debug_case[2]=field;debug_case[3]=enabled;
  memset((void *)r,0,3000);memset((void *)source,0,64);memset((void *)out,0xaa,512);memset((void *)header,0,16);
  *(uint8_t *)header=7;*(uint16_t *)source=(uint16_t)total;*(uint8_t *)(r+76)=(uint8_t)limit;*(uint8_t *)(r+804)=field;
  *(uint8_t *)(uintptr_t)0x805a87=(uint8_t)!enabled;finalized_cursor=0xdeadbeef;
  uint32_t result=opencfw_em9305_radio_compose_323dc0(r,0,16,0,header,source,out,4,1);
  unsigned initial=enabled?(limit<253?limit:253):0;
  unsigned present=total>initial||field;
  unsigned capacity=initial;if(capacity>(present?250u:254u))capacity=present?250:254;if(capacity>total)capacity=total;
  if(result!=(present?7:3)||finalized_cursor!=(present?out+4:0)||finalized_present!=(present?16:0)||finalized_type!=4)abort();
  if(*(uint8_t *)(header+4)!=(uint8_t)(capacity+(present?5:1))||*(uint16_t *)(source+10)!=capacity||*(uint8_t *)(out+2)!=(present?4:0)||*(uint8_t *)(out+3)!=(present?16:0))abort();
  cases++;
 }
 for(unsigned mask=0;mask<4;mask++)for(unsigned phy=0;phy<256;phy++){
  debug_case[0]=mask;debug_case[1]=phy;debug_case[4]=1;
  memset((void *)r,0,3000);memset((void *)out,0xaa,512);memset((void *)header,0,16);
  *(uint32_t *)(r+16)=0x44332211;*(uint32_t *)(r+20)=0x6655;*(uint32_t *)(r+24)=0xaa998877;*(uint32_t *)(r+28)=0xccbb;
  *(uint16_t *)(r+706)=0x1234;*(uint8_t *)(r+66)=(uint8_t)phy;
  uint32_t result=opencfw_em9305_radio_compose_323dc0(r,mask|8,0,0,header,0,out,6,1);
  unsigned offset=4+((mask&1)?6:0)+((mask&2)?6:0);
  if(result!=offset+2||finalized_present!=(mask|8)||*(uint8_t *)(out+offset)!=0x34||*(uint8_t *)(out+offset+1)!=(uint8_t)((phy<<4)+2))abort();
  cases++;
 }
 printf("PASS %u controlled compositor contract cases; ARC runtime unqualified\n",cases);
}
