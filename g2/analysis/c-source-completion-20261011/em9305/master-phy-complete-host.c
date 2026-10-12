#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t expected;static unsigned response,notify;
uintptr_t opencfw_em9305_phy_record_325250(uintptr_t p){if(p!=expected)abort();return 0x12345678;}
uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t p,uint32_t e){if(p!=expected||e||(*(uint32_t*)(p+636)&(1u<<21))||*(uint32_t*)(p+640))abort();response++;return 99;}
uint32_t opencfw_em9305_phy_length_notify_32317c(uintptr_t p,uint32_t e){if(p!=expected||e)abort();notify++;return 77;}
extern uintptr_t opencfw_em9305_phy_record_325250(uintptr_t);
extern uint32_t opencfw_em9305_phy_length_notify_32317c(uintptr_t,uint32_t);
/* Native315c64..315d3e full post-PHY data-length adjustment. */
uint32_t opencfw_em9305_phy_action_315c64(uintptr_t input)
{
 uintptr_t record=input;
 (void)opencfw_em9305_phy_record_325250(input);
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 if((bits&(1u<<21u))==0u)return bits;
 *(volatile uint32_t *)(record+636u)=bits&~(1u<<21u);
 *(volatile uint32_t *)(record+640u)=0u;
 (void)opencfw_em9305_phy_response_3232dc(record,0u);
 uint32_t mode_first=*(volatile uint8_t *)(record+76u);
 uint32_t old_first=*(volatile uint16_t *)(record+580u);
 uint32_t octets_first=*(volatile uint16_t *)(record+578u),time_first=0u;
 if(mode_first-1u<2u){
  time_first=*(volatile uint16_t *)(record+588u);
  if(time_first!=0u)*(volatile uint16_t *)(record+588u)=0u;
  else{uint32_t limit=octets_first*8u+112u;time_first=limit<old_first?limit:old_first;}
 }else if(mode_first==3u){uint32_t limit=octets_first*64u+976u;time_first=limit<old_first?limit:old_first;}
 uint32_t mode_second=*(volatile uint8_t *)(record+77u);
 uint32_t old_second=*(volatile uint16_t *)(record+576u);
 uint32_t octets_second=*(volatile uint16_t *)(record+574u),time_second=328u;
 if(mode_second-1u<2u){
  uint32_t value=*(volatile uint16_t *)(record+584u);
  if(value!=0u)*(volatile uint16_t *)(record+584u)=0u;
  else{uint32_t limit=octets_second*8u+112u;value=limit<old_second?limit:old_second;}
  if(value>=329u)time_second=value;
 }else if(mode_second==3u){
  uint32_t limit=octets_second*64u+976u,value=limit<old_second?limit:old_second;
  *(volatile uint16_t *)(record+584u)=(uint16_t)old_second;
  time_second=value>2704u?value:2704u;
 }
 *(volatile uint16_t *)(record+576u)=(uint16_t)time_second;
 if(mode_first==3u){*(volatile uint16_t *)(record+588u)=(uint16_t)old_first;if(time_first<2704u)time_first=2704u;}
 else if(time_first<328u)time_first=328u;
 uint32_t feature=*(volatile uint8_t *)(uintptr_t)0x805a94u;
 *(volatile uint16_t *)(record+580u)=(uint16_t)time_first;
 if((feature&32u)!=0u&&(old_first!=time_first||old_second!=time_second))
  return opencfw_em9305_phy_length_notify_32317c(record,0u);
 return feature;
}

int main(void){
 if(mmap((void*)0x805000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[800];expected=(uintptr_t)r;unsigned count=0;
 for(unsigned m1=0;m1<256;m1++)for(unsigned m2=0;m2<256;m2++)for(unsigned cached=0;cached<2;cached++)for(unsigned feature=0;feature<2;feature++){
 memset(r,0,sizeof r);r[76]=m1;r[77]=m2;*(uint16_t*)(r+578)=27;*(uint16_t*)(r+574)=40;*(uint16_t*)(r+580)=1000;*(uint16_t*)(r+576)=2000;*(uint16_t*)(r+588)=cached?777:0;*(uint16_t*)(r+584)=cached?888:0;*(uint32_t*)(r+636)=(1u<<21)|0x123;*(uint32_t*)(r+640)=123;*(volatile uint8_t*)0x805a94=feature?32:0;
 response=notify=0;unsigned first=m1==3?2704:(m1==1||m1==2)&&cached?777:328;unsigned second=m2==3?2704:(m2==1||m2==2)?(cached?888:432):328;
 unsigned result=opencfw_em9305_phy_action_315c64((uintptr_t)r);
 unsigned fc=m1==3?1000:(m1==1||m1==2)?0:cached?777:0;unsigned sc=m2==3?2000:(m2==1||m2==2)?0:cached?888:0;
 if(result!=(feature?77:0)||response!=1||notify!=feature||*(uint16_t*)(r+580)!=first||*(uint16_t*)(r+576)!=second||*(uint16_t*)(r+588)!=fc||*(uint16_t*)(r+584)!=sc||*(uint32_t*)(r+636)!=0x123)abort();
 count++;
 }
 printf("PASS %u post-PHY mode/cache cases\n",count);return 0;
}
