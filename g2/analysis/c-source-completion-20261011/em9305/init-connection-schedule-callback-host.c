#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,failures,finishes;static uint32_t period;
static uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t a,uintptr_t b){return (uint32_t)a+(uint32_t)b;}
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,uintptr_t compare){if(object!=0x806000+912+16||compare!=(uintptr_t)opencfw_em9305_init_schedule_compare_318b78)abort();if(calls&&*(uint32_t*)(0x806000+912+24)!=123u+calls*period*1250u)abort();calls++;return calls>failures;}
static uint32_t opencfw_em9305_init_schedule_finish_31ec40(uintptr_t object){if(object!=0x804000||*(uint32_t*)(object+36)!=0x803b94)abort();finishes++;return 77;}
#include "init-connection-schedule-callback-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;uint32_t periods[]={0,1,65535};
 for(unsigned enabled=0;enabled<2;enabled++)for(failures=0;failures<5;failures++)for(unsigned p=0;p<3;p++){
 memset((void*)0x800000,0,0x10000);calls=finishes=0;period=periods[p];*(uint8_t*)0x803c28=enabled;*(uint16_t*)0x803c0c=1;*(uint32_t*)0x805c70=0x806000;*(uint32_t*)(0x806000+912+24)=123;*(uint16_t*)(0x806000+912+266)=period;*(uint16_t*)(0x806000+912+262)=65535;
 if(opencfw_em9305_init_callback_320908(0x804000,0)!=77||finishes!=1||calls!=(enabled?failures+1:0)||*(uint16_t*)(0x806000+912+262)!=(uint16_t)(65535+(enabled?failures:0)))abort();
 cases++;
 }
 printf("PASS %u isolated schedule callback cases\n",cases);return 0;}
