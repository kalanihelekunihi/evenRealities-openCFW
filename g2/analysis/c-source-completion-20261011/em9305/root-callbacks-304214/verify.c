#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_callback_304214(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t);
#define R32(p) (*(uint32_t *)(uintptr_t)(p))
static unsigned stage,optional_calls,final_calls;
static uint32_t final_b(uintptr_t owner,uint32_t event)
{assert(stage++==4&&owner==123&&event==456);final_calls++;return 777;}
static uint32_t final_a(uintptr_t owner,uint32_t event)
{assert(stage++==3&&owner==123&&event==456);final_calls++;return 888;}
static uint32_t optional(uintptr_t owner,uint32_t r4,uint32_t value,uintptr_t payload,uint32_t count)
{assert(stage++==3&&owner==123&&r4==789&&value==321&&payload==0x810078&&count==2);optional_calls++;R32(0x810068)=(uint32_t)(uintptr_t)final_b;return 999;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n)
{assert(stage++==0&&v==0&&n==20);for(unsigned i=0;i<n;i++)((uint8_t *)p)[i]=0;return p;}
uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t p)
{assert(stage++==1);for(unsigned i=0;i<20;i++)assert(((uint8_t *)p)[i]==0);return 333;}
uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t p)
{assert(stage++==2&&p==333);return 222;}
int main(void)
{
 assert(mmap((void *)(uintptr_t)0x810000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)(uintptr_t)0x810000);
 for(unsigned word=0;word<2;word++)for(unsigned callback=0;callback<2;callback++){
  stage=optional_calls=final_calls=0;
  R32(0x810070)=word?321:0;R32(0x810074)=callback?(uint32_t)(uintptr_t)optional:0;R32(0x810068)=(uint32_t)(uintptr_t)final_a;
  assert(opencfw_em9305_callback_304214(123,0x810000,456,0xdeadbeef,789)==(word&&callback?0u:1u));
  assert(optional_calls==(word&&callback)&&final_calls==1&&stage==(word&&callback?5u:4u));
 }
 return 0;
}
