#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned notifications,disarms,transitions;
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){return 5;}
static uint32_t opencfw_em9305_pal_timer_disarm(void){disarms++;return 0;}
static uint32_t opencfw_em9305_auxiliary_transition_333a60(void){transitions++;return 0;}
static uintptr_t opencfw_em9305_auxiliary_unlink_333804(uintptr_t n){uintptr_t prev=*(uint32_t *)n,next=*(uint32_t *)(n+4);*(uint32_t *)(prev+4)=(uint32_t)next;if(next)*(uint32_t *)next=(uint32_t)prev;else *(uint32_t *)(uintptr_t)0x805f18=(uint32_t)prev;return n;}
static uint32_t notify(uintptr_t n,uintptr_t self){if(self!=(uintptr_t)notify||n<0x802000||n>=0x802400)abort();notifications++;return 0;}
#include "associated-schedule-insert-prepared.c"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uintptr_t root=0x805f04,incoming=0x803000;unsigned cases=0;
 for(unsigned count=0;count<=6;count++)for(unsigned time=0;time<7000;time+=250)for(unsigned width=100;width<=3100;width+=1000)for(unsigned state=0;state<=2;state++)for(unsigned priority=1;priority<=3;priority+=2){
  memset((void *)0x802000,0,4096);memset((void *)root,0,64);notifications=disarms=transitions=0;
  *(uint8_t *)root=(uint8_t)state;
  for(unsigned i=0;i<count;i++){
   uintptr_t n=0x802000+i*64;*(uint32_t *)n=i?(uint32_t)(n-64):0;*(uint32_t *)(n+4)=i+1<count?(uint32_t)(n+64):0;
   *(uint32_t *)(n+8)=1000+i*1000;*(uint32_t *)(n+12)=100;*(uint8_t *)(n+24)=2;*(uint32_t *)(n+32)=(uint32_t)(uintptr_t)notify;
  }
  *(uint32_t *)(root+16)=count?0x802000:0;*(uint32_t *)(root+20)=count?(uint32_t)(0x802000+(count-1)*64):0;
  *(uint32_t *)(incoming+8)=time;*(uint32_t *)(incoming+12)=width;*(uint8_t *)(incoming+24)=(uint8_t)priority;
  unsigned overlaps=0;for(unsigned i=0;i<count;i++)if(time<1105+i*1000&&1000+i*1000<time+width+5)overlaps++;
  unsigned rejected=(count&&state==2&&time<1105)||(overlaps&&priority==3);
  uint32_t result=opencfw_em9305_associated_schedule_insert_312da4(incoming,0);
  if(result!=!rejected||notifications!=(rejected?0:overlaps))abort();
  uintptr_t cur=*(uint32_t *)(root+16),prev=0;unsigned nodes=0,seen=0;
  while(cur){if(*(uint32_t *)cur!=prev)abort();seen+=cur==incoming;prev=cur;cur=*(uint32_t *)(cur+4);if(++nodes>8)abort();}
  if(prev!=*(uint32_t *)(root+20)||seen!=!rejected||nodes!=count+(rejected?0:1-overlaps))abort();
  unsigned head=*(uint32_t *)(root+16)==incoming;
  if(disarms!=head||transitions!=head)abort();
  cases++;
 }
 printf("PASS %u controlled scheduler-list cases; ARC runtime unqualified\n",cases);
}
