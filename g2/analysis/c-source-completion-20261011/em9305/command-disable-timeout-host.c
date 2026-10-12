#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocs,sends,fail,current_timeout,disable;
static _Alignas(4) uint8_t message[56];
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==56);allocs++;*(uint8_t *)0x805b18=9;return fail?0:(uintptr_t)message;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==9&&p==(uintptr_t)message);assert(*(uint16_t *)(message+2)==(disable?523:525));assert(*(uint16_t *)message==(disable?0xa5a5:current_timeout));for(unsigned j=4;j<56;j++)assert(message[j]==0xa5);sends++;return 77;}
uint32_t opencfw_em9305_ll_stream_gate_30e510(void)
{
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a9eu;
 if(busy==0u) *(volatile uint8_t *)(uintptr_t)0x805a9fu=1u;
 return busy==0u;
}
uint32_t opencfw_em9305_address_busy_307cb8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==1u;}
uint32_t opencfw_em9305_command_ready_3213d0(uint32_t id)
{
 if(id>5u)return 0u;
 uint32_t offset;
 offset=id*784u; /* Host-only bounded id<=5 native stride normalization. */
 return *(volatile uint8_t *)(uintptr_t)(0x803d78u+offset)!=0u;
}
/* Native30c54c..30c57e: disable allowed only in product state1. */
uint32_t opencfw_em9305_command_disable_30c54c(void)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(opencfw_em9305_address_busy_307cb8()==0u)return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(56u);
 if(message!=0u){
  *(volatile uint16_t *)(message+2u)=523u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}
/* Native30c600..30c64e: original full-width timeout guards, then halfword message. */
uint32_t opencfw_em9305_command_timeout_30c600(uint32_t timeout)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(timeout>=3840u)return 18u;
 if(opencfw_em9305_command_ready_3213d0(timeout)==0u)return 66u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(56u);
 if(message!=0u){
  *(volatile uint16_t *)message=(uint16_t)timeout;
  *(volatile uint16_t *)(message+2u)=525u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
disable=1;for(unsigned gate=0;gate<256;gate++)for(unsigned state=0;state<256;state++)for(fail=0;fail<2;fail++){*(uint8_t *)0x805a9e=gate;*(uint8_t *)0x8051a4=state;allocs=sends=0;memset(message,0xa5,56);unsigned admitted=gate==0&&state==1;assert(opencfw_em9305_command_disable_30c54c()==(admitted?0u:12u));assert(allocs==admitted&&sends==(admitted&&!fail));cases++;}
disable=0;for(current_timeout=0;current_timeout<65536;current_timeout++)for(unsigned mode=0;mode<8;mode++)for(fail=0;fail<2;fail++){unsigned gate=mode&1,ready_flag=(mode>>1)&1,busy=(mode>>2)&1;*(uint8_t *)0x805a9e=gate;*(uint8_t *)0x8051a4=busy;for(unsigned j=0;j<6;j++)*(uint8_t *)(uintptr_t)(0x803d78+j*784)=ready_flag;allocs=sends=0;memset(message,0xa5,56);unsigned ready=current_timeout<=5&&ready_flag;unsigned result=gate?12:current_timeout>=3840?18:!ready?66:busy?12:0;assert(opencfw_em9305_command_timeout_30c600(current_timeout)==result);assert(allocs==(result==0)&&sends==(result==0&&!fail));cases++;}
*(uint8_t *)0x805a9e=0;assert(opencfw_em9305_command_timeout_30c600(0xffffffff)==18);cases++;printf("PASS %u\n",cases);}
