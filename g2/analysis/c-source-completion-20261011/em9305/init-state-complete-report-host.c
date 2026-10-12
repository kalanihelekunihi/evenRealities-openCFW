#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned fail,posted,common,clean,trigger;static uint8_t output[88];
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=88)abort();memset((void *)0x807000,0xa5,88);return fail?0:0x807000;}
static void *opencfw_em9305_memcpy(void*d,const void*s,uint32_t n){return memcpy(d,s,n);}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){if(h!=23||m!=0x807000)abort();memcpy(output,(void*)m,88);posted++;return 91;}
static uint32_t opencfw_em9305_common_release_304588(uint32_t n){if(n!=1)abort();common++;return 92;}
static uint32_t opencfw_em9305_init_state_cleanup_325740(uintptr_t r){if(r!=0x803b94)abort();clean++;return 93;}
static uint32_t opencfw_em9305_init_state_action_31b6b0(uintptr_t a,uint32_t b){if(a||b)abort();trigger++;return 94;}
#include "init-state-complete-report-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
 for(unsigned mode=0;mode<8;mode++)for(unsigned id=0;id<256;id++){
  memset((void*)0x800000,0,0x10000);posted=common=clean=trigger=0;fail=0;
  *(uint8_t*)0x805a74=1;*(uint32_t*)0x805c70=0x806000;*(uint8_t*)0x805b18=23;
  for(unsigned i=0;i<44;i++)((uint8_t*)0x803bd8)[i]=(uint8_t)(i+id);
  *(uint16_t*)0x803c0c=(uint16_t)(id%4);*(uint8_t*)(uintptr_t)(0x806002+(id%4)*912)=1;
  uint32_t lo=0x12345678+id,hi=0xabcdef00+id,lo2=lo+(mode&1),hi2=hi+((mode>>1)&1);
  *(uint32_t*)0x803d04=lo;*(uint32_t*)0x803d08=hi;*(uint32_t*)0x803d0c=lo2;*(uint32_t*)0x803d10=hi2;
  *(uint8_t*)0x803d16=5;*(uint8_t*)0x803d17=(uint8_t)(5+((mode>>2)&1));
  *(uint32_t*)0x803c04=0x87654321;*(uint32_t*)0x803c08=0x10203040;*(uint8_t*)0x803c11=0x62;
  uint8_t expected[88];memset(expected,0xa5,88);uint16_t v=(uint16_t)(id%4);memcpy(expected,&v,2);v=0x3f01;memcpy(expected+2,&v,2);memcpy(expected+4,(void*)0x803bd8,44);
  expected[52]=(uint8_t)(5+((mode>>2)&1));if(mode)expected[52]|=2;expected[53]=0x62;expected[54]=1;
  memcpy(expected+60,&lo2,4);memcpy(expected+64,&hi2,4);uint32_t a=mode?lo:0,b=mode?hi:0;memcpy(expected+68,&a,4);memcpy(expected+72,&b,4);
  a=0x87654321;b=0x10203040;memcpy(expected+76,&a,4);memcpy(expected+80,&b,4);expected[84]=expected[86]=expected[87]=255;
  if(opencfw_em9305_init_state_action_31b3b8(0,0)!=93||posted!=1||common!=1||clean!=1||trigger||memcmp(output,expected,88)||*(uint8_t*)(uintptr_t)(0x806002+(id%4)*912))abort();
  cases++;
 }
 fail=1;posted=common=clean=trigger=0;if(opencfw_em9305_init_state_action_31b3b8(0,0)!=93||posted||common!=1||clean!=1)abort();cases++;
 *(uint8_t*)0x805a74=0;posted=common=clean=trigger=0;if(opencfw_em9305_init_state_action_31b3b8(0,0)!=94||trigger!=1||posted||common||clean)abort();cases++;
 printf("PASS %u isolated state report cases\n",cases);return 0;}
