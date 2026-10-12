#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
/* Native completion332cd0..332d2c: event0 sign-extends R2 into total64;
 * counters are loaded before ordered stores, limit uses fresh halfword reads. */
uint32_t opencfw_em9305_command_callback_332cd0(uintptr_t unused,uint32_t event,uint32_t delta)
{
 (void)unused;
 uintptr_t state=0x8058dcu;
 if(event==0u){
  uint32_t low=*(volatile uint32_t *)(state+12u);
  uint32_t high=*(volatile uint32_t *)(state+16u);
  uint32_t successful=*(volatile uint16_t *)(state+6u);
  uint32_t total=*(volatile uint16_t *)(state+20u);
  uint32_t next=low+delta;
  uint32_t upper=high+((delta&0x80000000u)!=0u?0xffffffffu:0u)+(next<low);
  *(volatile uint32_t *)(state+12u)=next;
  *(volatile uint16_t *)(state+6u)=(uint16_t)(successful+1u);
  *(volatile uint16_t *)(state+20u)=(uint16_t)(total+1u);
  *(volatile uint32_t *)(state+16u)=upper;
 }else if(event==4u){
  uint32_t count=*(volatile uint16_t *)(state+8u);
  *(volatile uint16_t *)(state+8u)=(uint16_t)(count+1u);
 }else{
  uint32_t count=*(volatile uint16_t *)(state+10u);
  *(volatile uint16_t *)(state+10u)=(uint16_t)(count+1u);
 }
 uint32_t limit=*(volatile uint16_t *)(state+2u);
 if(limit!=0u){
  uint32_t success=*(volatile uint16_t *)(state+6u);
  uint32_t failed=*(volatile uint16_t *)(state+8u);
  uint32_t other=*(volatile uint16_t *)(state+10u);
  if(success+failed+other>=limit)return 0u;
 }
 return *(volatile uint8_t *)state==2u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t p=0x8058dc;unsigned n=0;uint32_t values[]={0,1,0x7fffffff,0x80000000,0xffffffff};uint16_t counts[]={0,1,65534,65535};
for(unsigned event=0;event<6;event++)for(unsigned st=0;st<4;st++)for(unsigned limit=0;limit<5;limit++)for(unsigned ci=0;ci<4;ci++)for(unsigned li=0;li<5;li++)for(unsigned di=0;di<5;di++){uint32_t low=values[li],delta=values[di],high=values[(li+di)%5];*(uint8_t *)p=st;*(uint16_t *)(p+2)=limit;*(uint16_t *)(p+6)=counts[ci];*(uint16_t *)(p+8)=7;*(uint16_t *)(p+10)=9;*(uint16_t *)(p+20)=65535;*(uint32_t *)(p+12)=low;*(uint32_t *)(p+16)=high;uint64_t expected=((uint64_t)high<<32)|low;if(event==0)expected+=(uint64_t)(int64_t)(int32_t)delta;unsigned a=event==0?(uint16_t)(counts[ci]+1):counts[ci],b=event==4?8:7,c=event!=0&&event!=4?10:9;unsigned result=limit&&a+b+c>=limit?0:st==2;assert(opencfw_em9305_command_callback_332cd0(0,event,delta)==result);assert(*(uint16_t *)(p+6)==a&&*(uint16_t *)(p+8)==b&&*(uint16_t *)(p+10)==c&&*(uint16_t *)(p+20)==(event==0?0:65535));assert(*(uint32_t *)(p+12)==(uint32_t)expected&&*(uint32_t *)(p+16)==(uint32_t)(expected>>32));n++;}
printf("PASS %u\n",n);}
