#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
/* Native31abc0..31ac08: active channel/slot match over656-byte rows. */
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t channel,uint32_t slot)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(!count)return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c68u;
 for(uint32_t i=0u;i<count;++i,row+=656u){
  if(*(volatile uint8_t *)row==0u)continue;
  if(*(volatile uint8_t *)(row+11u)!=channel)continue;
  if(*(volatile uint8_t *)(row+12u)==slot)return row;
 }
 return 0u;
}
/* Native31b278..31b2a8: byte-sized inactive link count. */
uint32_t opencfw_em9305_config_free_links_31b278(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u),free=0u;
 if(count){uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c68u;
  for(uint32_t i=0u;i<count;++i,row+=656u)if(*(volatile uint8_t *)row==0u)++free;
 }
 return free&255u;
}
/* Native31b2a8..31b2d0: captured input count/rows/id, lookup each compact row. */
uint32_t opencfw_em9305_config_existing_count_31b2a8(uintptr_t input)
{
 uint32_t count=*(volatile uint8_t *)(input+20u),found=0u;
 if(count){uintptr_t rows=*(volatile uint32_t *)(input+24u);
  uint32_t channel=*(volatile uint8_t *)input;
  for(uint32_t i=0u;i<count;++i){uint32_t slot=*(volatile uint8_t *)(rows+i*10u);
   found+=opencfw_em9305_config_link_find_31abc0(channel,slot)!=0u;
  }
 }
 return found&255u;
}

int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x810000;*(uint32_t*)0x805c68=0x820000;*(uint8_t*)0x811000=7;*(uint32_t*)0x811018=0x812000;unsigned cases=0;
 for(unsigned count=0;count<256;++count)for(unsigned pattern=0;pattern<4;++pattern){*(uint8_t*)0x810035=count;*(uint8_t*)0x811014=count;unsigned found=0;
  for(unsigned i=0;i<256;++i){uintptr_t r=0x820000u+i*656u;unsigned active=pattern==0?1:pattern==1?0:pattern==2?(i&1):i%3;*(uint8_t*)r=active?255:0;*(uint8_t*)(r+11)=7;*(uint8_t*)(r+12)=i;*(uint8_t*)(uintptr_t)(0x812000+i*10)=i;if(i<count&&active)++found;}
  if(opencfw_em9305_config_free_links_31b278()!=count-found||opencfw_em9305_config_existing_count_31b2a8(0x811000)!=found)return 3;
  cases+=2;
  for(unsigned slot=0;slot<256;++slot){uintptr_t row=0x820000u+slot*656u,expect=slot<count&&*(uint8_t*)row?row:0;if(opencfw_em9305_config_link_find_31abc0(7,slot)!=expect||opencfw_em9305_config_link_find_31abc0(263,slot)||opencfw_em9305_config_link_find_31abc0(7,slot+256))return 4;cases+=3;}
 }printf("PASS %u\n",cases);return 0;}
