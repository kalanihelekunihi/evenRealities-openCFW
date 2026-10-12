#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
/* Native307c5c..307ca8: six active row address/role/kind comparisons. */
uint32_t opencfw_em9305_command_duplicate_307c5c(uint32_t role,uint32_t kind,uint32_t low,uint32_t high)
{
 for(uint32_t i=0u;i<6u;++i){
  uintptr_t offset=i*784u;
  if(*(volatile uint8_t *)(uintptr_t)(0x803d78u+offset)==0u)continue;
  uintptr_t row=0x804044u+offset;
  if(*(volatile uint8_t *)row!=role)continue;
  if(*(volatile uint8_t *)(row+1u)!=kind)continue;
  uint32_t stored_high=*(volatile uint32_t *)(row+8u);
  uint32_t stored_low=*(volatile uint32_t *)(row+4u);
  if(((stored_high^high)|(stored_low^low))==0u)return 1u;
 }
 return 0u;
}

int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;
 for(unsigned mask=0;mask<64;++mask)for(unsigned match=0;match<7;++match)for(unsigned mismatch=0;mismatch<5;++mismatch){
  memset((void *)0x800000,0,0x10000);
  uint32_t role=7,kind=1,low=0x12345678,high=0xabcdef01;
  for(unsigned i=0;i<6;++i){uintptr_t off=i*784u,row=0x804044u+off;
   *(uint8_t *)(0x803d78u+off)=(mask&(1u<<i))?255:0;
   *(uint8_t *)row=role;*(uint8_t *)(row+1)=kind;
   *(uint32_t *)(row+4)=low;*(uint32_t *)(row+8)=high;
   if(i!=match || mismatch){unsigned which=i==match?mismatch-1:i%4;
    if(which==0)++*(uint8_t *)row;
    if(which==1)++*(uint8_t *)(row+1);
    if(which==2)++*(uint32_t *)(row+4);
    if(which==3)++*(uint32_t *)(row+8);
   }
  }
  unsigned expected=match<6 && !mismatch && (mask&(1u<<match));
  if(opencfw_em9305_command_duplicate_307c5c(role,kind,low,high)!=(expected!=0))return 3;
  ++cases;
 }
 for(unsigned n=256;n<65536;++n){
  memset((void *)0x800000,0,0x10000);*(uint8_t *)0x803d78=1;
  *(uint8_t *)0x804044=7;*(uint8_t *)0x804045=1;
  if(opencfw_em9305_command_duplicate_307c5c(n,1,0,0)||opencfw_em9305_command_duplicate_307c5c(7,n,0,0))return 4;
  cases+=2;
 }
 printf("PASS %u\n",cases);return 0;
}
