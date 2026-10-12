#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
/* Native policy callback332db4..332e2c, complete selected body. */
uint32_t opencfw_em9305_command_callback_332db4(uintptr_t object,uint32_t event)
{
 uintptr_t state=0x8058dcu;
 uint32_t count=*(volatile uint16_t *)(state+4u);
 uint32_t captured=*(volatile uint8_t *)state;
 uint32_t next=count+1u;
 *(volatile uint16_t *)(state+4u)=(uint16_t)next;
 if(captured!=1u||event==1u)return 0u;
 uint32_t limit=*(volatile uint16_t *)(state+2u);
 if(limit!=0u&&(uint16_t)next>=limit)return 0u;
 uintptr_t record=*(volatile uint32_t *)(object+44u),policy=0x805994u;
 uint32_t channel=*(volatile uint8_t *)(policy+2u);
 uint32_t recorded_channel=*(volatile uint8_t *)(record+1u);
 if(channel!=recorded_channel)return 0u;
 uintptr_t packet=*(volatile uint32_t *)(record+104u);
 uint32_t kind=*(volatile uint8_t *)(policy+1u);
 uint32_t header=*(volatile uint8_t *)packet;
 if(kind!=(header&~32u))return 0u;
 uint32_t packet_pattern=*(volatile uint8_t *)(packet+1u);
 uint32_t pattern=*(volatile uint8_t *)policy;
 if(pattern!=packet_pattern)return 0u;
 uint32_t recorded_mode=*(volatile uint8_t *)(record+12u);
 uint32_t mode=*(volatile uint8_t *)(policy+3u);
 if(mode!=recorded_mode)return 0u;
 uint32_t index=*(volatile uint32_t *)(policy+16u);
 uint32_t bits=*(volatile uint32_t *)(policy+12u);
 uint32_t value=(bits&(1u<<(index&31u)))!=0u?0x555555u:0xaaaaaau;
 *(volatile uint32_t *)(policy+16u)=(index+1u)&31u;
 *(volatile uint32_t *)(record+8u)=value;
 return 1u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x82002c=0x830000;*(uint32_t *)0x830068=0x840000;uint16_t counts[]={0,1,65534,65535};unsigned cases=0;
for(unsigned state=0;state<4;state++)for(unsigned event=0;event<3;event++)for(unsigned ci=0;ci<4;ci++)for(unsigned limit=0;limit<4;limit++)for(unsigned mismatch=0;mismatch<5;mismatch++)for(unsigned index=0;index<34;index++)for(unsigned bits=0;bits<2;bits++){*(uint8_t *)0x8058dc=state;*(uint16_t *)0x8058e0=counts[ci];*(uint16_t *)0x8058de=limit;*(uint8_t *)0x805996=19;*(uint8_t *)0x830001=mismatch==1?18:19;*(uint8_t *)0x805995=5;*(uint8_t *)0x840000=mismatch==2?4:37;*(uint8_t *)0x805994=13;*(uint8_t *)0x840001=mismatch==3?12:13;*(uint8_t *)0x805997=2;*(uint8_t *)0x83000c=mismatch==4?1:2;*(uint32_t *)0x8059a4=index;*(uint32_t *)0x8059a0=bits?0xffffffff:0;*(uint32_t *)0x830008=0x12345678;unsigned next=(uint16_t)(counts[ci]+1);unsigned good=state==1&&event!=1&&(!limit||next<limit)&&!mismatch;assert(opencfw_em9305_command_callback_332db4(0x820000,event)==good);assert(*(uint16_t *)0x8058e0==next&&*(uint32_t *)0x8059a4==(good?(index+1)&31:index)&&*(uint32_t *)0x830008==(good?(bits?0x555555:0xaaaaaa):0x12345678));cases++;}
printf("PASS %u\n",cases);}
