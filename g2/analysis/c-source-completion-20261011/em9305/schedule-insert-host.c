#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned guards,transitions;
static uint32_t opencfw_em9305_pal_current_time(void){return 100;}
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){guards++;return 1;}
static uint32_t opencfw_em9305_auxiliary_transition_333a60(void){transitions++;return 17;}
/* Native schedule313220..3132f8; source-owned time and guard providers.
 * Signed native CMP.N is the sign bit of wrapping32-bit subtraction. */
uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t object)
{
 uintptr_t root=0x805f04u,queue=root+16u;
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uintptr_t head=*(volatile uint32_t *)queue;
 *(volatile uint32_t *)(object+8u)=guard+now;
 if(head==0u){
  *(volatile uint32_t *)(queue+4u)=(uint32_t)object;
  *(volatile uint32_t *)queue=(uint32_t)object;
  *(volatile uint32_t *)(object+4u)=0u;
  *(volatile uint32_t *)object=0u;
  goto done;
 }
 uint32_t width=*(volatile uint32_t *)(object+12u);
 uint32_t head_time=*(volatile uint32_t *)(head+8u);
 guard=opencfw_em9305_auxiliary_guard_interval();
 width+=guard;
 uint32_t edge=guard+width;
 if(((head_time-edge)&0x80000000u)==0u&&*(volatile uint8_t *)root!=2u){
  head=*(volatile uint32_t *)queue;
  uintptr_t prior=*(volatile uint32_t *)head;
  *(volatile uint32_t *)object=(uint32_t)prior;
  *(volatile uint32_t *)head=(uint32_t)object;
  prior=*(volatile uint32_t *)object;
  *(volatile uint32_t *)(object+4u)=(uint32_t)head;
  if(prior!=0u)*(volatile uint32_t *)(prior+4u)=(uint32_t)object;
  else *(volatile uint32_t *)queue=(uint32_t)object;
  goto done;
 }
 uintptr_t link=queue,current;
 for(;;){
  current=*(volatile uint32_t *)link;
  head=*(volatile uint32_t *)queue;
  uint32_t end;
  if(current==head){
   end=*(volatile uint32_t *)(current+16u);
   if(end!=0u)end+=*(volatile uint32_t *)(current+8u);
   else {
    uint32_t start=*(volatile uint32_t *)(current+8u);
    end=*(volatile uint32_t *)(current+12u)+start;
   }
  }else{
   uint32_t start=*(volatile uint32_t *)(current+8u);
   end=*(volatile uint32_t *)(current+12u)+start;
  }
  guard=opencfw_em9305_auxiliary_guard_interval();
  uintptr_t next=*(volatile uint32_t *)(current+4u);
  uint32_t time=guard+end;
  *(volatile uint32_t *)(object+8u)=time;
  uintptr_t after=0u;
  if(next!=0u){
   uint32_t needed=*(volatile uint32_t *)(object+12u);
   uint32_t next_time=*(volatile uint32_t *)(next+8u);
   link=current+4u;
   uint32_t sum=time+needed;
   guard=opencfw_em9305_auxiliary_guard_interval();
   sum+=guard;
   if(((next_time-sum)&0x80000000u)!=0u)continue;
   after=*(volatile uint32_t *)link;
  }
  *(volatile uint32_t *)(object+4u)=(uint32_t)after;
  *(volatile uint32_t *)(current+4u)=(uint32_t)object;
  after=*(volatile uint32_t *)(object+4u);
  *(volatile uint32_t *)object=(uint32_t)current;
  if(after!=0u)*(volatile uint32_t *)after=(uint32_t)object;
  else *(volatile uint32_t *)(root+20u)=(uint32_t)object;
  break;
 }
 done:
 head=*(volatile uint32_t *)queue;
 if(head==object)return opencfw_em9305_auxiliary_transition_333a60();
 return (uint32_t)head;
}


static void put(uintptr_t p,unsigned off,uint32_t v){*(uint32_t *)(p+off)=v;}
static uint32_t get(uintptr_t p,unsigned off){return *(uint32_t *)(p+off);}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t root=0x805f04,head=0x820000,next=0x830000,object=0x840000;unsigned cases=0;
for(unsigned mode=0;mode<2;mode++)for(unsigned special=0;special<2;special++)for(unsigned gap=0;gap<2;gap++){memset((void *)root,0,32);memset((void *)head,0,32);memset((void *)next,0,32);memset((void *)object,0xa5,32);*(uint8_t *)root=mode?2:1;put(root,16,head);put(root,20,next);put(head,0,0);put(head,4,next);put(head,8,0);put(head,12,10);put(head,16,special?4:0);put(next,0,head);put(next,4,0);put(next,8,gap?100:15);put(next,12,10);put(object,12,5);guards=transitions=0;assert(opencfw_em9305_auxiliary_insert_313220(object)==head&&!transitions);unsigned between=gap||(special&&!gap);if(between){assert(get(head,4)==object&&get(object,0)==head&&get(object,4)==next&&get(next,0)==object&&get(root,20)==next&&get(object,8)==(special?5:11)&&guards==4);}else{assert(get(head,4)==next&&get(next,4)==object&&get(object,0)==next&&get(object,4)==0&&get(root,20)==object&&get(object,8)==26&&guards==5);}cases++;}
for(unsigned mode=0;mode<2;mode++){memset((void *)root,0,32);memset((void *)head,0,32);memset((void *)object,0xa5,32);*(uint8_t *)root=mode?2:1;put(root,16,head);put(root,20,head);put(head,8,100);put(head,12,10);put(object,12,5);guards=transitions=0;unsigned result=opencfw_em9305_auxiliary_insert_313220(object);if(!mode){assert(result==17&&transitions==1&&guards==2&&get(root,16)==object&&get(root,20)==head&&get(object,0)==0&&get(object,4)==head&&get(head,0)==object&&get(object,8)==101);}else{assert(result==head&&!transitions&&guards==3&&get(root,16)==head&&get(root,20)==object&&get(object,0)==head&&get(object,4)==0&&get(object,8)==111);}cases++;}
memset((void *)root,0,32);memset((void *)object,0xa5,32);guards=transitions=0;assert(opencfw_em9305_auxiliary_insert_313220(object)==17&&transitions==1&&guards==1&&get(root,16)==object&&get(root,20)==object&&get(object,0)==0&&get(object,4)==0&&get(object,8)==101);cases++;
printf("PASS %u\n",cases);}
