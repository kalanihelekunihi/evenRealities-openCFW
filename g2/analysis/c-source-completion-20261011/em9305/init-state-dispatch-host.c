#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,old_state,fresh;
static void *opencfw_em9305_memset(void *d,uint32_t value,uint32_t length){return memset(d,value,length);}
#include "init-state-dispatch-prepared.c"
uint32_t opencfw_em9305_init_state_action_31b4e0(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b4e0||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
uint32_t opencfw_em9305_init_state_action_31b4a4(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b4a4||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
uint32_t opencfw_em9305_init_state_action_31b6b0(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b6b0||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
uint32_t opencfw_em9305_init_state_action_31b4c8(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b4c8||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
uint32_t opencfw_em9305_init_state_action_31b3b8(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b3b8||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
uint32_t opencfw_em9305_init_state_action_31b648(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b648||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
uint32_t opencfw_em9305_init_state_action_31b614(uintptr_t fn,uint32_t state){if(fn!=(uintptr_t)opencfw_em9305_init_state_action_31b614||state!=old_state)abort();calls++;*(uint8_t *)(uintptr_t)0x803bb8=fresh;return 99;}
int main(void){if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)0x800000)abort();unsigned cases=0;
 const uint8_t transitions[16]={0,1,0,0,3,1,2,0,3,2,2,0,3,3,3,0};
 const uint8_t exists[16]={0,1,1,0,1,1,1,1,0,1,0,1,0,1,1,1};
 for(old_state=0;old_state<4;old_state++)for(unsigned event=0;event<4;event++)for(fresh=0;fresh<4;fresh++){
  *(uint8_t *)(uintptr_t)0x803bb8=old_state;*(uint8_t *)(uintptr_t)0x804003=event;calls=0;
  unsigned expected=transitions[(exists[old_state*4+event]?fresh:old_state)*4+event];
  if(opencfw_em9305_init_state_event_320580(0x804000)!=expected||calls!=exists[old_state*4+event]||*(uint8_t *)(uintptr_t)0x803bb8!=expected)abort();
  cases++;
 }
 for(unsigned input=0;input<16;input++){
  memset((void *)0x803b90,0xa5,412);
  if(opencfw_em9305_init_lower_307bdc(input)!=0x803b94)abort();
  for(unsigned i=0;i<404;i++)if(*(uint8_t *)(uintptr_t)(0x803b94+i)!=0)abort();
  if(*(uint32_t *)(uintptr_t)0x803b90!=0xa5a5a5a5||*(uint32_t *)(uintptr_t)0x803d28!=0xa5a5a5a5)abort();
  if(*(uint32_t *)(uintptr_t)0x80295c!=(uint32_t)(uintptr_t)opencfw_em9305_init_state_event_320580||*(uint32_t *)(uintptr_t)0x805208!=(uint32_t)(uintptr_t)opencfw_em9305_init_state_reset_3205b4)abort();
  cases++;
 }
 printf("PASS %u isolated state/registration cases\n",cases);return 0;}
