#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t args[9];
static uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t r,uint32_t mode,uint32_t flags,uint32_t zero,uintptr_t header,uintptr_t size,uintptr_t payload,uint32_t type,uint32_t count){uint8_t expected[5]={7,0,0,0,0};if(memcmp((void *)header,expected,5)||(header&3))abort();uint32_t capture[9]={(uint32_t)r,mode,flags,zero,0,(uint32_t)size,(uint32_t)payload,type,count};memcpy(args,capture,sizeof args);return 0xabcd;}
#include "associated-packet-builders-prepared.c"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;uintptr_t r=0x802000;
 for(unsigned flags=0;flags<256;flags++)for(unsigned count=0;count<256;count++){
  *(uint8_t *)(r+32)=(uint8_t)flags;
  if(opencfw_em9305_associated_packet_continue_323ac8(r,0x803000,0x804000,count)!=0xabcd||args[0]!=r||args[1]!=(count==0&&!(flags&2)?8:0)||args[2]!=16||args[3]||args[5]!=0x804000||args[6]!=0x803000||args[7]!=5||args[8]!=count)abort();
  cases++;
 }
 for(unsigned mode=0;mode<256;mode++)for(unsigned enabled=0;enabled<256;enabled++)for(unsigned policy=0;policy<2;policy++){
  *(uint32_t *)(uintptr_t)0x805a98=policy?0xffffffff:0;*(uint8_t *)(r+716)=(uint8_t)mode;*(uint8_t *)(r+804)=(uint8_t)enabled;
  uint32_t expected=(uint8_t)((policy?8:0)|(mode&64)|(enabled*4)|16);
  if(opencfw_em9305_associated_packet_start_3243e0(r,0x803000,0x804000,0x12345678)!=0xabcd||args[1]||args[2]!=expected||args[3]||args[7]!=4||args[8]!=0x12345678)abort();
  cases++;
 }
 printf("PASS %u captured packet-builder argument cases; ARC runtime unqualified\n",cases);
}
