#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,available,fail,allocs,sends,errors,status_seen,available_calls;
static _Alignas(4) uint8_t message[16];
static uint32_t opencfw_em9305_ll_stream_gate_30e510(void){assert(*(uint8_t *)0x805a7e==0&&*(uint8_t *)0x805a7d==7);return gate;}
uint32_t opencfw_em9305_scan_available_307b9c(void){available_calls++;return available;}
uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t status){assert(*(uint8_t *)0x805a7d==1);errors++;status_seen=status;return 55;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==16);allocs++;*(uint8_t *)0x805b18=9;return fail?0:(uintptr_t)message;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==9&&p==(uintptr_t)message);sends++;return 67;}
extern uint32_t opencfw_em9305_scan_available_307b9c(void);
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
/* Native30b9f4..30ba84: product mirror before gate, genuine16x16 DSP products. */
uint32_t opencfw_em9305_command_scan_params_30b9f4(uint32_t first,uint32_t second,uint32_t interval,uint32_t duration)
{
 uintptr_t root=0x805a70u;
 uint32_t prior=*(volatile uint8_t *)(root+12u);
 *(volatile uint8_t *)(root+14u)=0u;
 *(volatile uint8_t *)(root+13u)=(uint8_t)prior;
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)goto gate_error;
 if(first==1u){
  if(second>=3u)goto argument_error;
  if(second==2u&&(interval==0u||duration==0u))goto argument_error;
 }
 uint32_t interval_ticks,duration_ticks;
 interval_ticks=(uint16_t)interval*10u; /* Host-only ISA arithmetic normalization. */
 duration_ticks=(uint16_t)duration*1280u; /* Host-only ISA arithmetic normalization. */
 if(interval!=0u&&first==1u&&duration!=0u&&interval_ticks>=duration_ticks)goto argument_error;
 if(opencfw_em9305_scan_available_307b9c()==0u)goto argument_error;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(16u);
 if(message==0u)return 0u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint32_t *)(message+12u)=duration_ticks;
 *(volatile uint32_t *)(message+8u)=interval_ticks;
 *(volatile uint8_t *)(message+4u)=(uint8_t)second;
 *(volatile uint8_t *)(message+3u)=(uint8_t)((first==0u)+1u);
 *(volatile uint8_t *)(message+2u)=7u;
 return opencfw_em9305_wsf_task_message_send(handler,message);
 gate_error:
 *(volatile uint8_t *)(root+13u)=1u;return opencfw_em9305_scan_error_30e7f8(12u);
 argument_error:
 *(volatile uint8_t *)(root+13u)=1u;return opencfw_em9305_scan_error_30e7f8(18u);
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uint32_t firsts[]={0,1,2,0xffffffff},seconds[]={0,1,2,3,255,0xffffffff},values[]={0,1,5,65535,65536,0xffffffff};unsigned cases=0;
for(unsigned a=0;a<4;a++)for(unsigned b=0;b<6;b++)for(unsigned c=0;c<6;c++)for(unsigned d=0;d<6;d++)for(unsigned mode=0;mode<8;mode++){
 uint32_t first=firsts[a],second=seconds[b],interval=values[c],duration=values[d];gate=mode&1;available=(mode>>1)&1;fail=(mode>>2)&1;allocs=sends=errors=available_calls=0;status_seen=0;*(uint8_t *)0x805a7c=7;*(uint8_t *)0x805a7d=0xa5;*(uint8_t *)0x805a7e=0xa5;memset(message,0xa5,16);uint32_t it=(interval&65535)*10,dt=(duration&65535)*1280;unsigned bad=first==1&&(second>=3||(second==2&&(!interval||!duration))||(interval&&duration&&it>=dt));unsigned admitted=gate&&!bad&&available;unsigned expected=!gate||bad||!available?55:fail?0:67;assert(opencfw_em9305_command_scan_params_30b9f4(first,second,interval,duration)==expected);assert(available_calls==(gate&&!bad)&&allocs==admitted&&sends==(admitted&&!fail)&&errors==(!gate||bad||!available));if(errors)assert(status_seen==(gate?18:12));assert(*(uint8_t *)0x805a7c==7&&*(uint8_t *)0x805a7e==0&&*(uint8_t *)0x805a7d==(errors?1:7));if(sends){assert(*(uint32_t *)(message+8)==it&&*(uint32_t *)(message+12)==dt&&message[2]==7&&message[3]==(first==0?2:1)&&message[4]==(uint8_t)second);assert(message[0]==0xa5&&message[1]==0xa5&&message[5]==0xa5&&message[6]==0xa5&&message[7]==0xa5);}cases++;
}
printf("PASS %u\n",cases);}
