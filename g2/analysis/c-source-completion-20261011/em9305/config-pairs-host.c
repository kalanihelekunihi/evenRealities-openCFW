#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned active,state,applied,apply_result;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){(void)id;return active;}
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id){(void)id;return state;}
uint32_t opencfw_em9305_config_pairs_apply_306b80(uint32_t n,uintptr_t p){(void)n;(void)p;++applied;return apply_result;}
extern uint32_t opencfw_em9305_config_pairs_apply_306b80(uint32_t,uintptr_t);
/* Native30b3f8..30b480: capability, duplicate first-array ids, second-array slot state. */
uint32_t opencfw_em9305_command_config_pairs_30b3f8(uint32_t count,uintptr_t arrays)
{
 if((*(volatile uint8_t *)(uintptr_t)0x805a98u&1u)==0u)return 12u;
 uint32_t status=0u;
 for(uint32_t row=0u;status==0u&&row<count;++row){
  for(uint32_t previous=0u;status==0u&&previous<row;++previous){
   uintptr_t first=*(volatile uint32_t *)arrays;
   uint32_t prior=*(volatile uint16_t *)(first+previous*2u);
   uint32_t current=*(volatile uint16_t *)(first+row*2u);
   if(current==prior)status=18u;
  }
  if(status!=0u)continue;
  uintptr_t second=*(volatile uint32_t *)(arrays+4u);
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t id=*(volatile uint16_t *)(second+row*2u);
  uint32_t capacity=*(volatile uint8_t *)(config+34u);
  status=2u;
  if(id>=capacity)continue;
  if(opencfw_em9305_ll_slot_active_30731c(id)==0u)continue;
  second=*(volatile uint32_t *)(arrays+4u);
  id=*(volatile uint16_t *)(second+row*2u);
  status=opencfw_em9305_ll_slot_state_306fdc(id)!=0u?12u:0u;
 }
 if(status==0u)status=opencfw_em9305_config_pairs_apply_306b80(count,arrays);
 return status&255u;
}

int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 *(uint32_t*)0x810000=0x810100;*(uint32_t*)0x810004=0x810200;*(uint32_t*)0x805cac=0x811000;unsigned cases=0;
 for(unsigned gate=0;gate<2;++gate)for(unsigned count=0;count<5;++count)for(unsigned dup=0;dup<5;++dup)for(unsigned cap=0;cap<256;++cap)for(unsigned flags=0;flags<4;++flags){
  *(uint8_t*)0x805a98=gate;*(uint8_t*)0x811022=cap;active=flags&1;state=(flags>>1)*255;applied=0;apply_result=0x123;
  for(unsigned i=0;i<4;++i){*(uint16_t*)(uintptr_t)(0x810100+i*2)=i==dup?0:i;*(uint16_t*)(uintptr_t)(0x810200+i*2)=i;}
  unsigned expected=gate?0:12;
  if(gate)for(unsigned i=0;i<count&&!expected;++i){for(unsigned j=0;j<i;++j)if(*(uint16_t*)(uintptr_t)(0x810100+i*2)==*(uint16_t*)(uintptr_t)(0x810100+j*2))expected=18;if(!expected)expected=i>=cap||!active?2:state?12:0;}
  unsigned expect_apply=gate&&!expected;if(expect_apply)expected=0x23;
  if(opencfw_em9305_command_config_pairs_30b3f8(count,0x810000)!=expected||applied!=expect_apply)return 3;
  ++cases;
 }printf("PASS %u\n",cases);return 0;
}
