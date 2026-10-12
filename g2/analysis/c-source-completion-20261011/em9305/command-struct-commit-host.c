#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t H,C,R,A,B,M,D;static unsigned present,allocfail,mutate,fail,copies,allocs,sends,packs;static uint32_t seed;
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){if(id!=(uint8_t)seed)fail++;return present?R:0;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){if(d!=(void*)(A+82)||s!=(void*)C||n!=12)fail++;copies++;memcpy(d,s,n);if(mutate&1)*(uint32_t*)(R+0xafc)=B;return d;}
static uint64_t opencfw_em9305_controller_pack_address(uintptr_t a){packs++;uint64_t v=0;for(unsigned j=0;j<6;j++)v|=(uint64_t)*(uint8_t*)(a+j)<<(j*8);return v;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=20)fail++;allocs++;if(mutate&2){*(uint8_t*)(H+9)=7;*(uint8_t*)(H+1)=9;*(uint8_t*)(H+2)=11;*(uint32_t*)(H+4)=D+8;*(uint8_t*)0x805b18=13;}return allocfail?0:M;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){if(h!=(mutate&2?13:17)||m!=M)fail++;sends++;return 73;}
/* Native306cec..306d7c: single-stream projection, fresh record reloads,
 * sparse event275 and nonfatal allocation failure. */
uint32_t opencfw_em9305_command_struct_commit_306cec(uintptr_t header,uintptr_t controls)
{
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)(header+9u));
 if(record==0u)return 66u;
 uintptr_t pointer=record+0xafcu;
 uintptr_t target=*(volatile uint32_t *)pointer;
 (void)opencfw_em9305_memcpy((void *)(target+82u),(const void *)controls,12u);
 target=*(volatile uint32_t *)pointer;
 uint32_t kind=*(volatile uint8_t *)(header+1u),address_kind=*(volatile uint8_t *)(header+2u);
 uintptr_t address=*(volatile uint32_t *)(header+4u);
 *(volatile uint8_t *)(target+65u)=(uint8_t)kind;
 *(volatile uint8_t *)(target+66u)=(uint8_t)address_kind;
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 target=*(volatile uint32_t *)pointer;
 uint32_t stream=*(volatile uint8_t *)(header+10u);
 *(volatile uint8_t *)(record+0x8d5u)=1u;
 *(volatile uint32_t *)(target+68u)=(uint32_t)packed;
 *(volatile uint32_t *)(target+72u)=(uint32_t)(packed>>32u);
 *(volatile uint8_t *)(target+76u)=(uint8_t)stream;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(20u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=275u;
 uint32_t id=*(volatile uint8_t *)(header+9u);
 kind=*(volatile uint8_t *)(header+1u);address_kind=*(volatile uint8_t *)(header+2u);
 *(volatile uint16_t *)message=(uint16_t)id;
 address=*(volatile uint32_t *)(header+4u);
 *(volatile uint8_t *)(message+5u)=(uint8_t)kind;
 *(volatile uint8_t *)(message+6u)=(uint8_t)address_kind;
 packed=opencfw_em9305_controller_pack_address(address);
 *(volatile uint32_t *)(message+8u)=(uint32_t)packed;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint32_t *)(message+12u)=(uint32_t)(packed>>32u);
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

int main(void){if(mmap((void*)0x800000,131072,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;
 H=0x810000;C=H+64;R=H+256;A=H+4096;B=H+4352;M=H+4608;D=H+4864;unsigned cases=0;
 for(seed=0;seed<256;seed++)for(present=0;present<2;present++)for(allocfail=0;allocfail<2;allocfail++)for(mutate=0;mutate<4;mutate++){
  memset((void*)R,0xa5,2824);memset((void*)A,0xa5,96);memset((void*)B,0xa5,96);memset((void*)M,0xa5,20);
  for(unsigned j=0;j<12;j++)*(uint8_t*)(C+j)=(uint8_t)(seed+31*j);for(unsigned j=0;j<16;j++)*(uint8_t*)(D+j)=(uint8_t)(seed+17*j);
  *(uint8_t*)(H+9)=seed;*(uint8_t*)(H+10)=seed^67;*(uint8_t*)(H+1)=seed^31;*(uint8_t*)(H+2)=seed^47;*(uint32_t*)(H+4)=D;*(uint32_t*)(R+0xafc)=A;*(uint8_t*)0x805b18=17;
  copies=allocs=sends=packs=0;uint32_t ret=opencfw_em9305_command_struct_commit_306cec(H,C);
  if(ret!=(present?0:66)||copies!=present||allocs!=present||sends!=(present&&!allocfail)||packs!=(present?(allocfail?1:2):0))fail++;
  if(present){
   uint8_t ea[96],eb[96],em[20];memset(ea,0xa5,96);memset(eb,0xa5,96);memset(em,0xa5,20);memcpy(ea+82,(void*)C,12);uint8_t *et=mutate&1?eb:ea;
   et[65]=seed^31;et[66]=seed^47;memcpy(et+68,(void*)D,6);et[74]=et[75]=0;et[76]=seed^67;
   if(!allocfail){*(uint16_t*)(em+2)=275;*(uint16_t*)em=mutate&2?7:seed;em[5]=mutate&2?9:seed^31;em[6]=mutate&2?11:seed^47;memcpy(em+8,(void*)(D+(mutate&2?8:0)),6);em[14]=em[15]=0;}
   if(memcmp((void*)A,ea,96)||memcmp((void*)B,eb,96)||memcmp((void*)M,em,20)||*(uint8_t*)(R+0x8d5)!=1)fail++;
  }
  cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
