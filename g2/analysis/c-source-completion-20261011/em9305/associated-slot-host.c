#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t guard, timers;
static uint32_t opencfw_em9305_config_link_divu_prior(uint32_t a,uint32_t b,uint32_t prior){return b?a/b:prior;}
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){return guard;}
static uint32_t opencfw_em9305_radio_primary_timer_333bec(uint32_t value){timers++;return value;}
#include "associated-slot-host-port.inc"
static uint32_t rng=0x6242;
static uint32_t random32(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static uint32_t reference_select(uint32_t lo,uint32_t hi,uint32_t step,uint32_t direction,uint32_t exclude){
 uint32_t q=(direction==1?hi:lo)/625u;
 if(step>625u)q/=step/625u;
 uint32_t edge=q*step;
 if(direction==1){if(edge<lo)edge=hi;}else if(edge<lo)edge+=step;
 uint32_t best=0;
 for(unsigned i=0;i<8;i++)if(i!=exclude){uint32_t v=((volatile uint32_t *)(uintptr_t)0x805f38)[i];if(v>=edge&&v<=hi&&v>=best)best=v;}
 return best?best:(edge<=hi?edge:hi);
}
static uint64_t reference_bitmap(uintptr_t head,uint32_t special,uint32_t q){
 uint64_t result=0;
 for(uintptr_t n=head;n;n=*(uint32_t *)(n+4)){
  uint32_t p=*(uint32_t *)(n+20);if(!p||(*(uint8_t *)(n+25)==1&&!special))continue;
  uint32_t begin=*(uint32_t *)(n+8)-*(uint32_t *)(head+8),end=begin+*(uint32_t *)(n+12);
  uint32_t b=q?begin/q:begin,e=q?end/q:end;if(e&224u)return result;
  uint32_t stride=(uint8_t)(q?p/q:p),reps=stride?(uint8_t)((32-(int)(uint8_t)b)/(int)stride+1):1;
  uint32_t width=(uint8_t)(e-b+1);
  for(unsigned k=0;k<reps;k++){
   b=(uint8_t)b;
   for(unsigned bit=0;bit<64;bit++)for(unsigned j=0;j<width;j++)if(((b+j)&63u)==bit)result|=UINT64_C(1)<<bit;
   b+=stride;
  }
 }
 return result;
}
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;
 for(unsigned i=0;i<65536;i++){
  uint32_t lo=random32(),hi=random32(),step=(i&1)?random32():625,direction=i%3,exclude=i%10;
  for(unsigned j=0;j<8;j++)((uint32_t *)(uintptr_t)0x805f38)[j]=random32();
  if(opencfw_em9305_associated_select_333948(lo,hi,step,direction,exclude)!=reference_select(lo,hi,step,direction,exclude))abort();
  cases++;
 }
 uintptr_t head=0x802000;
 for(unsigned i=0;i<65536;i++){
  uint32_t q=(i%7)?625u:0u;*(uint32_t *)(uintptr_t)0x805f2c=q;
  memset((void *)head,0,128);
  for(unsigned j=0;j<3;j++){
   uintptr_t n=head+j*32;*(uint32_t *)(n+4)=j<2?(uint32_t)(n+32):0;
   *(uint32_t *)(n+8)=random32()%25000;*(uint32_t *)(n+12)=random32()%2500;
   *(uint32_t *)(n+20)=random32()%25000;*(uint8_t *)(n+25)=j&1;
  }
  uint32_t special=i&1;
  if(opencfw_em9305_associated_bitmap_3336d8(head,special)!=reference_bitmap(head,special,q))abort();
  cases++;
 }
 for(unsigned id=0;id<8;id++)for(unsigned count=0;count<256;count++){
  memset((void *)0x805f28,0,160);*(uint8_t *)(uintptr_t)0x805f28=(uint8_t)count;
  *(uint32_t *)(uintptr_t)0x805f2c=625;*(uint32_t *)(uintptr_t)0x805f14=0;
  guard=0;timers=0;uint32_t out=0xdeadbeef;
  uint32_t success=opencfw_em9305_associated_slot_allocate_3133b4(id,1,625,1250,1,(uintptr_t)&out,0x1234);
  if(!success||out!=1250||timers!=1||*(uint8_t *)(uintptr_t)0x805f28!=(uint8_t)(count+1))abort();
  cases++;
 }
 printf("PASS %u controlled source-model cases; native execution unqualified\n",cases);
}
