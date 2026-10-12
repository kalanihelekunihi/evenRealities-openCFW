#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,mutation;
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t id,uint32_t slot){if(id!=7)__builtin_trap();++calls;if(mutation){*(uint8_t*)0x810014=0;*(uint32_t*)0x810018=0x81f000;}return 0x820000u+slot*656u;}
/* Native3185e8..318670: two PHY contributions, feature reads remain separately live. */
uint32_t opencfw_em9305_config_link_time_3185e8(uint32_t first_phy,uint32_t second_phy,uint32_t first_length,uint32_t second_length)
{
 uint32_t sum=0u;
 if(first_phy==1u)sum=(first_length<<3u)+112u;
 else if(first_phy==2u)sum=60u+(first_length<<2u);
 else if(first_phy==3u){uint32_t n=first_length+4u;
  sum=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 sum+=150u;
 if(second_phy==1u)sum+=(second_length<<3u)+112u;
 else if(second_phy==2u)sum+=(second_length<<2u)+60u;
 else if(second_phy==3u){uint32_t n=second_length+4u;
  sum+=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return sum+*(volatile uint16_t *)(config+54u)+150u;
}
/* Native318670..31869e: early second-slot gate, equality and first empty attachment. R1 preserved by native routine. */
uint32_t opencfw_em9305_config_attach_link_318670(uintptr_t channel,uintptr_t link)
{
 if(*(volatile uint32_t *)(channel+92u))return 0u;
 for(uint32_t i=0u;i<2u;++i){uintptr_t cell=channel+88u+i*4u;uint32_t value=*(volatile uint32_t *)cell;
  if(value==(uint32_t)link)return 1u;
  if(value==0u){*(volatile uint32_t *)cell=(uint32_t)link;return 1u;}
 }
 return 0u;
}
/* Native3185a8..3185e8: captured count/id/row base and full timing sum. */
uint32_t opencfw_em9305_config_basic_link_sum_3185a8(uintptr_t input)
{
 uint32_t count=*(volatile uint8_t *)(input+20u),total=0u;
 if(count){uintptr_t rows=*(volatile uint32_t *)(input+24u);uint32_t id=*(volatile uint8_t *)input;
  for(uint32_t i=0u;i<count;++i){uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+i*10u));
   uint32_t first_length=*(volatile uint8_t *)(link+448u);
   uint32_t second=*(volatile uint8_t *)(link+481u);
   uint32_t first=*(volatile uint8_t *)(link+480u);
   uint32_t second_length=*(volatile uint8_t *)(link+444u);
   total+=opencfw_em9305_config_link_time_3185e8(first,second,first_length,second_length);
  }
 }
 return total;
}

static uint32_t ref(uint32_t a,uint32_t b,uint32_t x,uint32_t y,unsigned f,uint32_t h){uint32_t first=a==1?x*8+112:a==2?x*4+60:a==3?f?(x+4)*16+462:(x+4)*64+720:0;uint32_t second=b==1?y*8+112:b==2?y*4+60:b==3?f?(y+4)*16+462:(y+4)*64+720:0;return first+second+h+300;}
int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x813000;unsigned cases=0;
for(unsigned seed=0;seed<128;++seed)for(unsigned count=0;count<256;++count){unsigned expected=0;*(uint8_t*)0x810000=7;*(uint8_t*)0x810014=count;*(uint32_t*)0x810018=0x811000;*(uint8_t*)0x805a86=seed&1?16:0;*(uint16_t*)0x813036=seed*511;calls=0;mutation=seed&2;
for(unsigned i=0;i<count;++i){unsigned slot=(i*17+seed)&255;*(uint8_t*)(uintptr_t)(0x811000+i*10)=slot;uintptr_t link=0x820000u+slot*656;unsigned a=(slot+seed)&7,b=(slot*3+seed)&7,x=(slot*19+seed)&255,y=(slot*23+seed)&255;*(uint8_t*)(link+480)=a;*(uint8_t*)(link+481)=b;*(uint8_t*)(link+448)=x;*(uint8_t*)(link+444)=y;expected+=ref(a,b,x,y,seed&1,seed*511);}
if(opencfw_em9305_config_basic_link_sum_3185a8(0x810000)!=expected||calls!=count)return 3;
++cases;}
printf("PASS %u\n",cases);}
