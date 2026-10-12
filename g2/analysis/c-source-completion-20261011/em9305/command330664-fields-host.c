#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned pre,calls,allocs,sends,status_events,length,fail,want_status=7;
static uint8_t *input_seen;
static uint8_t output[8];
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t command){(void)command;allocs++;length=n;return fail?0:(uintptr_t)(output+5);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output);sends++;return 77;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t v){(void)p;assert(v==want_status);status_events++;return 99;}
/* Native330664..330848 full command parent. Deeper provider ABIs from call sites; bodies unresolved. */
extern uint32_t opencfw_em9305_command_prehandle_330bdc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_scan_params_30b9f4(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_create_30c488(uintptr_t);
extern uint32_t opencfw_em9305_command_disable_30c54c(void);
extern uint32_t opencfw_em9305_command_timeout_30c600(uint32_t);
extern uint32_t opencfw_em9305_command_address_add_30aed4(uintptr_t);
extern uint32_t opencfw_em9305_command_address_remove_30ca1c(uintptr_t);
extern uint32_t opencfw_em9305_command_address_clear_30b12c(void);
extern uint32_t opencfw_em9305_command_scan_extended_30d774(uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_power_query_30c80c(uintptr_t);
uint32_t opencfw_em9305_dispatch_330664(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_command_prehandle_330bdc(request,input)!=0u)return 1u;
 uint32_t opcode=*(volatile uint16_t *)request,slot=opcode-0x2041u,status=0u;
 if(slot>9u)return 0u;
 _Alignas(4) uint8_t scratch[24];
 switch(slot){
 case 0u:{
  uint32_t first=*(volatile uint8_t *)input,second=*(volatile uint8_t *)(input+1u),mask=*(volatile uint8_t *)(input+2u);
  scratch[0]=(uint8_t)first;scratch[1]=(uint8_t)second;scratch[2]=(uint8_t)mask;
  uintptr_t cursor=input+3u;uint32_t count=0u;
  for(uint32_t bit=0u;bit<=7u&&count<=2u;++bit){
   if((mask&(1u<<bit))!=0u){
    uint32_t hi_a=*(volatile uint8_t *)(cursor+2u),hi_b=*(volatile uint8_t *)(cursor+4u);
    uint32_t lo_a=*(volatile uint8_t *)(cursor+1u),lo_b=*(volatile uint8_t *)(cursor+3u);
    uint32_t flags=*(volatile uint8_t *)cursor;
    uintptr_t row=(uintptr_t)scratch+count*6u;
    count++;cursor+=5u;
    *(uint8_t *)(row+8u)=(uint8_t)flags;
    *(uint16_t *)(row+4u)=(uint16_t)(lo_a+(hi_a<<8u));
    *(uint16_t *)(row+6u)=(uint16_t)(lo_b+(hi_b<<8u));
   }
  }
  status=opencfw_em9305_command_scan_extended_30d774(first,second,mask,(uintptr_t)scratch+4u);break;
 }
 case 1u:{
  uint32_t ah=*(volatile uint8_t *)(input+3u),bh=*(volatile uint8_t *)(input+5u);
  uint32_t al=*(volatile uint8_t *)(input+2u),bl=*(volatile uint8_t *)(input+4u);
  uint32_t second=*(volatile uint8_t *)(input+1u),first=*(volatile uint8_t *)input;
  (void)opencfw_em9305_command_scan_params_30b9f4(first,second,al+(ah<<8u),bl+(bh<<8u));return 1u;
 }
 case 2u:return 0u;
 case 3u:{
  uint32_t ah=*(volatile uint8_t *)(input+10u),bh=*(volatile uint8_t *)(input+12u),flags=*(volatile uint8_t *)input;
  uint32_t al=*(volatile uint8_t *)(input+9u),bl=*(volatile uint8_t *)(input+11u);
  uint32_t second=*(volatile uint8_t *)(input+1u),third=*(volatile uint8_t *)(input+2u),last=*(volatile uint8_t *)(input+13u);
  scratch[0]=(uint8_t)flags;scratch[1]=(uint8_t)second;scratch[2]=(uint8_t)third;
  *(uint32_t *)(scratch+4u)=(uint32_t)(input+3u);
  scratch[12]=(uint8_t)last;
  *(uint16_t *)(scratch+8u)=(uint16_t)(al+(ah<<8u));*(uint16_t *)(scratch+10u)=(uint16_t)(bl+(bh<<8u));
  if((flags&2u)!=0u&&(*(volatile uint8_t *)(uintptr_t)0x8058adu&32u)==0u)status=62u;
  else if((flags&4u)!=0u&&(*(volatile uint8_t *)(uintptr_t)0x805b34u&16u)==0u)status=17u;
  else status=opencfw_em9305_command_create_30c488((uintptr_t)scratch);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);return 1u;
 }
 case 4u:status=opencfw_em9305_command_disable_30c54c();break;
 case 5u:{uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;status=opencfw_em9305_command_timeout_30c600(low+(high<<8u));break;}
 case 6u:case 7u:{
  uint32_t first=*(volatile uint8_t *)input,last=*(volatile uint8_t *)(input+7u);
  *(uint32_t *)(scratch+4u)=(uint32_t)(input+1u);scratch[0]=(uint8_t)first;scratch[8]=(uint8_t)last;
  status=slot==6u?opencfw_em9305_command_address_add_30aed4((uintptr_t)scratch):opencfw_em9305_command_address_remove_30ca1c((uintptr_t)scratch);break;
 }
 case 8u:status=opencfw_em9305_command_address_clear_30b12c();break;
 case 9u:break;
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(slot==9u?2u:1u,*(volatile uint16_t *)request);
 if(response==0u)return 1u;
 uint32_t fresh=*(volatile uint16_t *)request,position=fresh-0x2041u;
 if((position<10u&&(499u&(1u<<position))!=0u)||fresh==0x2081u)*(volatile uint8_t *)response=(uint8_t)status;
 else if(position==9u){
  scratch[0]=0u;
  uint32_t result=opencfw_em9305_command_power_query_30c80c((uintptr_t)scratch);
  *(volatile uint8_t *)response=(uint8_t)result;
  *(volatile uint8_t *)(response+1u)=scratch[0];
 }
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}

uint32_t opencfw_em9305_command_prehandle_330bdc(uintptr_t a0,uintptr_t a1){(void)a0;(void)a1;return pre;}
uint32_t opencfw_em9305_command_scan_params_30b9f4(uint32_t a0,uint32_t a1,uint32_t a2,uint32_t a3){assert(a0==input_seen[0]&&a1==input_seen[1]&&a2==(unsigned)(input_seen[2]|input_seen[3]<<8)&&a3==(unsigned)(input_seen[4]|input_seen[5]<<8));calls++;return 7;}
uint32_t opencfw_em9305_command_create_30c488(uintptr_t a0){assert(*(uint8_t *)a0==input_seen[0]&&*(uint8_t *)(a0+1)==input_seen[1]&&*(uint8_t *)(a0+2)==input_seen[2]);assert(*(uint32_t *)(a0+4)==(uintptr_t)(input_seen+3));assert(*(uint16_t *)(a0+8)==(unsigned)(input_seen[9]|input_seen[10]<<8)&&*(uint16_t *)(a0+10)==(unsigned)(input_seen[11]|input_seen[12]<<8)&&*(uint8_t *)(a0+12)==input_seen[13]);calls++;return 7;}
uint32_t opencfw_em9305_command_disable_30c54c(void){calls++;return 7u;}
uint32_t opencfw_em9305_command_timeout_30c600(uint32_t a0){assert(a0==(unsigned)(input_seen[0]|input_seen[1]<<8));calls++;return 7;}
uint32_t opencfw_em9305_command_address_add_30aed4(uintptr_t a0){assert(*(uint8_t *)a0==input_seen[0]&&*(uint32_t *)(a0+4)==(uintptr_t)(input_seen+1)&&*(uint8_t *)(a0+8)==input_seen[7]);calls++;return 7;}
uint32_t opencfw_em9305_command_address_remove_30ca1c(uintptr_t a0){assert(*(uint8_t *)a0==input_seen[0]&&*(uint32_t *)(a0+4)==(uintptr_t)(input_seen+1)&&*(uint8_t *)(a0+8)==input_seen[7]);calls++;return 7;}
uint32_t opencfw_em9305_command_address_clear_30b12c(void){calls++;return 7u;}
uint32_t opencfw_em9305_command_scan_extended_30d774(uint32_t a0,uint32_t a1,uint32_t a2,uintptr_t a3){assert(a0==input_seen[0]&&a1==input_seen[1]&&a2==input_seen[2]);unsigned row=0,cursor=3;for(unsigned bit=0;bit<8&&row<3;bit++)if(a2&(1u<<bit)){assert(*(uint16_t *)(a3+row*6)==(unsigned)(input_seen[cursor+1]|input_seen[cursor+2]<<8));assert(*(uint16_t *)(a3+row*6+2)==(unsigned)(input_seen[cursor+3]|input_seen[cursor+4]<<8));assert(*(uint8_t *)(a3+row*6+4)==input_seen[cursor]);row++;cursor+=5;}calls++;return 7;}
uint32_t opencfw_em9305_command_power_query_30c80c(uintptr_t a0){(void)a0;calls++;*(uint8_t *)a0=3u;return 9u;}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);input_seen=(void *)0x810000;uint16_t request;unsigned cases=0;
for(unsigned seed=0;seed<256;seed++)for(unsigned mask=0;mask<256;mask++){for(unsigned j=0;j<48;j++)input_seen[j]=(uint8_t)(seed+j*37);input_seen[2]=mask;request=0x2041;calls=allocs=sends=status_events=0;assert(opencfw_em9305_dispatch_330664((uintptr_t)&request,(uintptr_t)input_seen)==1&&calls==1&&allocs==1&&sends==1&&output[5]==7);cases++;}
for(unsigned flags=0;flags<256;flags++)for(unsigned gates=0;gates<4;gates++){for(unsigned j=0;j<48;j++)input_seen[j]=(uint8_t)(flags+j*37);input_seen[0]=flags;*(uint8_t *)0x8058ad=(gates&1)?32:0;*(uint8_t *)0x805b34=(gates&2)?16:0;want_status=(flags&2)&&!(gates&1)?62:(flags&4)&&!(gates&2)?17:7;request=0x2044;calls=allocs=sends=status_events=0;assert(opencfw_em9305_dispatch_330664((uintptr_t)&request,(uintptr_t)input_seen)==1&&calls==(want_status==7)&&status_events==1&&!allocs&&!sends);cases++;}
want_status=7;for(unsigned seed=0;seed<256;seed++)for(unsigned slot=1;slot<=8;slot++){if(slot==2||slot==3)continue;for(unsigned j=0;j<48;j++)input_seen[j]=(uint8_t)(seed+j*37);request=0x2041+slot;calls=allocs=sends=status_events=0;assert(opencfw_em9305_dispatch_330664((uintptr_t)&request,(uintptr_t)input_seen)==1&&calls==1);cases++;}
printf("PASS %u\n",cases);}
