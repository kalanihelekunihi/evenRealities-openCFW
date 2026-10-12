#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned failure,mutate,starts,counts;static uintptr_t started;
static uint32_t opencfw_em9305_common_request_30455c(uint32_t n){if(n!=1)abort();*(uint32_t*)0x805c80=0x807100;return 8;}
static uint32_t opencfw_em9305_init_secondary_allocate_316e74(void){if(*(uint32_t*)0x8051ac!=11||*(uint32_t*)0x8051b0!=12||*(uint8_t*)0x8051a9!=5||*(uint8_t*)0x8051aa!=6||*(uint8_t*)0x8051b4!=7)abort();if(mutate){*(uint8_t*)0x807006=55;*(uint32_t*)0x807008=33;*(uint32_t*)0x80700c=44;*(uint32_t*)0x8051b8=0x804d00;}return failure?0:0x804c00;}
static uint32_t opencfw_em9305_init_secondary_start_3213f8(uintptr_t r){starts++;started=r;return 99;}
static uint32_t opencfw_em9305_command_count_30e4bc(void){counts++;return 71;}
#include "init-secondary-create-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
for(unsigned initial=0;initial<256;initial++)for(unsigned flag=0;flag<2;flag++)for(failure=0;failure<2;failure++)for(mutate=0;mutate<2;mutate++){
memset((void*)0x800000,0,0x10000);starts=counts=0;*(uint32_t*)0x805c80=0x807000;*(uint32_t*)0x8051b8=0x804b00;*(uint8_t*)0x805a77=initial;*(uint8_t*)0x807004=flag;*(uint8_t*)0x807005=255;*(uint8_t*)0x807006=5;*(uint8_t*)0x807007=6;*(uint32_t*)0x807008=11;*(uint32_t*)0x80700c=12;*(uint16_t*)0x807010=123;*(uint16_t*)0x807012=65535;*(uint8_t*)0x807014=255;*(uint8_t*)0x807015=7;
if(opencfw_em9305_init_secondary_action_318fe8(0,0,0)!=71||starts!=1||counts!=1||started!=(failure?(mutate?0x804d00u:0x804b00u):0x804c00u)||*(uint8_t*)0x805a77!=(uint8_t)(initial+flag))abort();
if(!failure){uintptr_t r=0x804c00;if(*(uint8_t*)(r+625)!=(mutate?55:5)||*(uint8_t*)(r+624)!=flag||*(uint8_t*)(r+626)!=6||*(uint8_t*)(r+9)!=11||*(uint16_t*)(r+616)!=123||*(uint32_t*)(r+632)!=(mutate?44u:12u)||*(uint32_t*)(r+628)!=(mutate?33u:11u)||*(uint8_t*)(r+6)!=1||*(uint8_t*)(r+7)!=1||*(uint32_t*)(r+620)!=655350)abort();}
cases++;
}
printf("PASS %u isolated creation action cases\n",cases);return 0;}
