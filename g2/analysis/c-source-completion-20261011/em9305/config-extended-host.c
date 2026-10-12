#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned applied,clear_size,phy_valid=1;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){clear_size=n;return memset(p,v,n);}
uint32_t opencfw_em9305_config_phy_pair_valid_332f80(uint32_t a,uint32_t b){(void)a;(void)b;return phy_valid;}
uint32_t opencfw_em9305_config_extended_apply_308a3c(uintptr_t p,uintptr_t o){(void)p;(void)o;++applied;return 0x12345678;}
extern uint32_t opencfw_em9305_config_extended_apply_308a3c(uintptr_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_extended_stride(uint32_t i)
{return i*14u;}
/* Native30d204..30d35a: complete extended validation. Output is cleared before any rejection. */
uint32_t opencfw_em9305_command_config_extended_30d204(uintptr_t input,uintptr_t output)
{
 uint32_t count=*(volatile uint8_t *)(input+19u);
 (void)opencfw_em9305_memset((void *)output,0u,count*2u);
 uint32_t minimum=(*(volatile uint8_t *)(uintptr_t)0x805a86u&128u)?4u:2u;
 if(*(volatile uint8_t *)input>239u)return 48u;
 if((uint32_t)(*(volatile uint32_t *)(input+4u)+0xfff00000u)<0xfff000ffu)return 48u;
 if((uint32_t)(*(volatile uint32_t *)(input+8u)+0xfff00000u)<0xfff000ffu)return 48u;
 if((uint32_t)(*(volatile uint8_t *)(input+12u)-1u)>=31u)return 48u;
 if((uint32_t)(*(volatile uint8_t *)(input+13u)-1u)>=31u)return 48u;
 uint32_t interval=*(volatile uint16_t *)(input+14u);
 if(interval<minimum||interval>=3201u)return 48u;
 if(*(volatile uint8_t *)(input+16u)>=8u||*(volatile uint8_t *)(input+17u)>=2u||*(volatile uint8_t *)(input+18u)>=2u)return 48u;
 count=*(volatile uint8_t *)(input+19u);
 if(count-1u>=16u)return 48u;
 uintptr_t rows=*(volatile uint32_t *)(input+20u);
 for(uint32_t i=0u;i<count;++i){uintptr_t row=rows+opencfw_em9305_config_extended_stride(i);
  if(*(volatile uint8_t *)row>239u)return 48u;
  if(*(volatile uint16_t *)(row+2u)>4095u||*(volatile uint16_t *)(row+4u)>4095u)return 48u;
  if(*(volatile uint16_t *)(row+6u)>4091u||*(volatile uint16_t *)(row+8u)>4091u)return 48u;
  if(*(volatile uint8_t *)(row+10u)==0u||*(volatile uint8_t *)(row+11u)==0u)return 48u;
  if(*(volatile uint8_t *)(row+12u)>=16u||*(volatile uint8_t *)(row+13u)>=16u)return 48u;
 }
 uint32_t limit=*(volatile uint8_t *)(rows+1u);
 if(limit<*(volatile uint8_t *)(rows+12u)||limit<*(volatile uint8_t *)(rows+13u))return 48u;
 uint32_t i=0u;
 do {rows=*(volatile uint32_t *)(input+20u);uintptr_t row=rows+i*14u;
  uint32_t second=*(volatile uint8_t *)(row+11u),first=*(volatile uint8_t *)(row+10u);
  if(opencfw_em9305_config_phy_pair_valid_332f80(first,second)==0u)return 17u;
  if(*(volatile uint8_t *)(row+10u)>=8u||*(volatile uint8_t *)(row+11u)>=8u)return 17u;
  ++i;count=*(volatile uint8_t *)(input+19u);
 }while(i<count);
 if(count){rows=*(volatile uint32_t *)(input+20u);
  for(i=0u;i<count;++i){uintptr_t row=rows+opencfw_em9305_config_extended_stride(i);
   if(*(volatile uint8_t *)(row+12u)&&*(volatile uint16_t *)(row+2u)==0u)return 18u;
   if(*(volatile uint8_t *)(row+13u)&&*(volatile uint16_t *)(row+4u)==0u)return 18u;
  }
 }
 return opencfw_em9305_config_extended_apply_308a3c(input,output);
}

static void reset(void){memset((void*)0x810000,0,0x4000);*(uint32_t*)0x810004=255;*(uint32_t*)0x810008=255;*(uint8_t*)0x81000c=1;*(uint8_t*)0x81000d=1;*(uint16_t*)0x81000e=2;*(uint8_t*)0x810013=1;*(uint32_t*)0x810014=0x811000;*(uint8_t*)0x811001=15;*(uint8_t*)0x81100a=1;*(uint8_t*)0x81100b=1;*(uint8_t*)0x805a86=0;applied=clear_size=0;phy_valid=1;}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned cap=0;cap<2;++cap)for(unsigned v=0;v<65536;++v){reset();*(uint8_t*)0x805a86=cap?128:0;*(uint16_t*)0x81000e=v;unsigned expected=(v>=(cap?4:2)&&v<3201)?0x12345678:48;if(opencfw_em9305_command_config_extended_30d204(0x810000,0x812000)!=expected||clear_size!=2)return 3;++cases;}
for(unsigned off=0;off<4;++off)for(unsigned v=0;v<65536;++v){reset();*(uint16_t*)(uintptr_t)(0x811002+off*2)=v;unsigned expected=v<=(off<2?4095:4091)?0x12345678:48;if(opencfw_em9305_command_config_extended_30d204(0x810000,0x812000)!=expected)return 4;++cases;}
for(unsigned v=0;v<256;++v){reset();*(uint8_t*)0x810013=v;for(unsigned j=1;j<16;++j)memcpy((void*)(uintptr_t)(0x811000+j*14),(void*)0x811000,14);unsigned expected=(v>=1&&v<=16)?0x12345678:48;if(opencfw_em9305_command_config_extended_30d204(0x810000,0x812000)!=expected||clear_size!=v*2)return 5;++cases;}
reset();phy_valid=0;if(opencfw_em9305_command_config_extended_30d204(0x810000,0x812000)!=17)return 6;++cases;
reset();*(uint8_t*)0x81100c=1;if(opencfw_em9305_command_config_extended_30d204(0x810000,0x812000)!=18)return 7;++cases;
printf("PASS %u\n",cases);}
