#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_lower_30a29c(uint32_t);
void opencfw_em9305_callback_32aa48(void){}
void opencfw_em9305_callback_327a54(void){}
void opencfw_em9305_callback_32bb40(void){}
void opencfw_em9305_callback_32ae3c(void){}
void opencfw_em9305_callback_32c148(void){}
void opencfw_em9305_callback_306cbc(void){}
static uint8_t version,product_count;static unsigned stage;
uint32_t opencfw_em9305_init_child_3251dc(uint32_t cb){assert(stage==0&&cb==(uint32_t)(uintptr_t)opencfw_em9305_callback_32bb40);stage=1;*(uint32_t *)0x805cacu=0x809000u;*(uint8_t *)0x809004u=version;*(uint8_t *)0x80900cu=product_count;return cb;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(stage==1&&p==(void *)0x900000u&&v==0&&n==(uint32_t)product_count*2824u);
 assert(*(uint32_t *)0x805b30u==(0xa5000000u|(version<9?0:4096))&&*(uint32_t *)0x805b34u==(0x51000080u|(version<13?0:version==13?256:1280)));
 stage=2;*(uint8_t *)0x809004u=(uint8_t)~version;*(uint8_t *)0x80900cu=0;*(uint32_t *)0x805c38u=0x910000u;return memset(p,0,n);}
int main(void){assert(mmap((void *)0x800000u,0x200000u,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);unsigned cases=0;const unsigned counts[]={0,1,255};
 for(unsigned v=0;v<256;v++)for(unsigned k=0;k<3;k++){
  version=(uint8_t)v;product_count=(uint8_t)counts[k];stage=0;*(uint32_t *)0x805cacu=0x809100u;*(uint8_t *)0x809104u=(uint8_t)~v;*(uint32_t *)0x805c38u=0x900000u;
  *(uint32_t *)0x805b30u=0xa5000000u;*(uint32_t *)0x805b34u=0x51000080u;
  uint32_t bytes=counts[k]*2824;*(uint8_t *)0x8fffffu=0xa5;*(uint8_t *)(uintptr_t)(0x900000u+bytes)=0xa5;if(bytes){*(uint8_t *)0x900000u=0xa5;*(uint8_t *)(uintptr_t)(0x900000u+bytes-1)=0xa5;}
  assert(opencfw_em9305_init_lower_30a29c(0)==0x900000u&&stage==2);
  assert(*(uint8_t *)0x8fffffu==0xa5&&*(uint8_t *)(uintptr_t)(0x900000u+bytes)==0xa5);if(bytes)assert(*(uint8_t *)0x900000u==0&&*(uint8_t *)(uintptr_t)(0x900000u+bytes-1)==0);
  assert(*(uint32_t *)0x802970u==(uint32_t)(uintptr_t)opencfw_em9305_callback_32aa48);
  assert(*(uint32_t *)0x802988u==(uint32_t)(uintptr_t)opencfw_em9305_callback_327a54);
  assert(*(uint32_t *)0x80521cu==(uint32_t)(uintptr_t)opencfw_em9305_callback_32ae3c);
  assert(*(uint32_t *)0x8028a0u==(uint32_t)(uintptr_t)opencfw_em9305_callback_32c148);
  assert(*(uint32_t *)0x801300u==(uint32_t)(uintptr_t)opencfw_em9305_callback_306cbc);
  cases++;
 }
 printf("PASS%u product-clear/version/mutation cases\n",cases);return 0;
}
