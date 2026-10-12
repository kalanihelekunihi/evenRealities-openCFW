#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_lower_30a0a4(uint32_t);
void opencfw_em9305_callback_31bbb0(void){}
void opencfw_em9305_callback_328d78(void){}
void opencfw_em9305_callback_32922c(void){}
void opencfw_em9305_callback_31ce10(void){}
static unsigned stage;static uint8_t next_version;
uint32_t opencfw_em9305_init_child_3251dc(uint32_t cb){assert(stage==0&&cb==(uint32_t)(uintptr_t)opencfw_em9305_callback_31ce10);stage=1;return cb;}
uint32_t opencfw_em9305_init_child_317498(void){assert(stage==1);stage=2;return 0x1234u;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(stage==2&&p==(void *)0x8028d0u&&v==0&&n==128);stage=3;*(uint32_t *)0x805cacu=0x809000u;*(uint8_t *)0x809004u=next_version;return memset(p,0,n);}
int main(void){assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
 for(unsigned version=0;version<256;version++){
  stage=0;next_version=(uint8_t)version;*(uint32_t *)0x805cacu=0x809100u;*(uint8_t *)0x809104u=(uint8_t)~version;*(uint32_t *)0x805b30u=0xa5000000;
  memset((void *)0x8028cfu,0xa5,130);
  assert(opencfw_em9305_init_lower_30a0a4(0)==(version<11?version:0x805b30u)&&stage==3);
  assert(*(uint32_t *)0x805b30u==(0xa5000000u|(version<11?0:0x40000000u)));
  assert(*(uint8_t *)0x8028cfu==0xa5&&*(uint8_t *)0x802950u==0xa5);
  for(unsigned i=0;i<128;i++)assert(*(uint8_t *)(uintptr_t)(0x8028d0u+i)==0);
  assert(*(uint32_t *)0x802894u==(uint32_t)(uintptr_t)opencfw_em9305_callback_31bbb0);
  assert(*(uint32_t *)0x802990u==(uint32_t)(uintptr_t)opencfw_em9305_callback_328d78);
  assert(*(uint32_t *)0x80523cu==(uint32_t)(uintptr_t)opencfw_em9305_callback_32922c);
 }
 puts("PASS256 primary buffer registration/mutating-child cases");return 0;
}
