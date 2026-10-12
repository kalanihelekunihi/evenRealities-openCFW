#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){uintptr_t c=*(volatile uint32_t*)0x805c18;return *(volatile uint16_t*)(c+6);}
static uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b){int32_t v=(int32_t)(a-b);return v<0?0:(uint32_t)v;}
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t b){return (a&65535)*(b&65535);}
/* Native314370..3143f4: captured parent/now, guard addition in the call
 * delay slot, mode overhead and sparse accumulator update. */
uint32_t opencfw_em9305_radio_schedule_314370(uintptr_t object,uintptr_t record,uint32_t now,uint32_t guard)
{
 uint32_t initial=*(volatile uint32_t *)(object+12u);
 uintptr_t parent=*(volatile uint32_t *)(object+44u);
 uintptr_t accumulator=record+164u;
 uint32_t overhead=initial+guard;
 overhead+=opencfw_em9305_auxiliary_guard_interval();
 uint32_t mode=*(volatile uint8_t *)(parent+13u);
 if(mode==3u)overhead+=336u;else if(mode==2u)overhead+=24u;else if(mode==1u)overhead+=40u;
 uint32_t used=*(volatile uint32_t *)accumulator;
 uint32_t available=*(volatile uint32_t *)(object+16u);
 if(available<used+overhead){*(volatile uint32_t *)accumulator=available;return 0u;}
 uintptr_t next=*(volatile uint32_t *)(object+4u);
 uint32_t remaining=available-used;
 if(next!=0u){
  uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(*(volatile uint32_t *)(next+8u),now);
  if(remaining<elapsed)elapsed=remaining;
  if(elapsed<overhead){*(volatile uint32_t *)accumulator=*(volatile uint32_t *)accumulator+elapsed;return 0u;}
  remaining=elapsed;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805c18u;
 uint32_t cap=opencfw_em9305_config_limit_mpyuw(*(volatile uint16_t *)(config+4u),1000u);
 uint32_t room=remaining-overhead;
 return room<cap?room:cap;
}

int main(void){if(mmap((void*)0x800000,131072,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;uintptr_t o=0x810000,r=o+128,parent=o+512,next=o+576,cfg=o+640;*(uint32_t*)0x805c18=cfg;uint32_t vals[]={0,1000,0xffffffffu},caps[]={0,1,65535};unsigned cases=0,fail=0;
 for(unsigned mode=0;mode<256;mode++)for(unsigned a=0;a<3;a++)for(unsigned b=0;b<3;b++)for(unsigned c=0;c<3;c++)for(unsigned d=0;d<3;d++)for(unsigned e=0;e<3;e++)for(unsigned n=0;n<2;n++)for(unsigned k=0;k<3;k++){
  memset((void*)o,0xa5,64);memset((void*)r,0xa5,196);*(uint32_t*)(o+12)=vals[a];*(uint32_t*)(o+16)=vals[b];*(uint32_t*)(o+44)=parent;*(uint32_t*)(o+4)=n?next:0;*(uint8_t*)(parent+13)=mode;*(uint32_t*)(r+164)=vals[c];*(uint32_t*)(next+8)=vals[d];*(uint16_t*)(cfg+4)=caps[k];*(uint16_t*)(cfg+6)=17;
  uint8_t expected[196],obj[64];memcpy(expected,(void*)r,196);memcpy(obj,(void*)o,64);uint32_t used=vals[c],available=vals[b],overhead=vals[a]+vals[e]+17;
  if(mode==1)overhead+=40;else if(mode==2)overhead+=24;else if(mode==3)overhead+=336;uint32_t want;
  if(available<used+overhead){*(uint32_t*)(expected+164)=available;want=0;}else{uint32_t room=available-used;if(n){uint32_t delta=vals[d]-73;uint32_t dt=(delta&0x80000000u)?0:delta;if(room>dt)room=dt;}
   if(n&&room<overhead){*(uint32_t*)(expected+164)=used+room;want=0;}else {room-=overhead;uint32_t cap=caps[k]*1000;want=room>cap?cap:room;}}
  uint32_t got=opencfw_em9305_radio_schedule_314370(o,r,73,vals[e]);
  if(got!=want||memcmp(expected,(void*)r,196)||memcmp(obj,(void*)o,64))fail++;cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
