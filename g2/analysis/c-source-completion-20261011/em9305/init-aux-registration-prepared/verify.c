#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_lower_307e30(uint32_t);
void opencfw_em9305_callback_32233c(void){}
void opencfw_em9305_callback_322184(void){}
void opencfw_em9305_callback_322178(void){}
void opencfw_em9305_callback_322580(void){}
void opencfw_em9305_callback_3225b0(void){}
void opencfw_em9305_callback_3246f8(void){}
void opencfw_em9305_callback_3042b4(void){}
void opencfw_em9305_callback_30425c(void){}
void opencfw_em9305_callback_3041e0(void){}
void opencfw_em9305_callback_304214(void){}
int main(void){assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
 for(unsigned version=0;version<256;version++){
  *(uint32_t *)0x805cacu=0x809000u;*(uint8_t *)0x809004u=(uint8_t)version;*(uint32_t *)0x805b34u=0xa5000080u;
  assert(opencfw_em9305_init_lower_307e30(0xdeadbeef)==(version<13?version:0x805b34u));
  assert(*(uint32_t *)0x805b34u==(0xa5000080u|(version<13?0:4096)));
  for(unsigned i=0;i<6;i++)assert(*(uint32_t *)(uintptr_t)(0x805c44u+i*4u)==0x801a1cu+584u*i);
  assert(*(uint32_t *)0x805c8cu==(uint32_t)(uintptr_t)opencfw_em9305_callback_32233c);
  assert(*(uint32_t *)0x805c88u==(uint32_t)(uintptr_t)opencfw_em9305_callback_322184);
  assert(*(uint32_t *)0x805c84u==(uint32_t)(uintptr_t)opencfw_em9305_callback_322178);
  assert(*(uint32_t *)0x805c90u==(uint32_t)(uintptr_t)opencfw_em9305_callback_322580);
  assert(*(uint32_t *)0x805c94u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3225b0);
  assert(*(uint32_t *)0x805ca8u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3246f8);
  assert(*(uint32_t *)0x805c14u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3042b4);
  assert(*(uint32_t *)0x805c10u==(uint32_t)(uintptr_t)opencfw_em9305_callback_30425c);
  assert(*(uint32_t *)0x805c08u==(uint32_t)(uintptr_t)opencfw_em9305_callback_3041e0);
  assert(*(uint32_t *)0x805c0cu==(uint32_t)(uintptr_t)opencfw_em9305_callback_304214);
 }
 puts("PASS256 auxiliary registration states");return 0;
}
