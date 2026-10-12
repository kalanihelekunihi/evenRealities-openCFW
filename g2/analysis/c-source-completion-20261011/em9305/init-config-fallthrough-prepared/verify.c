#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_lower_30a134(uint32_t);
extern uint32_t opencfw_em9305_init_lower_30a1a0(uint32_t);
void opencfw_em9305_callback_32bb9c(void){}
void opencfw_em9305_callback_32a218(void){}
void opencfw_em9305_callback_329844(void){}
void opencfw_em9305_callback_318f2c(void){}
void opencfw_em9305_callback_318c1c(void){}
void opencfw_em9305_callback_31bd78(void){}
void opencfw_em9305_callback_32ae70(void){}
void opencfw_em9305_callback_32bc6c(void){}
void opencfw_em9305_callback_325984(void){}
void opencfw_em9305_callback_3189f4(void){}
void opencfw_em9305_callback_319890(void){}
void opencfw_em9305_callback_32a628(void){}
void opencfw_em9305_callback_32a5ac(void){}
uint32_t opencfw_em9305_callback_30fc20(uint32_t a,uint32_t b){return a+b;}
uint32_t opencfw_em9305_callback_30fc24(uint32_t a,uint32_t b){return a+b;}
static unsigned stage;static uint8_t version;static uint32_t expected_prefix;static unsigned prefix_entry;
uint32_t opencfw_em9305_init_child_3251dc(uint32_t cb){assert(stage==0&&cb==(uint32_t)(uintptr_t)opencfw_em9305_callback_3189f4);assert(*(uint32_t *)0x805b30u==expected_prefix);
 if(prefix_entry){assert(*(uint32_t *)0x8052ccu==(uint32_t)(uintptr_t)opencfw_em9305_callback_30fc20&&*(uint32_t *)0x8052d0u==(uint32_t)(uintptr_t)opencfw_em9305_callback_30fc24);}
 stage=1;return cb;}
uint32_t opencfw_em9305_init_child_318ab8(uint32_t cb){assert(stage==1&&cb==(uint32_t)(uintptr_t)opencfw_em9305_callback_3189f4);stage=2;*(uint32_t *)0x805cacu=0x809000u;*(uint8_t *)0x809004u=version;*(uint32_t *)0x805b30u=0x80204000u;*(uint32_t *)0x805b34u=0x12345600u;return 0x42;}
int main(void){assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);unsigned cases=0;
 for(unsigned v=0;v<256;v++)for(unsigned entry=0;entry<2;entry++)for(unsigned existing=0;existing<2;existing++){
  version=(uint8_t)v;stage=0;prefix_entry=entry;expected_prefix=0x55550000u|(entry?((uint8_t)~v<7u?1u:17u):0u);*(uint32_t *)0x805cacu=0x809100u;*(uint8_t *)0x809104u=(uint8_t)~v;
  *(uint32_t *)0x80280cu=existing?0x12345678u:0;*(uint32_t *)0x802954u=existing?0x87654321u:0;*(uint32_t *)0x805b30u=0x55550000u;
  uint32_t result=entry?opencfw_em9305_init_lower_30a134(0):opencfw_em9305_init_lower_30a1a0(0);
  uint32_t mask=v<7?0:v==7?14:v==8?46:v==9?0x1002e:0x501002e;
  assert(stage==2&&result==(v<7?0x809000u:(0x80204000u|mask)));
  assert(*(uint32_t *)0x805b30u==(0x80204000u|mask)&&*(uint32_t *)0x805b34u==(0x12345600u|(v<12?0:128)));
  assert(*(uint32_t *)0x802954u==(existing?0x87654321u:(uint32_t)(uintptr_t)opencfw_em9305_callback_329844));
  assert(*(uint32_t *)0x80280cu==(existing?0x12345678u:(uint32_t)(uintptr_t)(entry?opencfw_em9305_callback_32a5ac:opencfw_em9305_callback_32bc6c)));
  assert(*(uint32_t *)0x802950u==(uint32_t)(uintptr_t)opencfw_em9305_callback_32bb9c&&*(uint32_t *)0x805200u==(uint32_t)(uintptr_t)opencfw_em9305_callback_32a218);
  cases++;
 }
 printf("PASS%u config fallthrough/version/child-mutation cases\n",cases);return 0;
}
