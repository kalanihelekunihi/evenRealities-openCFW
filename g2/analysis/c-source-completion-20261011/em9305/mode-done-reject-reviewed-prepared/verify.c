#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_done_3234ec(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_reject_3233b4(uintptr_t,uint32_t);
static unsigned child314,child2a8,child374;
static uint32_t last_reason;
uint32_t opencfw_em9305_mode_event_323314(uintptr_t c,uint32_t reason)
{assert(c==0x810000u);last_reason=reason;++child314;return 0x314u;}
uint32_t opencfw_em9305_mode_event_3232a8(uintptr_t c,uint32_t reason)
{assert(c==0x810000u);last_reason=reason;++child2a8;return 0x2a8u;}
uint32_t opencfw_em9305_mode_event_323374(uintptr_t c)
{assert(c==0x810000u);++child374;return 0x374u;}
int main(void)
{
 assert(mmap((void *)0x800000u,0x30000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 uint8_t *c=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(c!=(void *)-1);
 assert(opencfw_em9305_mode_done_3234ec((uintptr_t)c,2u)==0x810000u);
 *(volatile uint32_t *)(c+636u)=1u<<2u;
 *(volatile uint32_t *)(c+640u)=99u;
 assert(opencfw_em9305_mode_done_3234ec((uintptr_t)c,2u)==0x314u);
 assert(child314==1u&&last_reason==0u);
 assert(*(volatile uint32_t *)(c+636u)==0u&&*(volatile uint32_t *)(c+640u)==0u);
 *(volatile uint32_t *)(c+636u)=1u<<3u;
 assert(opencfw_em9305_mode_done_3234ec((uintptr_t)c,3u)==0x374u);
 assert(child374==1u);
 *(volatile uint32_t *)(c+636u)=1u<<7u;
 assert(opencfw_em9305_mode_done_3234ec((uintptr_t)c,7u)==0x2a8u);
 assert(child2a8==1u&&last_reason==0u);
 *(volatile uint32_t *)(c+636u)=1u<<4u;
 *(volatile uint32_t *)(c+544u)=0xffffffffu;
 *(volatile uint8_t *)(uintptr_t)0x802818u=7u;
 assert(opencfw_em9305_mode_reject_3233b4((uintptr_t)c,4u)==0x810000u);
 assert((*(volatile uint32_t *)(c+544u)&(1u<<5u))==0u);
 *(volatile uint32_t *)(c+636u)=1u<<7u;
 assert(opencfw_em9305_mode_reject_3233b4((uintptr_t)c,7u)==0x2a8u);
 assert(child2a8==2u&&last_reason==17u);
 assert((*(volatile uint32_t *)(c+544u)&(1u<<26u))==0u);
 *(volatile uint8_t *)(uintptr_t)0x802818u=13u;
 *(volatile uint8_t *)(uintptr_t)0x80281du=0x55u;
 *(volatile uint32_t *)(c+636u)=1u<<2u;
 assert(opencfw_em9305_mode_reject_3233b4((uintptr_t)c,2u)==0x314u);
 assert(child314==2u&&last_reason==0x55u);
 assert(opencfw_em9305_mode_reject_3233b4((uintptr_t)c,2u)==0x810000u);
 return 0;
}
