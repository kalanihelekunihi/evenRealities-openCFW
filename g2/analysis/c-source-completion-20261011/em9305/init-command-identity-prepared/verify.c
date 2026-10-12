#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_lower_3080f8(uint32_t);
extern uint32_t opencfw_em9305_init_lower_30814c(uint32_t);
void opencfw_em9305_callback_31c0e0(void){}
void opencfw_em9305_callback_324628(void){}
void opencfw_em9305_callback_326904(void){}
void opencfw_em9305_callback_323620(void){}
void opencfw_em9305_callback_324dd4(void){}
void opencfw_em9305_callback_324e3c(void){}
uint32_t opencfw_em9305_ll_command_pending_310634(void){*(uint8_t *)0x805ec5u=1;return 0x805ec5u;}
uint32_t opencfw_em9305_radio_identity_control_303c9c(uint32_t v){for(unsigned j=0;j<16;j++)assert(*(uint8_t *)(uintptr_t)(0x8051e4u+j)==0);*(uint32_t *)0x80160cu=v;return v;}
int main(void){assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
 for(unsigned version=0;version<256;version++){
  *(uint32_t *)0x805b34u=version<<8;*(uint8_t *)0x805ec5u=0;
  assert(opencfw_em9305_init_lower_3080f8(0)==0x805ec5u&&*(uint8_t *)0x805ec5u==1&&*(uint32_t *)0x805b34u==((version<<8)|14));
  *(uint32_t *)0x805cacu=0x809000u;*(uint8_t *)0x809004u=(uint8_t)version;*(uint32_t *)0x805b30u=0xa5000000;memset((void *)0x8051e4u,0xa5,16);
  assert(opencfw_em9305_init_lower_30814c(0)==262&&*(uint16_t *)0x8051eau==262&&*(uint32_t *)0x805b30u==(0xa5000000u|(version<8?0:64)));
  assert(*(uint32_t *)0x80160cu==(uint32_t)(uintptr_t)opencfw_em9305_callback_324e3c);
  assert(*(uint32_t *)0x8056bcu==(uint32_t)(uintptr_t)opencfw_em9305_callback_31c0e0);
  assert(*(uint32_t *)0x803d48u==(uint32_t)(uintptr_t)opencfw_em9305_callback_31c0e0);
  assert(*(uint32_t *)0x805178u==(uint32_t)(uintptr_t)opencfw_em9305_callback_324628);
  assert(*(uint32_t *)0x8052c8u==(uint32_t)(uintptr_t)opencfw_em9305_callback_326904);
  assert(*(uint32_t *)0x805170u==(uint32_t)(uintptr_t)opencfw_em9305_callback_323620);
  assert(*(uint32_t *)0x802968u==(uint32_t)(uintptr_t)opencfw_em9305_callback_324dd4);
 }
 puts("PASS512 command/identity initialization cases");return 0;
}
