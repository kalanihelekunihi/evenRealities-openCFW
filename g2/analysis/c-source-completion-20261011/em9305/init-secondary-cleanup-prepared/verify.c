#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_secondary_cleanup_321450(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_action_3190e0(uintptr_t,uint32_t,uint32_t);
static unsigned callback_calls,release_calls,event_calls,send_calls;static uint32_t expected_slot,last_code,last_handler;static uintptr_t current,allocated;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,(int)v,n);}
uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==1);return 91;}
uint32_t opencfw_em9305_command_count_down_30e48c(void){(*(uint8_t *)0x805a79u)--;return 0x805a79u;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==0x80a000u);release_calls++;return 97;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==24);return allocated;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(p==allocated);send_calls++;last_handler=h;return 98;}
uint32_t opencfw_em9305_init_secondary_event_30e928(uint32_t code,uint32_t slot,uint8_t *p,uint32_t flag){assert(slot==expected_slot&&flag==5);for(unsigned j=0;j<18;j++)assert(p[j]==0);event_calls++;last_code=code;return 99;}
static uint32_t callback(uint32_t a,uint32_t b,uintptr_t self){assert(a==expected_slot&&b==expected_slot&&self==(uintptr_t)callback);callback_calls++;return 101;}
int main(void){
 assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);unsigned cases=0;
 for(unsigned slot=0;slot<6;slot++)for(unsigned count=0;count<256;count++)for(unsigned flags=0;flags<8;flags++){
  expected_slot=slot;current=0x803d78u+784*slot;memset((void *)current,0,784);*(uint8_t *)current=1;
  *(uint32_t *)(current+12)=(flags&1)?(uint32_t)(uintptr_t)callback:0;*(uint8_t *)(current+624)=(uint8_t)(flags&2);
  *(uint32_t *)(current+604)=(flags&4)?0x80a000u:0;*(uint8_t *)0x805a77u=(uint8_t)count;*(uint8_t *)0x805a79u=(uint8_t)count;
  unsigned c=callback_calls,r=release_calls;assert(opencfw_em9305_init_secondary_cleanup_321450(current)==((flags&4)?97u:0u));
  assert(callback_calls==c+!!(flags&1)&&release_calls==r+!!(flags&4)&&*(uint8_t *)current==0);
  assert(*(uint8_t *)0x805a77u==(uint8_t)(count-!!(flags&2))&&*(uint8_t *)0x805a79u==(uint8_t)(count-1));cases++;
 }
 expected_slot=2;current=0x803d78u+2*784;
 for(unsigned flags=0;flags<16;flags++){
  memset((void *)current,0,784);memset((void *)0x8051a4u,0,24);*(uint32_t *)0x8051b8u=(uint32_t)current;*(uint8_t *)0x8051a5u=1;
  *(uint8_t *)(current+4)=(uint8_t)(flags&1);*(uint8_t *)(current+603)=(uint8_t)(flags&2);*(uint8_t *)(current+777)=5;
  *(uint8_t *)0x8051a8u=(uint8_t)!!(flags&4);allocated=(flags&8)?0x80b000u:0;memset((void *)0x80b000u,0xa5,24);
  *(uint32_t *)0x8051b0u=0x12345678;*(uint32_t *)0x8051acu=0x87654321;
  *(uint8_t *)0x8051aau=6;*(uint8_t *)0x8051a9u=7;*(uint8_t *)0x8051b4u=8;*(uint8_t *)0x805b18u=9;
  *(uint8_t *)(current+6)=10;*(uint32_t *)(current+620)=0x12345678;*(uint16_t *)(current+616)=0xabcd;
  unsigned e=event_calls,s=send_calls;assert(opencfw_em9305_init_secondary_action_3190e0(1,2,3)==((flags&2)?(uint32_t)(current+603):0));
  assert(event_calls==e+!!(flags&1)+((flags&2)&&!(flags&4)));assert(send_calls==s+((flags&2)&&(flags&4)&&(flags&8)));
  assert(*(uint8_t *)(current+603)==0&&*(uint8_t *)0x8051a5u==0);
  if(send_calls!=s){assert(last_handler==9&&*(uint16_t *)0x80b002u==267&&*(uint8_t *)0x80b005u==10&&*(uint16_t *)0x80b010u==0xabcd&&*(uint16_t *)0x80b012u==0x5678&&*(uint8_t *)0x80b015u==8);}
  cases++;
 }
 printf("PASS %u cleanup/state contract cases\n",cases);return 0;
}
