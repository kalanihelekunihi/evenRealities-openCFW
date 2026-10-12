#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls;
static uint32_t opencfw_em9305_associated_random_31896c(void){calls++;return 1;}
static uint32_t opencfw_em9305_config_link_mpywhul(uint32_t a,uint32_t b){return a*(uint16_t)b;}
#include "associated-packet-channel-prepared.c"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uintptr_t r=0x802000;unsigned cases=0;
 for(unsigned previous=0;previous<256;previous++)for(unsigned selected=0;selected<37;selected++){
  *(uint8_t *)(r+697)=(uint8_t)previous;calls=0;
  uint64_t mask=UINT64_C(1)<<selected;*(uint32_t *)(uintptr_t)0x805aa0=(uint32_t)mask;*(uint32_t *)(uintptr_t)0x805aa4=(uint32_t)(mask>>32);
  unsigned expected=0,channel=previous;do{channel=(channel+1)%37;expected++;}while(channel!=selected);
  uint32_t result=opencfw_em9305_associated_packet_refill_3259fc(r);
  if(result!=1||calls!=expected||*(uint8_t *)(r+697)!=selected||*(uint8_t *)(r+696)!=1)abort();
  cases++;
 }
 printf("PASS %u bounded rejection-channel cases; ARC runtime unqualified\n",cases);
}
