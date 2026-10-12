#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_child_3191dc(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_319714(uint32_t,uint32_t,uint32_t);
static unsigned mask_cuts;
/* Target selected mask helper contains native DSP ISA; this one child
 * cut is explicitly excluded from numeric-equivalence scope. */
uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t a,uint32_t b){(void)a;(void)b;mask_cuts++;return 2;}
void *opencfw_em9305_memcpy(void *a,const void *b,uint32_t n){return memcpy(a,b,n);}
int main(void){assert(mmap((void *)0x800000u,0x100000u,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);unsigned cases=0;
 const uint8_t wanted[43]={12,8,2,1,1,1,1,2,9,9,1,1,6,2,9,24,24,3,1,1,9,9,3,3,5,3,2,1,35,2,2,36,9,16,4,4,5,5,11,11,4,11,43};
 for(unsigned route=0;route<43;route++)for(unsigned length=0;length<2;length++)for(unsigned mode=0;mode<3;mode++)for(unsigned flags=0;flags<2;flags++){
  memset((void *)0x800000u,0,0x100000u);
  uint8_t *packet=(uint8_t *)0x801000u;packet[0]=length?0x20:0;packet[1]=wanted[route];packet[2]=0xc7;
  unsigned header=length?3:2;packet[header]=(uint8_t)route;
  for(unsigned k=1;k<64;k++)packet[header+k]=(uint8_t)(k*7+3);
  if(route==1)packet[header+5]=1;
  *(uint32_t *)0x805a94u=flags?0xffffffffu:0;*(uint32_t *)0x805a98u=flags?0xffffffffu:0;
  uint32_t result=opencfw_em9305_child_3191dc(0x800000u,0x801000u,mode);
  assert(*(uint8_t *)0x800008u==route&&*(uint8_t *)0x800005u==wanted[route]&&*(uint8_t *)0x800004u==length);
  assert(result==0||result==25||result==30);cases++;
 }
 for(unsigned route=3;route<20;route++)for(unsigned length=0;length<2;length++)for(unsigned mode=0;mode<3;mode++){
  memset((void *)0x800000u,0,0x100000u);uint8_t *packet=(uint8_t *)0x801000u;packet[0]=length?0x20:0;packet[1]=23;packet[2]=0xc7;
  unsigned header=length?3:2;packet[header]=(uint8_t)route;for(unsigned k=1;k<64;k++)packet[header+k]=(uint8_t)(k*7+3);
  *(uint32_t *)0x805a94u=0xffffffffu;
  uint32_t result=opencfw_em9305_child_319714(0x800000u,0x801000u,mode);
  assert(*(uint8_t *)0x800008u==route&&*(uint8_t *)0x800005u==23);
  if(route==3&&mode!=0){assert(result==0&&memcmp((void *)0x80000cu,packet+header+1,8)==0);}else assert(result==0||result==25);
  cases++;
 }
 printf("PASS%u connected-source/header cases; maskDSP child cuts %u\n",cases,mask_cuts);return 0;
}
