#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#define R32(p) (*(uint32_t *)(uintptr_t)(p))
uint32_t opencfw_em9305_callback_30425c(uintptr_t,uint32_t,uint32_t,uintptr_t,uint32_t);
static unsigned stage,mutation;
uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t p)
{assert(stage++==0&&p==0x810100&&R32(p+4)==222);assert(*(uint8_t *)(uintptr_t)0x8015c4==1);if(mutation)R32(0x81002c)=0x810200;return 666;}
uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t p)
{assert(stage++==1&&p==0x8015cc&&R32(p+8)==300);assert(R32((mutation?0x810200:0x810100)+4)==111);return 555;}
void *opencfw_em9305_memset(void *p,uint32_t value,uint32_t n)
{assert(stage++==2&&value==0&&n==20);for(unsigned i=0;i<n;i++)((uint8_t *)p)[i]=0;return p;}
uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t p)
{assert(stage++==3);for(unsigned i=0;i<20;i++)assert(((uint8_t *)p)[i]==0);return 444;}
uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t p)
{assert(stage++==4&&p==444);return 333;}
uint32_t opencfw_em9305_radio_record_request_30fc68(uintptr_t p,uint32_t sel)
{assert(stage++==5&&p==0x812345&&sel==77);return 999;}
int main(void)
{
 assert(mmap((void *)(uintptr_t)0x810000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)(uintptr_t)0x810000);
 assert(mmap((void *)(uintptr_t)0x801000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)(uintptr_t)0x801000);
 for(mutation=0;mutation<2;mutation++){
  stage=0;R32(0x81002c)=0x810100;R32(0x810104)=111;R32(0x810148)=222;R32(0x810204)=333;
  assert(opencfw_em9305_callback_30425c(0x810000,100,200,0x812345,77)==999&&stage==6);
  if(mutation)assert(R32(0x810104)==222);
 }
 return 0;
}
