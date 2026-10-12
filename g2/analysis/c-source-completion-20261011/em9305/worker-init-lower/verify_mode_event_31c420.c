#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_31c420(uintptr_t,uint32_t);
static unsigned notified,rejected,responded;
uint32_t opencfw_em9305_init_response_packet_326a84(uintptr_t c)
{assert(c==0x810000u);++responded;return 0x91u;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t c,uint32_t reason,uint32_t x)
{assert(c==0x810000u&&reason==30u&&x==0u);++rejected;return 0x92u;}
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t p)
{assert(p==0x810010u);++notified;return 0x93u;}
uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t c)
{*(volatile uint8_t *)(c+12u)=0x22u;return (uint32_t)c;}
int main(void)
{
 uint8_t *p=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(p!=(void *)-1);
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,0x99u)==0x810000u);
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,13u)==0x91u);
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,14u)==0x92u);
 assert(responded==1u&&rejected==1u);
 p[1]=1u;p[620]=7u;
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,0x49u)==1u);
 assert(p[12]==0x28u&&p[620]==0u&&p[1]==3u&&notified==0u);
 p[1]=2u;p[620]=7u;
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,0x4au)==0x93u);
 assert(p[12]==0x1eu&&p[620]==0u&&p[1]==3u&&notified==1u);
 p[1]=2u;
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,0x51u)==0x93u);
 assert(p[12]==0x22u&&notified==2u);
 p[1]=2u;
 assert(opencfw_em9305_mode_event_31c420((uintptr_t)p,0x73u)==0x93u);
 assert(p[12]==0x30u&&notified==3u);
 return 0;
}
