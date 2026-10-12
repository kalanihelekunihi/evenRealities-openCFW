#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned applied,phy_valid=1,mutation;static uint32_t cleared;
uint32_t opencfw_em9305_config_phy_pair_valid_332f80(uint32_t a,uint32_t b){(void)a;(void)b;if(mutation)*(uint8_t*)0x810014=0;return phy_valid;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){cleared=n;return memset(p,v,n);}
uint32_t opencfw_em9305_config_basic_apply_3087ec(uintptr_t p,uintptr_t o){if(p!=0x810000||o!=0x812000)__builtin_trap();++applied;return 0x123;}
extern uint32_t opencfw_em9305_config_phy_pair_valid_332f80(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_config_basic_apply_3087ec(uintptr_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_basic_stride(uint32_t i){return i*10u;}
static uint32_t opencfw_em9305_config_basic_time(uint32_t length,uint32_t phy)
{
 if(!length)return 0u;
 if(phy==1u)return length*8u+80u;
 if(phy==4u)return length*64u+720u;
 if(phy==2u)return 44u+length*4u;
 return 0u;
}
/* Native30d00c..30d204: complete basic configuration validation, clamp and apply. */
uint32_t opencfw_em9305_command_config_basic_30d00c(uintptr_t input,uintptr_t output)
{
 uint32_t count=*(volatile uint8_t *)(input+20u);
 if(count-1u>=16u)return 18u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(*(volatile uint8_t *)(config+53u)<count)return 9u;
 uintptr_t rows=*(volatile uint32_t *)(input+24u);
 uint32_t first_length=0u,second_length=0u;
 for(uint32_t i=0u;i<count;++i){first_length=*(volatile uint16_t *)(rows+2u+i*10u);if(first_length)break;}
 for(uint32_t i=0u;i<count;++i){second_length=*(volatile uint16_t *)(rows+4u+i*10u);if(second_length)break;}
 if(*(volatile uint8_t *)input>239u)return 18u;
 uint32_t first_time=*(volatile uint32_t *)(input+4u);
 if((first_length&&first_time<255u)||first_time>0xfffffu)return 18u;
 uint32_t second_time=*(volatile uint32_t *)(input+8u);
 if((second_length&&second_time<255u)||second_time>0xfffffu)return 18u;
 if(*(volatile uint8_t *)(input+12u)>=8u)return 18u;
 if(*(volatile uint8_t *)(input+13u)>=2u)return 18u;
 if(*(volatile uint8_t *)(input+14u)>=2u)return 18u;
 for(uint32_t i=0u;i<count;++i){
  uintptr_t row=rows+opencfw_em9305_config_basic_stride(i);
  if(*(volatile uint8_t *)row>239u)return 18u;
  uint32_t a=*(volatile uint16_t *)(row+2u);if(a>4095u)return 18u;
  uint32_t b=*(volatile uint16_t *)(row+4u);if(b>4095u||(a|b)==0u)return 18u;
  if(*(volatile uint8_t *)(row+6u)==0u)return 17u;
  if(*(volatile uint8_t *)(row+7u)==0u)return 17u;
  if(*(volatile uint8_t *)(row+8u)>=16u)*(volatile uint8_t *)(row+8u)=15u;
  else if(*(volatile uint8_t *)(row+9u)>=16u)*(volatile uint8_t *)(row+9u)=15u;
 }
 uint32_t live_count,i=0u;
 for(;;){
  live_count=*(volatile uint8_t *)(input+20u);
  if(i>=live_count)break;
  rows=*(volatile uint32_t *)(input+24u);
  uintptr_t row=rows+i*10u;
  uint32_t second=*(volatile uint8_t *)(row+7u),first=*(volatile uint8_t *)(row+6u);
  if(opencfw_em9305_config_phy_pair_valid_332f80(first,second)==0u)return 17u;
  first=*(volatile uint8_t *)(row+6u);if(first&~7u)return 17u;
  second=*(volatile uint8_t *)(row+7u);if(second&~7u)return 17u;
  if(((first-1u)&first)!=0u||((second-1u)&second)!=0u)return 17u;
  ++i;
 }
 if(live_count){
  first_time=*(volatile uint32_t *)(input+4u);
  rows=*(volatile uint32_t *)(input+24u);
  for(uint32_t j=0u;j<live_count;++j){uintptr_t row=rows+opencfw_em9305_config_basic_stride(j);
   uint32_t a=*(volatile uint16_t *)(row+2u),ta=0u;
   if(a)ta=opencfw_em9305_config_basic_time(a,*(volatile uint8_t *)(row+6u));
   uint32_t b=*(volatile uint16_t *)(row+4u),tb=0u;
   if(b)tb=opencfw_em9305_config_basic_time(b,*(volatile uint8_t *)(row+7u));
   if(ta>first_time)return 18u;
   if(tb>*(volatile uint32_t *)(input+8u))return 18u;
  }
 }
 if((uint16_t)(*(volatile uint16_t *)(input+16u)-4001u)<61540u)return 18u;
 if((uint16_t)(*(volatile uint16_t *)(input+18u)-4001u)<61540u)return 18u;
 (void)opencfw_em9305_memset((void *)output,0u,live_count*2u);
 return opencfw_em9305_config_basic_apply_3087ec(input,output)&255u;
}

static void reset(void){memset((void*)0x810000,0,64);memset((void*)0x811000,0,160);memset((void*)0x812000,0xa5,40);*(uint32_t*)0x805cac=0x813000;*(uint8_t*)0x813035=255;*(uint8_t*)0x810014=1;*(uint32_t*)0x810018=0x811000;*(uint32_t*)0x810004=0xfffff;*(uint32_t*)0x810008=0xfffff;*(uint16_t*)0x810010=5;*(uint16_t*)0x810012=4000;for(unsigned i=0;i<16;++i){uintptr_t r=0x811000+i*10;*(uint16_t*)(r+2)=1;*(uint16_t*)(r+4)=1;*(uint8_t*)(r+6)=1;*(uint8_t*)(r+7)=1;}applied=0;cleared=999;mutation=0;phy_valid=1;}
static unsigned run(unsigned expected){unsigned r=opencfw_em9305_command_config_basic_30d00c(0x810000,0x812000);if(r!=expected||applied!=(expected==0x23)){printf("bad %u %u\n",r,expected);return 1;}return 0;}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
 for(unsigned v=0;v<65536;++v)for(unsigned which=0;which<2;++which){reset();*(uint16_t*)(uintptr_t)(0x810010+which*2)=v;if(run(v>=5&&v<=4000?0x23:18))return 3;++cases;}
 for(unsigned count=0;count<256;++count)for(unsigned capacity=0;capacity<256;++capacity){reset();*(uint8_t*)0x810014=count;*(uint8_t*)0x813035=capacity;if(run(count<1||count>16?18:capacity<count?9:0x23))return 4;if(applied&&cleared!=count*2)return 5;++cases;}
 for(unsigned a=0;a<256;++a)for(unsigned bv=0;bv<256;++bv){reset();*(uint8_t*)0x811008=a;*(uint8_t*)0x811009=bv;if(run(0x23))return 6;if(*(uint8_t*)0x811008!=(a>=16?15:a)||*(uint8_t*)0x811009!=(a<16&&bv>=16?15:bv))return 7;++cases;}
 for(unsigned f=0;f<7;++f)for(unsigned v=0;v<256;++v){reset();const uintptr_t addresses[]={0x810000,0x81000c,0x81000d,0x81000e,0x811000,0x811006,0x811007};*(uint8_t*)addresses[f]=v;unsigned e=0x23;if(f==0||f==4){if(v>239)e=18;}else if(f==1){if(v>=8)e=18;}else if(f==2||f==3){if(v>=2)e=18;}else if(v==0||(v&~7)||(v&(v-1)))e=17;if(run(e))return 8;++cases;}
 for(unsigned v=0;v<65536;++v){reset();*(uint16_t*)0x811002=v;if(run(v>4095?18:0x23))return 9;++cases;}
 const unsigned times[]={0,254,255,783,784,785,1048575,1048576};
 for(unsigned phy=1;phy<=4;phy*=2)for(unsigned w=0;w<2;++w)for(unsigned n=0;n<8;++n){reset();*(uint8_t*)(uintptr_t)(0x811006+w)=phy;*(uint32_t*)(uintptr_t)(0x810004+w*4)=times[n];unsigned required=phy==4?784:255;if(run(times[n]<required||times[n]>1048575?18:0x23))return 12;++cases;}
 reset();phy_valid=0;if(run(17))return 10;++cases;reset();mutation=1;if(run(0x23)||cleared)return 11;++cases;
 printf("PASS %u\n",cases);return 0;}
