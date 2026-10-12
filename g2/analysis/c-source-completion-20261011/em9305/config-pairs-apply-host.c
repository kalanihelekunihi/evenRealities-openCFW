#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned mode,finds,allocs,sends;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){++finds;if(id>1)__builtin_trap();return (mode&2)&&id==1?0:0x811000+id*1024;}
uint32_t opencfw_em9305_ll_link_state_ready_31b750(uintptr_t p){return (mode&4)&&p==0x811400;}
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){if(id>1)__builtin_trap();return 0x814000+id*256;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=6)__builtin_trap();++allocs;return mode&8?0:0x815000;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){if(h!=73||p!=0x815000)__builtin_trap();++sends;return 0xbad;}
/* Native306b80..306c44: clipped two-row link/channel mutation, latch and six-byte message. */
uint32_t opencfw_em9305_config_pairs_apply_306b80(uint32_t count,uintptr_t arrays)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805ab1u!=0u)return 12u;
 uint32_t limit=count<2u?count:2u;
 for(uint32_t i=0u;i<limit;++i){
  uintptr_t first=*(volatile uint32_t *)arrays;
  uint32_t id=*(volatile uint16_t *)(first+i*2u);
  uintptr_t link=opencfw_em9305_ll_link_find_31ab88(id);
  if(link==0u)return 2u;
  if(opencfw_em9305_ll_link_state_ready_31b750(link)!=0u)return 11u;
  uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)(link+11u));
  *(volatile uint8_t *)(channel+1u)=1u;
  *(volatile uint8_t *)(link+25u)=0u;
 }
 *(volatile uint8_t *)(uintptr_t)0x802a48u=(uint8_t)limit;
 *(volatile uint8_t *)(uintptr_t)0x805ab1u=1u;
 for(uint32_t i=0u;i<limit;++i){
  uintptr_t first=*(volatile uint32_t *)arrays,second=*(volatile uint32_t *)(arrays+4u);
  uint32_t a=*(volatile uint16_t *)(first+i*2u);
  *(volatile uint16_t *)(uintptr_t)(0x802a4au+i*2u)=(uint16_t)a;
  uint32_t b=*(volatile uint16_t *)(second+i*2u);
  *(volatile uint16_t *)(uintptr_t)(0x802a4eu+i*2u)=(uint16_t)b;
  *(volatile uint8_t *)(uintptr_t)(0x802a52u+i)=0u;
 }
 uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
 if(message==0u)return 0u;
 uint32_t second=*(volatile uint16_t *)(uintptr_t)0x802a4eu;
 *(volatile uint16_t *)(message+2u)=0x2401u;
 *(volatile uint16_t *)message=(uint16_t)second;
 uint32_t first=*(volatile uint16_t *)(uintptr_t)0x802a4au;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)(message+4u)=(uint16_t)first;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 *(uint32_t*)0x810000=0x810100;*(uint32_t*)0x810004=0x810200;*(uint16_t*)0x810100=0;*(uint16_t*)0x810102=1;*(uint16_t*)0x810200=27;*(uint16_t*)0x810202=29;
 *(uint8_t*)0x81100b=0;*(uint8_t*)0x81140b=1;*(uint8_t*)0x805b18=73;
 unsigned cases=0;
 for(unsigned count=0;count<65536;++count)for(mode=0;mode<16;++mode){
  finds=allocs=sends=0;*(uint8_t*)0x805ab1=mode&1;memset((void*)0x802a48,0xa5,16);memset((void*)0x815000,0xa5,8);*(uint8_t*)0x811019=9;*(uint8_t*)0x811419=9;*(uint8_t*)0x814001=9;*(uint8_t*)0x814101=9;
  unsigned limit=count<2?count:2,expected=mode&1?12:limit==2&&(mode&2)?2:limit==2&&(mode&4)?11:0;
  if(opencfw_em9305_config_pairs_apply_306b80(count,0x810000)!=expected)return 3;
  if(expected){if(allocs||sends||*(uint8_t*)0x802a48!=0xa5)return 4;if(limit==2&&!(mode&1)&&(*(uint8_t*)0x811019||*(uint8_t*)0x814001!=1))return 5;}
  else{
   if(allocs!=1||sends!=(!(mode&8))||*(uint8_t*)0x802a48!=limit||*(uint8_t*)0x805ab1!=1)return 6;
   for(unsigned i=0;i<limit;++i)if(*(uint16_t*)(uintptr_t)(0x802a4a+i*2)!=i||*(uint16_t*)(uintptr_t)(0x802a4eu+i*2)!=(i?29:27)||*(uint8_t*)(uintptr_t)(0x802a52+i))return 7;
   if(sends){uint16_t a=limit?0:0xa5a5,bv=limit?27:0xa5a5;if(*(uint16_t*)0x815000!=bv||*(uint16_t*)0x815002!=0x2401||*(uint16_t*)0x815004!=a||*(uint16_t*)0x815006!=0xa5a5)return 8;}
  }++cases;
 }
 printf("PASS %u\n",cases);return 0;
}
