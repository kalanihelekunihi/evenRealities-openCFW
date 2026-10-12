#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t elapsed,guardvalue;static unsigned transitions,times;
static uint32_t opencfw_em9305_pal_current_time(void){times++;return 100;}
static uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b){if(b!=125)abort();(void)a;return elapsed;}
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){return guardvalue;}
static uint32_t opencfw_em9305_auxiliary_transition_333a60(void){transitions++;return 7;}
#include "init-schedule-adjust-prepared.c"
#define W(a) (*(uint32_t*)(uintptr_t)(a))
static void reset(void){memset((void*)0x800000,0,0x10000);elapsed=1;guardvalue=5;transitions=times=0;W(0x806008)=200;W(0x80600c)=20;}
static void nodes(uint32_t a,uint32_t b){W(0x805f14)=0x807000;W(0x805f18)=b?0x807100:0x807000;W(0x807008)=a;if(b){W(0x807004)=0x807100;W(0x807100)=0x807000;W(0x807108)=b;}}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
/* Empty insertion, zero/overflow minimum and wrapped timestamp. */
uint32_t mins[]={0,1,65535,0xffffffff};for(unsigned j=0;j<4;j++){reset();if(opencfw_em9305_init_schedule_adjust_312f88(0x806000,mins[j],0)!=1||W(0x805f14)!=0x806000||W(0x805f18)!=0x806000||W(0x806000)||W(0x806004)||W(0x806008)!=200+mins[j]||transitions!=1)abort();cases++;}
/* Time gate restores original, negative maximum reanchors to now+guard. */
reset();elapsed=0;if(opencfw_em9305_init_schedule_adjust_312f88(0x806000,10,99)||W(0x806008)!=200||W(0x805f14)||times!=1)abort();cases++;
reset();elapsed=0;if(!opencfw_em9305_init_schedule_adjust_312f88(0x806000,10,0x80000000)||W(0x806008)!=105||times!=2)abort();cases++;
/* Before head and after tail maintain both inverse link directions. */
reset();nodes(300,0);if(!opencfw_em9305_init_schedule_adjust_312f88(0x806000,0,100)||W(0x805f14)!=0x806000||W(0x806004)!=0x807000||W(0x807000)!=0x806000||transitions!=1)abort();cases++;
reset();nodes(100,0);if(!opencfw_em9305_init_schedule_adjust_312f88(0x806000,0,100)||W(0x805f18)!=0x806000||W(0x806000)!=0x807000||W(0x807004)!=0x806000||transitions)abort();cases++;
/* Between head and tail. Native final BP tests next timestamp minus duration+2guard. */
reset();nodes(100,300);if(!opencfw_em9305_init_schedule_adjust_312f88(0x806000,0,100)||W(0x806000)!=0x807000||W(0x806004)!=0x807100||W(0x807004)!=0x806000||W(0x807100)!=0x806000||transitions)abort();cases++;
/* Mode2 prevents early head insertion; traversal exhausts budget and restores time. */
reset();nodes(300,400);*(uint8_t*)0x805f04=2;if(opencfw_em9305_init_schedule_adjust_312f88(0x806000,0,10)||W(0x806008)!=200||W(0x805f14)!=0x807000||W(0x805f18)!=0x807100||transitions)abort();cases++;
/* N flag uses wrapped subtraction, including arithmetic overflow. */
reset();W(0x806008)=0x7ffffff0;nodes(0x80000010,0);if(!opencfw_em9305_init_schedule_adjust_312f88(0x806000,0,100)||W(0x805f14)!=0x806000)abort();cases++;
printf("PASS %u isolated adjustment/list cases\n",cases);return 0;}
