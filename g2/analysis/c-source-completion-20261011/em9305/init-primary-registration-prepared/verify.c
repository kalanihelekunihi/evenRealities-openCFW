#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_lower_307d74(uint32_t);
void opencfw_em9305_callback_3228a8(void){} void opencfw_em9305_callback_3228f0(void){}
void opencfw_em9305_callback_3227e0(void){} void opencfw_em9305_callback_3227a4(void){}
static uint8_t next_version;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(p==(void *)0x804fd8u&&v==0&&n==404);*(uint32_t *)0x805cacu=0x809000u;*(uint8_t *)0x809004u=next_version;return memset(p,0,n);}
int main(void){assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
 for(unsigned version=0;version<256;version++){
  next_version=(uint8_t)version;*(uint32_t *)0x805cacu=0x809100u;*(uint8_t *)0x809104u=(uint8_t)~version;
  *(uint32_t *)0x805b30u=0xa5a50000u;memset((void *)0x804fd7u,0xa5,406);
  assert(opencfw_em9305_init_lower_307d74(0xdeadbeef)==(version<8?version:0x805b30u));
  assert(*(uint32_t *)0x805b30u==(0xa5a50000u|(version<8?0:128)));
  assert(*(uint8_t *)0x804fd7u==0xa5&&*(uint8_t *)0x80516cu==0xa5);
  for(unsigned j=0;j<404;j++)assert(*(uint8_t *)(uintptr_t)(0x804fd8u+j)==0);
  assert(*(uint32_t *)0x802958u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3228a8&&*(uint32_t *)0x805204u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3228f0&&*(uint32_t *)0x80289cu==(uint32_t)(uintptr_t)opencfw_em9305_callback_3227e0&&*(uint32_t *)0x802898u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3227a4);
 }
 puts("PASS256 primary registration/mutating-child states");return 0;
}
