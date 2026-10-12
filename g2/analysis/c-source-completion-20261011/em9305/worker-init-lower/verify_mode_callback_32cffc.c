#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_callback_32cffc(uintptr_t,uintptr_t);
static uintptr_t allocated;
static unsigned allocations,sends,timings;
static uint32_t sent_handler;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes)
{ assert(bytes==8u);++allocations;return allocated; }
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t event)
{ assert(event==0x820000u);sent_handler=handler;++sends;return 0x55u; }
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t bytes,uint32_t unit)
{ assert(bytes==800u&&unit==0x123u);++timings;return 0x234u; }
int main(void)
{
    uint8_t *g=mmap((void *)0x802000u,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *event=mmap((void *)0x820000u,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(g!=(void *)-1&&root!=(void *)-1&&ctx!=(void *)-1&&event!=(void *)-1);
    *(uint32_t *)(g+0x81cu)=0x6a8u; /* bits 9 and 10 */
    *(uint32_t *)(g+0x820u)=0x1befu;
    *(uint32_t *)(root+0xa98u)=0xffffffffu;
    *(uint32_t *)(root+0xa94u)=0xffffffffu;
    ctx[2]=2u;
    assert(opencfw_em9305_mode_callback_32cffc((uintptr_t)ctx,0)==0u);
    assert(ctx[534]==1u&&*(uint32_t *)(ctx+540u)==0x1befu);
    assert(*(uint32_t *)(ctx+536u)==(0x6a8u&0xf787cf2fu));
    assert(ctx[81]==1u&&ctx[80]==1u);
    assert(allocations==0u&&timings==0u);
    ctx[2]=0u;ctx[565]=0u;ctx[6]=4u;
    *(uint32_t *)(g+0x820u)=0x1befu;
    *(uint32_t *)(root+0xc70u)=(uint32_t)(uintptr_t)ctx;
    *(uint32_t *)(root+0xcacu)=(uint32_t)(uintptr_t)root;
    root[68]=2u;
    root[0xb18u]=0x7bu;
    allocated=(uintptr_t)event;
    assert(opencfw_em9305_mode_callback_32cffc((uintptr_t)ctx,0)==0u);
    assert(allocations==1u&&sends==1u&&sent_handler==0x7bu);
    assert(*(uint16_t *)(event+2u)==0x6c01u&&event[4]==1u);
    assert(*(uint16_t *)event==0u&&event[5]==0x96u&&event[6]==0x96u);
    root[68]=6u;
    assert(opencfw_em9305_mode_callback_32cffc((uintptr_t)ctx,0)==0u);
    assert(event[5]==6u&&event[6]==6u);
    root[0xa85u]=0u;ctx[770]=1u;ctx[769]=0u;
    assert(opencfw_em9305_mode_callback_32cffc((uintptr_t)ctx,0)==800u);
    assert(timings==0u);
    ctx[770]=1u;ctx[769]=0u;root[0xa85u]=0x80u;
    *(uint16_t *)(ctx+532u)=0x123u;
    assert(opencfw_em9305_mode_callback_32cffc((uintptr_t)ctx,0)==0x234u);
    assert(ctx[772]==0x34u&&timings==1u);
    return 0;
}
