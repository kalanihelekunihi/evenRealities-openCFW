#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,valid,identity,allocfail,fail,allocs,sends,errors,kindcalls,idcalls,lastsize,laststatus;static uintptr_t M;static uint32_t sendvalue=0x12345678;
static uint32_t opencfw_em9305_ll_connection_gate_30e524(void){return gate;}
static uint32_t opencfw_em9305_ll_stream_kind_valid_30e4dc(uint32_t k){if(k!=6)fail++;kindcalls++;return valid;}
static uint32_t opencfw_em9305_radio_identity_exists_31445c(uint32_t k,uint32_t lo,uint32_t hi){if(k!=7||lo!=0x1234||hi!=0x5678)fail++;idcalls++;return identity;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t size){allocs++;lastsize=size;return allocfail?0:M;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){if(h!=9||m!=M)fail++;sends++;return sendvalue;}
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
/* Native3082dc..308308: event774 with three explicit cleared fields. */
uint32_t opencfw_em9305_command_advertising_notify_3082dc(void)
{
 uintptr_t message=opencfw_em9305_wsf_event_allocate(24u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=774u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+5u)=0u;
 *(volatile uint32_t *)(message+12u)=0u;
 *(volatile uint32_t *)(message+8u)=0u;
 return opencfw_em9305_wsf_task_message_send(handler,message);
}
/* Native306a7c..306a90: mask mismatch preserves incoming full R0. */
uint32_t opencfw_em9305_command_advertising_data_notify_306a7c(uint32_t mask)
{
 uint32_t configured=*(volatile uint8_t *)(uintptr_t)0x805400u;
 if((configured&mask)!=mask)return mask;
 return opencfw_em9305_command_advertising_notify_3082dc();
}
/* Native30e758..30e774: sparse four-byte error event, actual emitter child. */
uint32_t opencfw_em9305_command_advertising_error_30e758(uint32_t status)
{
 uint8_t event[4] __attribute__((aligned(4)));*(uint16_t *)(void *)event=0u;event[2]=3u;event[3]=(uint8_t)status;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
/* Native30aff8..30b094: captured enable and full mode/capability paths. */
void opencfw_em9305_command_advertising_enable_30aff8(uint32_t enable)
{
 uint32_t gate=opencfw_em9305_ll_connection_gate_30e524();
 uintptr_t state=0x805b84u;
 if(gate==0u){(void)opencfw_em9305_command_advertising_error_30e758(12u);return;}
 uint32_t mode=*(volatile uint8_t *)(state+12u);
 if(mode<5u&&(0x13u&(1u<<mode))!=0u){
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t active=*(volatile uint8_t *)(uintptr_t)0x805a70u,capacity=*(volatile uint8_t *)(config+34u);
  if(active==capacity){(void)opencfw_em9305_command_advertising_error_30e758(12u);return;}
 }
 if(enable!=1u||opencfw_em9305_ll_stream_kind_valid_30e4dc(*(volatile uint8_t *)(state+13u))!=0u){
  uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);if(message==0u)return;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint8_t *)(message+3u)=(uint8_t)(1u+(enable==0u));
  *(volatile uint8_t *)(message+2u)=4u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);return;
 }
 mode=*(volatile uint8_t *)(state+12u);
 if(mode==3u){
  uint32_t high=*(volatile uint32_t *)(state+20u),low=*(volatile uint32_t *)(state+16u),kind=*(volatile uint8_t *)(state+14u);
  if(opencfw_em9305_radio_identity_exists_31445c(kind,low,high)!=0u){
   uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
   if(message!=0u){*(volatile uint16_t *)(message+2u)=260u;uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;(void)opencfw_em9305_wsf_task_message_send(handler,message);return;}
  }
 }
 (void)opencfw_em9305_command_advertising_error_30e758(18u);
}

uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){if(*(uint16_t*)p||*(uint8_t*)(p+2)!=3)fail++;errors++;laststatus=*(uint8_t*)(p+3);return 55;}
int main(void){if(mmap((void*)0x800000,131072,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;M=0x810000;*(uint8_t*)0x805b18=9;unsigned cases=0;
 for(unsigned mode=0;mode<256;mode++)for(unsigned enable=0;enable<4;enable++)for(unsigned bits=0;bits<64;bits++){
 gate=bits&1;valid=(bits>>1)&1;identity=(bits>>2)&1;allocfail=(bits>>3)&1;unsigned equal=(bits>>4)&1;unsigned spare=(bits>>5)&1;(void)spare;*(uint32_t*)0x805cac=0x811000;*(uint8_t*)0x811022=5;*(uint8_t*)0x805a70=equal?5:4;*(uint8_t*)0x805b90=mode;*(uint8_t*)0x805b91=6;*(uint8_t*)0x805b92=7;*(uint32_t*)0x805b94=0x1234;*(uint32_t*)0x805b98=0x5678;
 allocs=sends=errors=kindcalls=idcalls=laststatus=0;memset((void*)M,0xa5,24);uint8_t exp[24];memset(exp,0xa5,24);unsigned ea=0,es=0,ee=0,ek=0,ei=0,st=0;
 if(!gate||(mode<5&&(0x13&(1u<<mode))&&equal)){ee=1;st=12;}
 else{ek=enable==1;if(enable!=1||valid){ea=1;if(!allocfail){es=1;exp[2]=4;exp[3]=1+(enable==0);}}
 else{ei=mode==3;if(mode==3&&identity){ea=1;if(!allocfail){es=1;*(uint16_t*)(exp+2)=260;}else{ee=1;st=18;}}else{ee=1;st=18;}}}
 opencfw_em9305_command_advertising_enable_30aff8(enable);
 if(allocs!=ea||sends!=es||errors!=ee||kindcalls!=ek||idcalls!=ei||laststatus!=st||memcmp(exp,(void*)M,24)||(ea&&lastsize!=4))fail++;cases++;
 }
 for(unsigned configured=0;configured<256;configured++)for(unsigned mask=0;mask<256;mask++)for(allocfail=0;allocfail<2;allocfail++){
 *(uint8_t*)0x805400=configured;allocs=sends=0;memset((void*)M,0xa5,24);uint8_t exp[24];memset(exp,0xa5,24);unsigned allowed=(configured&mask)==mask;
 uint32_t want=allowed?(allocfail?0:sendvalue):mask;
 if(allowed&&!allocfail){*(uint16_t*)(exp+2)=774;exp[5]=0;*(uint32_t*)(exp+8)=0;*(uint32_t*)(exp+12)=0;}
 uint32_t got=opencfw_em9305_command_advertising_data_notify_306a7c(mask);
 if(got!=want||allocs!=allowed||sends!=(allowed&&!allocfail)||memcmp(exp,(void*)M,24)||(allowed&&lastsize!=24))fail++;cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
