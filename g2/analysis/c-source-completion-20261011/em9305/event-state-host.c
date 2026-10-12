#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern void *opencfw_em9305_memset(void*,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_command_stop_30b654(uintptr_t);
extern uint32_t opencfw_em9305_common_init_303d2c(uint32_t);
uint32_t opencfw_em9305_event_reset_332cc0(uint32_t incoming)
{(void)incoming;return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x8058dcu,0u,404u);}
/* Native332c84..332cbc retains path-specific R0, including state before write4. */
uint32_t opencfw_em9305_event_mode_332c84(uintptr_t event)
{
 uint32_t operation=*(volatile uint8_t *)(event+3u);
 if(operation==1u){
  *(volatile uint8_t *)(uintptr_t)0x805a78u=0u;
  *(volatile uint8_t *)(uintptr_t)0x8058dcu=0u;
  return opencfw_em9305_command_count_down_30e48c();
 }
 if(operation!=0u)return 0x805a70u;
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805a78u;
 if(enabled==0u)return 0u;
 (void)opencfw_em9305_command_stop_30b654(0u);
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x8058dcu;
 if(state==3u)*(volatile uint8_t *)(uintptr_t)0x8058dcu=4u;
 return state;
}
/* Native30e0e8..30e11c: clear404, callback registration, actual common-init. */
uint32_t opencfw_em9305_init_event_state_30e0e8(uint32_t incoming)
{
 (void)incoming;(void)opencfw_em9305_memset((void *)(uintptr_t)0x8058dcu,0u,404u);
 *(volatile uint32_t *)(uintptr_t)0x805210u=(uint32_t)(uintptr_t)opencfw_em9305_event_reset_332cc0;
 *(volatile uint32_t *)(uintptr_t)0x802964u=(uint32_t)(uintptr_t)opencfw_em9305_event_mode_332c84;
 return opencfw_em9305_common_init_303d2c(0x802964u);
}

static unsigned calls,nextstate,clears,inits;
void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){if(p!=(void*)0x8058dc||v||n!=404)abort();clears++;return memset(p,v,n);}
uint32_t opencfw_em9305_command_count_down_30e48c(void){calls++;if(*(volatile uint8_t*)0x8058dc||*(volatile uint8_t*)0x805a78)abort();return 827;}
uint32_t opencfw_em9305_command_stop_30b654(uintptr_t p){if(p)abort();calls++;*(volatile uint8_t*)0x8058dc=nextstate;return 923;}
uint32_t opencfw_em9305_common_init_303d2c(uint32_t p){if(p!=0x802964)abort();inits++;for(unsigned i=0;i<404;i++)if(*(volatile uint8_t*)(uintptr_t)(0x8058dc+i))abort();return 845;}
int main(void){
 if(mmap((void*)0x800000,0x7000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t event[4];unsigned cases=0;
 for(unsigned op=0;op<256;op++)for(unsigned enabled=0;enabled<2;enabled++)for(nextstate=0;nextstate<256;nextstate++){
 event[3]=op;*(volatile uint8_t*)0x8058dc=31;*(volatile uint8_t*)0x805a78=enabled;calls=0;
 unsigned expected=op==1?827:op!=0?0x805a70:enabled?nextstate:0;
 unsigned state=op==1?0:op==0&&enabled?(nextstate==3?4:nextstate):31;
 if(opencfw_em9305_event_mode_332c84((uintptr_t)event)!=expected||*(volatile uint8_t*)0x8058dc!=state||calls!=(op==1||(op==0&&enabled)))abort();
 cases++;
 }
 for(unsigned seed=0;seed<256;seed++){
 memset((void*)0x8058dc,seed,404);*(volatile uint8_t*)0x8058db=91;*(volatile uint8_t*)0x805a70=19;clears=inits=0;
 if(opencfw_em9305_init_event_state_30e0e8(seed)!=845||clears!=1||inits!=1||*(volatile uint8_t*)0x8058db!=91||*(volatile uint8_t*)0x805a70!=19||*(volatile uint32_t*)0x805210!=(uint32_t)(uintptr_t)opencfw_em9305_event_reset_332cc0||*(volatile uint32_t*)0x802964!=(uint32_t)(uintptr_t)opencfw_em9305_event_mode_332c84)abort();
 memset((void*)0x8058dc,seed,404);if(opencfw_em9305_event_reset_332cc0(seed)!=0x8058dc||clears!=2)abort();
 cases++;
 }
 printf("PASS %u event-mode/reset cases\n",cases);return 0;
}
