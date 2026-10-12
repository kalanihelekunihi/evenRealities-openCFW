#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_secondary_start_3213f8(uintptr_t);
extern uint32_t opencfw_em9305_callback_3213ec(uintptr_t);
static uintptr_t seen;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(n==148u);return memset(p,(int)v,n);}
uint32_t opencfw_em9305_callback_321648(uintptr_t p){seen=p;assert(*(uint8_t *)(0x809000u+8u)==1u);return 0x91234567u;}
uint32_t opencfw_em9305_callback_321c30(uintptr_t p){return (uint32_t)p;}
uint32_t opencfw_em9305_callback_321958(uintptr_t p){return (uint32_t)p;}
static void word(unsigned char *p,unsigned off,uint32_t value){memcpy(p+off,&value,4);}
int main(void){
 uintptr_t r=0x808000u;
 assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
 for(unsigned marker=0;marker<256;marker++){
  unsigned char expected[784];memset((void *)r,(int)marker,784);memset(expected,(int)marker,784);
  memset(expected+48,0,148);expected[74]=1;expected[72]=1;expected[96]=9;
  word(expected,80,(uint32_t)(uintptr_t)opencfw_em9305_callback_3213ec);
  word(expected,76,(uint32_t)(uintptr_t)opencfw_em9305_callback_321648);
  word(expected,200,(uint32_t)(uintptr_t)opencfw_em9305_callback_321c30);
  word(expected,196,(uint32_t)(uintptr_t)opencfw_em9305_callback_321958);
  word(expected,84,(uint32_t)r);word(expected,92,(uint32_t)(r+96));
  expected[2]=0;expected[603]=0;word(expected,212,0);
  assert(opencfw_em9305_init_secondary_start_3213f8(r)==0);
  assert(memcmp((void *)r,expected,784)==0);
  *(uint32_t *)(r+36)=0x809000u;*(uint8_t *)0x809008u=(uint8_t)marker;
  assert(opencfw_em9305_callback_3213ec(r)==0x91234567u && seen==r);
 }
 puts("PASS 512 full-record and callback fixtures");return 0;
}
