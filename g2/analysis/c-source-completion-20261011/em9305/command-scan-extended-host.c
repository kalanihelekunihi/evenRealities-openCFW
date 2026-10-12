#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate;
uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
/* Native307a58/307b8c: ARC dynamic bit index uses low five bits. */
void opencfw_em9305_scan_mask_clear_307a58(uint32_t bit)
{volatile uint8_t *p=(volatile uint8_t *)(uintptr_t)0x803560u;uint32_t v=*p;*p=(uint8_t)(v&~(1u<<(bit&31u)));}
void opencfw_em9305_scan_mask_set_307b8c(uint32_t bit)
{volatile uint8_t *p=(volatile uint8_t *)(uintptr_t)0x803560u;uint32_t v=*p;*p=(uint8_t)(v|(1u<<(bit&31u)));}
/* Native307b70..307b8c: authenticated table, callers supply index0 or2. */
void opencfw_em9305_scan_config_307b70(uint32_t index,uint32_t first,uint32_t second,uintptr_t input)
{
 static const uintptr_t states[3]={0x8035dcu,0x802a60u,0x80389cu};
 uintptr_t row=states[index];
 uint32_t duration=*(volatile uint16_t *)(input+2u),interval=*(volatile uint16_t *)input;
 *(volatile uint8_t *)(row+14u)=(uint8_t)second;
 *(volatile uint16_t *)(row+10u)=(uint16_t)duration;
 uint32_t mode=*(volatile uint8_t *)(input+4u);
 *(volatile uint16_t *)(row+8u)=(uint16_t)interval;
 *(volatile uint8_t *)(row+13u)=(uint8_t)first;
 *(volatile uint8_t *)(row+12u)=(uint8_t)mode;
}
/* Native332fa8..332fc4: interval>=duration>=4, mode<2. */
uint32_t opencfw_em9305_scan_row_valid_332fa8(uintptr_t input)
{
 uint32_t duration=*(volatile uint16_t *)(input+2u),interval=*(volatile uint16_t *)input;
 if(interval<duration||duration<4u)return 0u;
 return *(volatile uint8_t *)(input+4u)<2u;
}
static inline uint32_t opencfw_em9305_scan_stride6(uint32_t value){return value*6u;}
/* Native30d774..30d854: full extended scan guard and compact row graph. */
uint32_t opencfw_em9305_command_scan_extended_30d774(uint32_t first,uint32_t second,uint32_t mask,uintptr_t input)
{
 uintptr_t root=0x805a70u;
 uint32_t cap=*(volatile uint32_t *)(root+36u),cap2=*(volatile uint32_t *)(root+40u);
 uint32_t allowed=(cap&128u)?3u:1u;
 if((cap2&1024u)==0u){if(second&12u)return 17u;}else allowed|=12u;
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 uint32_t state4=*(volatile uint8_t *)(root+4u),state3=*(volatile uint8_t *)(root+3u);
 if(state3|state4)return 12u;
 uint32_t allowed_mask=((cap>>9u)&4u)|1u;
 if(mask&~allowed_mask)return 17u;
 if(first>((cap&64u)?3u:1u))return 18u;
 if((second&12u)==8u||mask==0u||second>allowed)return 18u;
 uint32_t count=0u,row_index=0u,has1=mask&1u,has4=mask&4u;
 if(has1){if(opencfw_em9305_scan_row_valid_332fa8(input)==0u)return 18u;row_index=1u;}
 if(has4&&opencfw_em9305_scan_row_valid_332fa8(input+opencfw_em9305_scan_stride6(row_index))==0u)return 18u;
 if(!has1)opencfw_em9305_scan_mask_clear_307a58(0u);
 else{opencfw_em9305_scan_mask_set_307b8c(0u);opencfw_em9305_scan_config_307b70(0u,first,second,input);count=1u;}
 if(!has4)opencfw_em9305_scan_mask_clear_307a58(2u);
 else{opencfw_em9305_scan_mask_set_307b8c(2u);opencfw_em9305_scan_config_307b70(2u,first,second,input+opencfw_em9305_scan_stride6(count));++count;}
 *(volatile uint8_t *)(root+12u)=(uint8_t)count;
 return 0u;
}

int main(void){
 if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;uintptr_t input=0x806000;
 for(unsigned caps=0;caps<16;++caps)for(unsigned first=0;first<8;++first)for(unsigned second=0;second<32;++second)for(unsigned mask=0;mask<16;++mask)for(unsigned guards=0;guards<8;++guards){
  memset((void*)0x800000,0xa5,0x10000);
  uint32_t cap=((caps&1)?128:0)|((caps&2)?64:0)|((caps&4)?2048:0),cap2=(caps&8)?1024:0;
  *(uint32_t*)0x805a94=cap;*(uint32_t*)0x805a98=cap2;gate=!(guards&1);
  *(uint8_t*)0x805a74=(guards&2)?1:0;*(uint8_t*)0x805a73=(guards&4)?1:0;
  *(uint16_t*)input=8;*(uint16_t*)(input+2)=4;*(uint8_t*)(input+4)=0;
  *(uint16_t*)(input+6)=12;*(uint16_t*)(input+8)=6;*(uint8_t*)(input+10)=1;
  uint8_t before[65536];memcpy(before,(void*)0x800000,sizeof before);
  unsigned expected=0,allowed=((cap&128)?3:1)|((cap2&1024)?12:0);
  if(!(cap2&1024)&&(second&12))expected=17;
  else if(!gate||(guards&6))expected=12;
  else if(mask&~(((cap>>9)&4)|1))expected=17;
  else if(first>((cap&64)?3:1)||(second&12)==8||!mask||second>allowed)expected=18;
  unsigned got=opencfw_em9305_command_scan_extended_30d774(first,second,mask,input);
  if(got!=expected){printf("bad %u %u %u %u %u %u %u\n",caps,first,second,mask,guards,got,expected);return 3;}
  if(expected){if(memcmp(before,(void*)0x800000,sizeof before))return 4;}
  else{
   uint8_t expected_mem[65536];memcpy(expected_mem,before,sizeof before);
   expected_mem[0x3560]=(uint8_t)((0xa5&~5)|(mask&5));unsigned n=0;
   const unsigned rows[]={0x35dc,0x2a60,0x389c};
   for(unsigned i=0;i<3;i+=2)if(mask&(1u<<i)){
    unsigned r=rows[i],v=n?12:8,d=n?6:4,m=n?1:0;
    memcpy(expected_mem+r+8,&v,2);memcpy(expected_mem+r+10,&d,2);
    expected_mem[r+12]=m;expected_mem[r+13]=first;expected_mem[r+14]=second;++n;
   }
   expected_mem[0x5a7c]=n;if(memcmp(expected_mem,(void*)0x800000,sizeof before))return 5;
  }++cases;
 }
 for(unsigned mode=0;mode<256;++mode)for(unsigned d=0;d<16;++d)for(unsigned v=0;v<16;++v){
  *(uint16_t*)input=v;*(uint16_t*)(input+2)=d;*(uint8_t*)(input+4)=mode;
  if(opencfw_em9305_scan_row_valid_332fa8(input)!=(v>=d&&d>=4&&mode<2))return 6;
  ++cases;
 }
 printf("PASS %u\n",cases);return 0;
}
