#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned queues,empty_b=1,empty_a=1;
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t q){if(q!=0x805000+360&&q!=0x804000+360)abort();queues++;return q==0x805000+360?empty_b:empty_a;}
#include "init-schedule-compare-prepared.c"
static void defaults(void){memset((void*)0x800000,0,0x10000);queues=0;empty_a=empty_b=1;*(uint8_t*)(0x802000+26)=1;*(uint32_t*)(0x802000+44)=0x803000;*(uint8_t*)0x803000=4;*(uint32_t*)(0x801000+36)=0x804000;*(uint32_t*)(0x802000+36)=0x805000;*(uint8_t*)0x804001=1;*(uint16_t*)(0x804000+266)=4;*(uint16_t*)(0x805000+266)=4;*(uint32_t*)(0x804000+392)=1;*(uint32_t*)(0x805000+392)=1;*(uint8_t*)(0x804000+635)=255;*(uint8_t*)(0x805000+635)=255;}
static void check(unsigned second,unsigned expected_queues){uint32_t r=opencfw_em9305_init_schedule_compare_318b78(0x801000,0x802000);if(r!=(second?0x802000u:0x801000u)||queues!=expected_queues)abort();}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
 defaults();*(uint8_t*)(0x802000+26)=2;check(0,0);cases++;
 defaults();*(uint8_t*)0x803000=6;check(0,0);cases++;
 defaults();*(uint8_t*)0x804001=0;check(1,0);cases++;
 defaults();*(uint8_t*)(0x805000+401)=1;check(1,0);cases++;
 defaults();*(uint32_t*)(0x805000+392)=0;check(1,0);cases++;
 defaults();*(uint8_t*)(0x804000+401)=1;check(0,0);cases++;
 defaults();*(uint32_t*)(0x804000+392)=0;check(0,0);cases++;
 defaults();*(uint8_t*)(0x805000+635)=0;check(1,0);cases++;
 defaults();*(uint8_t*)(0x804000+635)=0;check(0,0);cases++;
 defaults();empty_b=0;check(1,1);cases++;
 defaults();empty_a=0;check(0,2);cases++;
 defaults();check(1,2);cases++;
 defaults();*(uint16_t*)(0x804000+266)=1;*(uint16_t*)(0x805000+266)=8;*(uint32_t*)(0x805000+392)=2;check(1,2);cases++;
 defaults();*(uint16_t*)(0x804000+266)=20;*(uint16_t*)(0x805000+266)=4;*(uint32_t*)(0x804000+392)=5;check(0,2);cases++;
 defaults();*(uint32_t*)(0x805000+392)=0x80000000u;check(1,0);cases++;
 defaults();*(uint32_t*)(0x805000+392)=0xffffffffu;check(1,2);cases++;
 printf("PASS %u isolated native-branch comparator cases\n",cases);return 0;}
