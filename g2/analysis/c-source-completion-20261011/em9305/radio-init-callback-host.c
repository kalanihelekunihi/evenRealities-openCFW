#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t trace[16],n,times,clockfirst,clocksecond,messagecalls;
static uint32_t opencfw_em9305_pal_current_time(void){return times++==0?clockfirst:clocksecond;}
static uint32_t opencfw_em9305_pal_elapsed_raw(uint32_t now,uint32_t start){return now-start;}
uint32_t opencfw_em9305_init_event_dispatch_306c7c(uint32_t i){trace[n++]=i;return 0xcafe;}
uint32_t opencfw_em9305_init_message_3075cc(uintptr_t p){if(p!=0x12345678)abort();messagecalls++;return 0xabcd;}
static void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t z){return memset(p,v,z);}
#include "radio-init-callback-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned vectors=0;for(unsigned mask=0;mask<65536;mask++)for(unsigned msg=0;msg<2;msg++){
 n=times=messagecalls=0;clockfirst=0xffffffe0;clocksecond=mask;uint32_t elapsed=clocksecond-clockfirst;*(uint16_t*)0x8058d8=mask^0xaaaa;if(opencfw_em9305_init_callback_30bf24(mask,msg?0x12345678:0)!=elapsed||times!=2||messagecalls!=msg)abort();unsigned k=0;for(unsigned i=0;i<15;i++)if(mask&(1u<<i)){if(trace[k++]!=i)abort();}if(n!=k||*(uint16_t*)0x8058d8!=(uint16_t)(elapsed>(mask^0xaaaa)?elapsed:mask^0xaaaa))abort();vectors++;
}
for(unsigned v=0;v<65536;v++){uint32_t low=v*0x10203u,high=~low;memset((void*)0x805a70,0xa5,64);*(uint32_t*)0x805b30=low;*(uint32_t*)0x805b34=high;uint8_t ex[64]={0};uint32_t x[16]={0};x[5]=0x46dc40;x[6]=0xfe000000;x[9]=low;x[10]=high;x[12]=~0u;x[13]=31;memcpy(ex,x,64);if(opencfw_em9305_init_state_30e9a4(v)!=low||memcmp((void*)0x805a70,ex,64))abort();vectors++;}printf("PASS %u event/time/state source projections; actual elapsed C; genuine event/message providers controlled\n",vectors);return 0;}
