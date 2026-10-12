#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_callback_3041e0(uintptr_t);
static unsigned stage;
static uint8_t owner[160];
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n)
{
 assert(stage++==0u&&v==0u&&n==20u);
 assert(*(uint8_t *)(uintptr_t)0x8015c4u==1u&&owner[136]==0u);
 for(uint32_t i=0;i<n;i++)((uint8_t *)p)[i]=(uint8_t)v;
 return p;
}
uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t p)
{assert(stage++==1u);for(unsigned i=0;i<20;i++)assert(((uint8_t *)p)[i]==0u);return 999u;}
uint32_t opencfw_em9305_radio_request_30fcd8(uintptr_t p,uint32_t mode)
{assert(stage++==2u&&p==(uintptr_t)(owner+120)&&mode==1u);return 888u;}
int main(void)
{
 assert(mmap((void *)(uintptr_t)0x801000u,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)(uintptr_t)0x801000u);
 for(unsigned seed=0;seed<256u;seed++){
  stage=0;owner[136]=(uint8_t)seed;owner[135]=77;owner[137]=99;
  *(uint8_t *)(uintptr_t)0x8015c4u=(uint8_t)seed;
  assert(opencfw_em9305_callback_3041e0((uintptr_t)owner)==0u);
  assert(stage==3&&owner[135]==77&&owner[137]==99);
 }
 return 0;
}
