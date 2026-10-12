#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_3212f0(uintptr_t,uint32_t);
static unsigned special,slot_calls,fallback;
static uint32_t slot_zero(uintptr_t context,uint32_t event)
{ assert(context==0x810000u && event==0x51u);++slot_calls;return 0u; }
static uint32_t slot_accept(uintptr_t context,uint32_t event)
{ assert(context==0x810000u && event==0x51u);++slot_calls;return 0x88u; }
uint32_t opencfw_em9305_mode_event_323374(uintptr_t context)
{ assert(context==0x810000u);++special;return 0x77u; }
uint32_t opencfw_em9305_mode_event_31c420(uintptr_t context,uint32_t event)
{ assert(context==0x810000u && event==0x51u);++fallback;return 0x99u; }
int main(void)
{
 assert((uintptr_t)slot_zero<=UINT32_MAX && (uintptr_t)slot_accept<=UINT32_MAX);
 assert(mmap((void *)0x800000u,0x10000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                   MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(ctx!=(void *)-1);
 ctx[526]=1u;
 assert(opencfw_em9305_mode_event_3212f0((uintptr_t)ctx,0x1cu)==0x77u);
 assert(special==1u && slot_calls==0u && fallback==0u);
 *(volatile uint32_t *)(uintptr_t)(0x803d28u+4u*2u)=(uint32_t)(uintptr_t)slot_zero;
 *(volatile uint32_t *)(uintptr_t)(0x803d28u+4u*10u)=(uint32_t)(uintptr_t)slot_accept;
 assert(opencfw_em9305_mode_event_3212f0((uintptr_t)ctx,0x51u)==0x88u);
 assert(slot_calls==2u && fallback==0u);
 *(volatile uint32_t *)(uintptr_t)(0x803d28u+4u*10u)=0u;
 assert(opencfw_em9305_mode_event_3212f0((uintptr_t)ctx,0x51u)==0x99u);
 assert(slot_calls==3u && fallback==1u);
 return 0;
}
