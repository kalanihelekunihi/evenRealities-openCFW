#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls;
void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){return memset(p,v,n);}
uint32_t opencfw_em9305_command_count_30e4bc(void){if(calls!=0)__builtin_trap();++calls;return 0xff;}
uint32_t opencfw_em9305_common_request_30455c(uint32_t role){if(calls!=1||role!=1)__builtin_trap();++calls;return 0xee;}
static inline uint32_t opencfw_em9305_config_allocator_stride(uint32_t i,uint32_t w){return i*w;}
/* Native316b5c..316bbc: first inactive140B channel, typed initialization and shared request. */
uintptr_t opencfw_em9305_config_channel_allocate_316b5c(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+52u);
 if(!count)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c64u;
 for(uint32_t i=0u;i<count;++i){uintptr_t row=base+opencfw_em9305_config_allocator_stride(i,140u);
  if(*(volatile uint8_t *)row!=0u)continue;
  (void)opencfw_em9305_memset((void *)row,0u,140u);
  *(volatile uint8_t *)row=1u;
  *(volatile uint32_t *)(row+92u)=0u;*(volatile uint32_t *)(row+88u)=0u;
  *(volatile uint16_t *)(row+8u)=(uint16_t)i;
  *(volatile uint8_t *)(row+6u)=(uint8_t)id;
  (void)opencfw_em9305_command_count_30e4bc();
  (void)opencfw_em9305_common_request_30455c(1u);
  return row;
 }
 return 0u;
}
/* Native316bbc..316c56: first inactive656B link and product-derived live fields. */
uintptr_t opencfw_em9305_config_link_allocate_316bbc(uintptr_t channel)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(!count)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
 for(uint32_t i=0u;i<count;++i){uintptr_t row=base+opencfw_em9305_config_allocator_stride(i,656u);
  if(*(volatile uint8_t *)row!=0u)continue;
  (void)opencfw_em9305_memset((void *)row,0u,656u);
  uint32_t seed=*(volatile uint16_t *)(row+6u);
  config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  *(volatile uint16_t *)(row+80u)=(uint16_t)seed;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  uint32_t capacity=*(volatile uint8_t *)(config+34u);
  *(volatile uint8_t *)(row+528u)=255u;*(volatile uint8_t *)(row+532u)=255u;
  *(volatile uint16_t *)(row+82u)=0x5201u;
  *(volatile uint16_t *)(row+458u)=0x470fu;
  *(volatile uint8_t *)(row+88u)=(uint8_t)handler;
  *(volatile uint8_t *)(row+464u)=(uint8_t)handler;
  uint32_t id=*(volatile uint8_t *)(channel+6u);
  uint32_t index=i+capacity;
  *(volatile uint8_t *)row=1u;
  *(volatile uint16_t *)(row+8u)=(uint16_t)index;
  *(volatile uint16_t *)(row+456u)=(uint16_t)index;
  *(volatile uint8_t *)(row+11u)=(uint8_t)id;
  return row;
 }
 return 0u;
}

int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x810000;*(uint32_t*)0x805c64=0x820000;*(uint32_t*)0x805c68=0x820000;*(uint8_t*)0x811006=7;unsigned cases=0;
 for(unsigned kind=0;kind<2;++kind)for(unsigned count=0;count<256;++count)for(unsigned pick=0;pick<4;++pick)for(unsigned variant=0;variant<2;++variant){unsigned width=kind?656:140,slot=pick==0?0:pick==1?count/2:pick==2?(count?count-1:0):count;
  memset((void*)0x820000,0xa5,256*656);*(uint8_t*)0x810034=count;*(uint8_t*)0x810035=count;*(uint8_t*)0x810022=variant?255:0;*(uint8_t*)0x805b18=variant?73:255;calls=0;
  if(slot<count)*(uint8_t*)(uintptr_t)(0x820000+slot*width)=0;
  uintptr_t expected=slot<count?0x820000+slot*width:0;
  uintptr_t got=kind?opencfw_em9305_config_link_allocate_316bbc(0x811000):opencfw_em9305_config_channel_allocate_316b5c(263);
  if(got!=expected)return 3;
  if(got){uint8_t bytes[656];memset(bytes,0,width);bytes[0]=1;
   if(kind){uint16_t index=slot+(variant?255:0);bytes[528]=bytes[532]=255;*(uint16_t*)(bytes+82)=0x5201;*(uint16_t*)(bytes+458)=0x470f;bytes[88]=bytes[464]=variant?73:255;*(uint16_t*)(bytes+8)=*(uint16_t*)(bytes+456)=index;bytes[11]=7;if(calls)return 4;}
   else{*(uint16_t*)(bytes+8)=slot;bytes[6]=7;if(calls!=2)return 5;}
   if(memcmp(bytes,(void*)got,width))return 6;
  }else if(calls)return 7;
  ++cases;
 }printf("PASS %u\n",cases);return 0;}
