#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned mode,cleared,finalized;
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){if(id!=7)__builtin_trap();return mode&1?0:0x812000;}
uint32_t opencfw_em9305_config_channel_busy_31b2f8(uintptr_t p){if(p!=0x812000)__builtin_trap();return mode&2;}
uint32_t opencfw_em9305_config_link_clear_31ad88(uintptr_t p){if(p<0x820000||p>=0x850d70)__builtin_trap();++cleared;if(mode&4)*(uint8_t*)0x811035=0;return 0xff;}
uint32_t opencfw_em9305_config_channel_clear_31ad64(uintptr_t p){if(p!=0x812000)__builtin_trap();++finalized;return 0xee;}
extern uint32_t opencfw_em9305_config_channel_busy_31b2f8(uintptr_t);
extern uint32_t opencfw_em9305_config_link_clear_31ad88(uintptr_t);
extern uint32_t opencfw_em9305_config_channel_clear_31ad64(uintptr_t);
static inline uint32_t opencfw_em9305_config_clear_stride(uint32_t i){return i*656u;}
/* Native3083a4..30843c and30ca18 tail: channel guard, live link release and final clear. */
uint32_t opencfw_em9305_command_config_clear_30ca18(uint32_t id)
{
 uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(id);
 if(!channel)return 2u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(count){uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
  for(uint32_t i=0u;i<count;++i){uintptr_t row=base+opencfw_em9305_config_clear_stride(i);
   if(*(volatile uint8_t *)row==0u)continue;
   if(*(volatile uint8_t *)(row+11u)!=id)continue;
   if(*(volatile uint8_t *)(row+10u)==1u)return 12u;
   if(*(volatile uint8_t *)(row+67u)!=0u)return 12u;
  }
 }
 if(opencfw_em9305_config_channel_busy_31b2f8(channel)!=0u)return 12u;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t i=0u;
 while(i<*(volatile uint8_t *)(config+53u)){
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
  uintptr_t row=base+opencfw_em9305_config_clear_stride(i);
  if(*(volatile uint8_t *)row!=0u&&*(volatile uint8_t *)(row+11u)==id&&*(volatile uint8_t *)(row+10u)==0u){
   (void)opencfw_em9305_config_link_clear_31ad88(row);
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  }++i;
 }
 (void)opencfw_em9305_config_channel_clear_31ad64(channel);
 return 0u;
}

int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x811000;*(uint32_t*)0x805c68=0x820000;unsigned cases=0;
 for(unsigned count=0;count<256;++count)for(unsigned profile=0;profile<16;++profile)for(mode=0;mode<8;++mode){
  memset((void*)0x820000,0,256*656);*(uint8_t*)0x811035=count;cleared=finalized=0;unsigned matches=0,busy=0;
  for(unsigned i=0;i<count;++i){uintptr_t r=0x820000u+i*656u;*(uint8_t*)r=(profile&1)?1:0;*(uint8_t*)(r+11)=(profile&2)?7:8;*(uint8_t*)(r+10)=(profile&4)?1:0;*(uint8_t*)(r+67)=(profile&8)?255:0;if(*(uint8_t*)r&&*(uint8_t*)(r+11)==7){++matches;if(*(uint8_t*)(r+10)==1||*(uint8_t*)(r+67))busy=1;}}
  unsigned expected=mode&1?2:(busy||(mode&2))?12:0;
  if(opencfw_em9305_command_config_clear_30ca18(7)!=expected)return 3;
  unsigned want=expected?0:((mode&4)&&matches?1:matches);
  if(cleared!=want||finalized!=(expected==0))return 4;
  ++cases;
 }printf("PASS %u\n",cases);return 0;}
