#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocfail,allocs,posts,notifies;
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=4)abort();allocs++;return allocfail?0:0x809000;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){if(h!=9||m!=0x809000||*(uint16_t*)m!=0xa5a5||*(uint8_t*)(m+2)!=23||*(uint8_t*)(m+3)!=5)abort();posts++;return 71;}
static uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t o){if(o!=0x806030||*(uint8_t*)0x806003!=1)abort();notifies++;return 72;}
#include "init-secondary-schedule-action-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
for(unsigned notify=0;notify<256;notify++)for(unsigned mark=0;mark<2;mark++)for(allocfail=0;allocfail<2;allocfail++){
memset((void*)0x800000,0,0x10000);memset((void*)0x809000,0xa5,4);allocs=posts=notifies=0;*(uint32_t*)0x8051b8=0x806000;*(uint8_t*)0x8051a5=notify;*(uint8_t*)(0x806000+603)=mark;*(uint8_t*)0x806004=7;*(uint8_t*)0x806009=23;*(uint8_t*)0x805b18=9;
uint32_t result=opencfw_em9305_init_secondary_action_318fc0(0,0,0);
if(result!=(notify?72u:allocfail?0u:71u)||allocs!=!notify||posts!=(!notify&&!allocfail)||notifies!=!!notify||*(uint8_t*)0x806004!=(mark?7:1)||*(uint8_t*)0x806003!=!!notify)abort();
cases++;
}
printf("PASS %u isolated secondary schedule cases\n",cases);return 0;}
