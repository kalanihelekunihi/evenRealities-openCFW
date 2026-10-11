#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,mutate;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t p,uintptr_t q){assert(p==0x880000+1077&&memcmp((void *)q,"\5\0\0\0\42",5)==0);assert(*(uint16_t *)(0x850000+76)==15);calls++;if(mutate)*(uint32_t *)(0x880000+2812)=0x851000;return 17;}
uint32_t opencfw_em9305_radio_encode_323c94(uintptr_t p,uintptr_t q){assert(p==0x880000+1079&&q==(mutate?0x851000:0x850000)+100);calls++;return 19;}
uint32_t opencfw_em9305_radio_transfer_31dd88(uintptr_t p,uintptr_t q,uintptr_t r){assert(p==0x840000+912*3&&q==(mutate?0x851000:0x850000)+100&&r==0x880000);assert(*(uint16_t *)(r+528)==36&&*(uint8_t *)(r+688)==1);calls++;return 77;}
uint32_t opencfw_em9305_radio_encode_324594(uintptr_t p,uintptr_t q,uintptr_t r,uint32_t n){assert(p==0x880000&&q==p+1077&&r==p+1144&&n==1);calls++;return 0x12345;}
/* Authenticated stock334474..334479, five-byte event template. */
static const uint8_t opencfw_em9305_radio_event_334474[5]={5u,0u,0u,0u,34u};
/* Native32d7f4..32d910: complete control/payload branches, fresh pointer
 * reads after child calls, explicit bitshift modulo64 and ordered stores. */
uint32_t opencfw_em9305_radio_callback_32d7f4(uintptr_t record)
{
 uintptr_t control=*(volatile uint32_t *)(record+2812u);
 uintptr_t context=record+428u;
 if(*(volatile uint8_t *)(control+77u)!=0u){
  uint8_t event[5];
  (void)opencfw_em9305_memcpy(event,opencfw_em9305_radio_event_334474,5u);
  *(volatile uint16_t *)(control+76u)=15u;
  uint32_t first=opencfw_em9305_radio_encode_3239d4(record+1077u,(uintptr_t)event);
  control=*(volatile uint32_t *)(record+2812u);
  uint32_t second=opencfw_em9305_radio_encode_323c94(record+1079u,control+100u);
  control=*(volatile uint32_t *)(record+2812u);
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uint32_t id=*(volatile uint16_t *)(control+94u),offset;
  *(volatile uint16_t *)(context+100u)=(uint16_t)(first+second);
  offset=id*912u;
  *(volatile uint8_t *)(context+260u)=1u;
  return opencfw_em9305_radio_transfer_31dd88(base+offset,control+100u,record);
 }
 uint32_t index=*(volatile uint8_t *)(record+799u)&127u;
 uintptr_t buffer=*(volatile uint32_t *)(context+732u);
 uintptr_t slot=buffer+3852u+index;
 uint32_t entry_index=*(volatile uint8_t *)slot;
 if(entry_index!=255u&&*(volatile uint8_t *)(buffer+(entry_index<<8))!=0u){
  *(volatile uint8_t *)slot=255u;
  buffer=*(volatile uint32_t *)(context+732u);
  uintptr_t entry=buffer+(entry_index<<8);
  *(volatile uint8_t *)entry=0u;
  uintptr_t destination=*(volatile uint32_t *)(context+720u);
  uint32_t bytes=*(volatile uint8_t *)(entry+1u);
  (void)opencfw_em9305_memcpy((void *)destination,(const void *)(entry+4u),bytes);
  buffer=*(volatile uint32_t *)(context+732u);
  entry=buffer+(entry_index<<8);
  uint32_t length=*(volatile uint8_t *)(entry+1u);
  uint32_t value=*(volatile uint16_t *)(entry+2u);
  *(volatile uint8_t *)(context+261u)=1u;
  *(volatile uint16_t *)(record+1144u)=(uint16_t)length;
  *(volatile uint16_t *)(context+278u)=(uint16_t)value;
  uint32_t shift=entry_index&63u,low=0u,high=0u;
  if(shift<32u) low=1u<<shift;else high=1u<<(shift-32u);
  uint32_t prior_low=*(volatile uint32_t *)(buffer+3844u);
  uint32_t prior_high=*(volatile uint32_t *)(buffer+3848u);
  *(volatile uint32_t *)(buffer+3844u)=low|prior_low;
  *(volatile uint32_t *)(buffer+3848u)=high|prior_high;
 }else *(volatile uint8_t *)(context+261u)=3u;
 uint32_t result=opencfw_em9305_radio_encode_324594(record,record+1077u,record+1144u,1u);
 *(volatile uint16_t *)(context+100u)=(uint16_t)result;
 return result;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned scenario=0;scenario<7;scenario++){memset((void *)0x800000,0,0x100000);uintptr_t r=0x880000,control=0x850000,buffer=0x860000;calls=0;mutate=scenario==6;
*(uint32_t *)(r+2812)=control;*(uint32_t *)(r+1160)=buffer;*(uint32_t *)(r+1148)=0x830000;*(uint32_t *)0x805c70=0x840000;*(uint16_t *)(control+94)=3;*(uint16_t *)(0x851000+94)=3;*(uint8_t *)(r+799)=130;
*(uint8_t *)(control+77)=scenario==0||scenario==6;unsigned index=scenario==4?33:scenario==5?65:1;*(uint8_t *)(buffer+3854)=scenario==1?255:index;uintptr_t entry=buffer+index*256;*(uint8_t *)entry=scenario==2?0:1;*(uint8_t *)(entry+1)=8;*(uint16_t *)(entry+2)=0x3210;for(unsigned i=0;i<8;i++)*(uint8_t *)(entry+4+i)=i+1;
*(uint32_t *)(buffer+3844)=4;*(uint32_t *)(buffer+3848)=8;
unsigned expected=scenario==0||scenario==6?77:0x12345;assert(opencfw_em9305_radio_callback_32d7f4(r)==expected);assert(calls==(scenario==0||scenario==6?3:1));
if(scenario!=0&&scenario!=6){assert(*(uint16_t *)(r+528)==0x2345);if(scenario==1||scenario==2){assert(*(uint8_t *)(r+689)==3);assert(*(uint32_t *)(buffer+3844)==4&&*(uint32_t *)(buffer+3848)==8);}else{assert(*(uint8_t *)(r+689)==1&&*(uint16_t *)(r+1144)==8&&*(uint16_t *)(r+706)==0x3210);assert(*(uint8_t *)entry==0&&*(uint8_t *)(buffer+3854)==255);for(unsigned i=0;i<8;i++)assert(*(uint8_t *)(uintptr_t)(0x830000+i)==i+1);uint64_t mask=(8ULL<<32)|4ULL;mask|=1ULL<<(index&63);assert(*(uint32_t *)(buffer+3844)==(uint32_t)mask&&*(uint32_t *)(buffer+3848)==(uint32_t)(mask>>32));}}
cases++;}printf("PASS %u\n",cases);}
