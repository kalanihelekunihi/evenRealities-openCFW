#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_secondary_fill_324768(uintptr_t,uint8_t *);
extern uint32_t opencfw_em9305_init_secondary_event_30e928(uint32_t,uint32_t,uint8_t *,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_action_319094(uintptr_t,uint32_t,uint32_t);
static uint8_t captured[28];static unsigned notified;static uintptr_t current;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,(int)v,n);}
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t p,uint32_t lo,uint32_t hi){for(unsigned j=0;j<4;j++)((uint8_t *)p)[j]=(uint8_t)(lo>>(8*j));((uint8_t *)p)[4]=(uint8_t)hi;((uint8_t *)p)[5]=(uint8_t)(hi>>8);return p;}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t p,uintptr_t q){memcpy((void *)p,(void *)q,6);return p;}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){memcpy(captured,(void *)p,28);return 0x1234u;}
uint32_t opencfw_em9305_init_secondary_notify_313354(uintptr_t p){assert(p==current+48);assert(*(uint8_t *)(current+4)==0&&*(uint8_t *)(current+3)==1);notified++;return 99;}
static uint16_t half(unsigned off){uint16_t n;memcpy(&n,captured+off,2);return n;}
int main(void){
 assert(mmap((void *)0x800000u,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
 const uint32_t times[]={0u,1u,0x7fffffffu,0xffffffffu};unsigned cases=0;
 for(unsigned index=0;index<6;index++)for(unsigned t=0;t<4;t++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned active=0;active<2;active++){
  current=0x803d78u+index*784u;memset((void *)current,0,784);
  *(uint32_t *)(current+252)=times[t];*(uint32_t *)(current+720)=0x44332211u;*(uint32_t *)(current+724)=0x6655u;
  *(uint8_t *)(current+716)=7;*(uint8_t *)(current+717)=8;*(uint8_t *)(current+776)=9;*(uint8_t *)(current+256)=10;
  *(uint8_t *)(current+512)=11;*(uint8_t *)(current+513)=12;*(uint8_t *)(current+514)=13;*(uint8_t *)(current+515)=14;*(uint8_t *)(current+777)=(uint8_t)enabled;
  uint8_t response[20];memset(response,0xa5,20);assert(opencfw_em9305_init_secondary_fill_324768(current,response)==14);
  assert(response[0]==7&&response[1]==8&&memcmp(response+2,"\x11\x22\x33\x44\x55\x66",6)==0);
  uint16_t scaled;memcpy(&scaled,response+10,2);assert(scaled==(uint16_t)(((uint64_t)times[t]*0x1a36e3u)>>31));
  assert(response[8]==9&&response[9]==0&&response[12]==10&&response[13]==11&&response[14]==12&&response[15]==13&&response[16]==14&&response[17]==0&&response[18]==0xa5);
  *(uint32_t *)0x8051b8u=(uint32_t)current;*(uint8_t *)0x8051a5u=(uint8_t)active;
  unsigned before=notified;assert(opencfw_em9305_init_secondary_action_319094(1,2,3)==0x1234u);assert(notified==before+active&&*(uint8_t *)0x8051a5u==0);
  uint32_t header;memcpy(&header,captured,4);assert(header==0x1e0000u&&captured[4]==62&&half(6)==index&&half(8)==0x0807u);
  assert(memcmp(captured+10,response+2,6)==0&&captured[16]==9&&half(18)==scaled&&captured[20]==10&&captured[21]==(enabled?11:0)&&half(22)==0x0d0cu&&captured[24]==14);cases++;
 }
 printf("PASS %u native-field and state-action contract cases\n",cases);return 0;
}
