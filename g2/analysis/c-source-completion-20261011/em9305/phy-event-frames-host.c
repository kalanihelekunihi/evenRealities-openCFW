#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
/* Native3232dc/32317c reserve their original event frames before C executes.
 * Untouched native stack bytes remain untouched, never zero-initialized. */
static inline uint32_t opencfw_em9305_phy_event_index(uintptr_t record)
{int32_t delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c70u);int32_t index=delta/912;return (uint8_t)index;}
uint32_t opencfw_em9305_phy_response_frame_3232dc(uintptr_t record,uint32_t reason,uintptr_t event)
{
 uint32_t index=opencfw_em9305_phy_event_index(record);
 *(volatile uint8_t *)(event+4u)=(uint8_t)reason;
 *(volatile uint8_t *)(event+3u)=(uint8_t)reason;
 uint32_t mode=*(volatile uint16_t *)(record+76u);
 *(volatile uint8_t *)(event+2u)=22u;
 *(volatile uint16_t *)(event+8u)=(uint16_t)mode;
 *(volatile uint16_t *)(event+6u)=(uint16_t)index;
 *(volatile uint16_t *)event=(uint16_t)index;
 return opencfw_em9305_ll_event_callback_30e79c(event);
}
uint32_t opencfw_em9305_phy_length_frame_32317c(uintptr_t record,uint32_t reason,uintptr_t event)
{
 uint32_t index=opencfw_em9305_phy_event_index(record);
 *(volatile uint8_t *)(event+3u)=(uint8_t)reason;
 *(volatile uint8_t *)(event+2u)=18u;
 uint32_t a=*(volatile uint16_t *)(record+578u),b=*(volatile uint16_t *)(record+580u);
 *(volatile uint16_t *)(event+6u)=(uint16_t)a;
 uint32_t c=*(volatile uint16_t *)(record+574u),d=*(volatile uint16_t *)(record+576u);
 *(volatile uint16_t *)(event+8u)=(uint16_t)b;
 *(volatile uint16_t *)(event+10u)=(uint16_t)c;
 *(volatile uint16_t *)(event+12u)=(uint16_t)d;
 *(volatile uint16_t *)(event+4u)=(uint16_t)index;
 *(volatile uint16_t *)event=(uint16_t)index;
 return opencfw_em9305_ll_event_callback_30e79c(event);
}
static uintptr_t seen;
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){seen=p;return 0x98765432u;}
int main(void){
 if(mmap((void*)0x805000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[600] __attribute__((aligned(4))),event[16] __attribute__((aligned(4))),expected[16];unsigned cases=0;
 for(int id=-32768;id<32768;id++){
  uint8_t fill=(uint8_t)id;memset(event,fill,sizeof event);memcpy(expected,event,sizeof event);
  *(volatile uint32_t*)0x805c70=(uint32_t)((uintptr_t)r-(uint32_t)(id*912));
  *(uint16_t*)(r+76)=(uint16_t)(id^0x8123);uint32_t reason=(uint32_t)id;
  *(uint16_t*)expected=(uint8_t)id;expected[2]=22;expected[3]=(uint8_t)reason;expected[4]=(uint8_t)reason;*(uint16_t*)(expected+6)=(uint8_t)id;*(uint16_t*)(expected+8)=*(uint16_t*)(r+76);
  if(opencfw_em9305_phy_response_frame_3232dc((uintptr_t)r,reason,(uintptr_t)event)!=0x98765432u||seen!=(uintptr_t)event||memcmp(event,expected,16))abort();
  cases++;
  memset(event,fill,16);memcpy(expected,event,16);*(uint16_t*)expected=(uint8_t)id;expected[2]=18;expected[3]=(uint8_t)reason;*(uint16_t*)(expected+4)=(uint8_t)id;
  unsigned offsets[4]={578,580,574,576};for(unsigned j=0;j<4;j++){*(uint16_t*)(r+offsets[j])=(uint16_t)(id+j*91);*(uint16_t*)(expected+6+j*2)=*(uint16_t*)(r+offsets[j]);}
  if(opencfw_em9305_phy_length_frame_32317c((uintptr_t)r,reason,(uintptr_t)event)!=0x98765432u||memcmp(event,expected,16))abort();
  cases++;
 }
 printf("PASS %u signed index and ambient frame cases\n",cases);return 0;
}
