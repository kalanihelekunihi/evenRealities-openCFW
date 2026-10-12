#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned copies,updates,inserts,reports,cleanups;
static uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t record,uint32_t action){if(record!=0x802000||action!=3)abort();cleanups++;return 0x9876;}
static void *opencfw_em9305_memcpy(void *out,const void *in,uint32_t n){copies++;return memcpy(out,in,n);}
static uint32_t opencfw_em9305_associated_report_30e89c(uint32_t id,uint32_t count,uint32_t zero,uint32_t spacing,uint32_t stamp){if(id!=7||zero||spacing!=625||stamp!=100||count!=*(uint16_t *)(uintptr_t)0x8022f0)abort();reports++;return 99;}
static uint32_t opencfw_em9305_associated_channel_pending_327af4(uintptr_t record){updates++;*(uint16_t *)(record+752)=(uint16_t)(*(uint16_t *)(record+752)+3);return 0;}
static uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t channels,uint32_t count){if(channels!=0x8022d0||count!=*(uint16_t *)(uintptr_t)0x8022f0)abort();return count^0x1ff;}
static uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,uint32_t zero){if(object!=0x804000||zero)abort();inserts++;return inserts==3?0x5555:0;}
#include "associated-radio-callback-host-port.inc"
int main(void){
 if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;
 for(unsigned seed=0;seed<65536;seed++)for(unsigned stop=0;stop<2;stop++){
  uintptr_t r=0x802000,o=0x804000,p=0x804200;
  memset((void *)r,0,3000);memset((void *)o,0,1024);copies=updates=inserts=reports=cleanups=0;
  *(uint32_t *)(o+36)=(uint32_t)r;*(uint32_t *)(o+44)=(uint32_t)p;*(uint32_t *)(o+8)=100;
  *(uint8_t *)(r+1)=7;*(uint32_t *)(r+700)=625;*(uint16_t *)(r+752)=(uint16_t)seed;*(uint8_t *)(r+698)=(uint8_t)stop;
  *(uint8_t *)(p+15)=(uint8_t)seed;*(uint8_t *)(uintptr_t)0x805bed=42;*(uint8_t *)(uintptr_t)0x805bee=seed&1;
  *(uint8_t *)(r+1164)=seed&1;*(uint8_t *)(r+1165)=5;*(uint16_t *)(r+1166)=123;*(uint32_t *)(r+1148)=0x803000;
  for(unsigned j=0;j<5;j++)*(uint8_t *)(r+1168+j)=(uint8_t)(seed+j);
  uint32_t result=opencfw_em9305_associated_radio_callback_32b538(o);
  if(stop){if(result!=0x9876||cleanups!=1||copies||updates||inserts||reports)abort();}
  else{
   if(result!=0x5555||updates!=3||inserts!=3||cleanups||copies!=(seed&1)||reports!=(seed&1))abort();
   if(*(uint16_t *)(r+752)!=(uint16_t)(seed+12)||*(uint32_t *)(o+8)!=1975||*(uint32_t *)(o+20)!=625)abort();
   if(*(uint8_t *)(r+697)!=(uint8_t)((uint16_t)(seed+12)^0x1ff))abort();
   if(*(uint8_t *)(p+14)!=((uint8_t)seed?(uint8_t)seed:42))abort();
   if((seed&1)&&(*(uint8_t *)(r+1164)||*(uint16_t *)(r+1144)!=5||*(uint16_t *)(r+706)!=123||memcmp((void *)0x803000,(void *)(r+1168),5)))abort();
  }
  cases++;
 }
 printf("PASS %u controlled callback cases; ARC runtime unqualified\n",cases);
}
