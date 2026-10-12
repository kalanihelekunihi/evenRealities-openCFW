#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_event_308664_body(uint32_t,uintptr_t,uint32_t,uint8_t *);
static uint8_t expect[32];
static unsigned call_stage;
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
    assert(call_stage==0);
    /* The native 32-byte stack frame does not initialize bytes 29..31. */
    assert(memcmp((const void *)event,expect,32u)==0);
    call_stage=1;
    return 0xa55aa55au;
}
static void set16(uint8_t *p,uint16_t v)
{ p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8u); }
static void set32(uint8_t *p,uint32_t v)
{ for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(v>>(8u*i)); }
static void run(unsigned include_first,uint32_t period,uint16_t shift)
{
    const uintptr_t record=(uintptr_t)0x803d78u+784u*3u;
    set32((uint8_t *)(record+252u),period);
    set16((uint8_t *)(record+716u),shift);
    *(uint8_t *)(record+32u)=0xe1u; /* Reject unscaled ADD3 immediate. */
    *(uint8_t *)(record+256u)=0x37u;
    *(uint8_t *)(record+776u)=0x42u;
    *(uint8_t *)(record+512u)=0x51u;
    *(uint8_t *)(record+513u)=0x52u;
    *(uint8_t *)(record+514u)=0x53u;
    *(uint8_t *)(record+515u)=0x54u;
    set32((uint8_t *)(record+720u),0x12345678u);
    set32((uint8_t *)(record+724u),0x9abcdef0u);
    set16((uint8_t *)(uintptr_t)0x8051c2u,0x1122u);
    set16((uint8_t *)(uintptr_t)0x8051c4u,0x3344u);
    memset(expect,0,sizeof expect); expect[5]=0xa5u; expect[21]=0xa5u; expect[29]=0xa5u; expect[30]=0xa5u; expect[31]=0xa5u;
    set32(expect,0x260000u);
    expect[4]=62u;
    set16(expect+6u,0x1122u);
    set16(expect+8u,0x3344u);
    set16(expect+10u,3u);
    set16(expect+12u,shift);
    set32(expect+14u,0x12345678u); set16(expect+18u,0xdef0u);
    expect[20]=0x42u;
    uint64_t prod=(uint64_t)period*0x1a36e3u;
    set16(expect+22u,(uint16_t)((((uint32_t)(prod>>32u))<<1u)|
        ((uint32_t)prod>>31u)));
    expect[24]=0x37u;
    expect[25]=include_first?0x51u:0u;
    expect[26]=0x52u;
    expect[27]=0x53u;
    expect[28]=0x54u;
    call_stage=0;
    uint8_t frame[32] __attribute__((aligned(4))); memset(frame,0xa5,sizeof frame);
    assert(opencfw_em9305_init_transition_event_308664_body(62u,record,include_first,frame)==
        0xa55aa55au);
    assert(call_stage==1);
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(unsigned i=0;i<256u;i++) { run(i&1u,i*0x01010101u,(uint16_t)(i*113u)); }
    return 0;
}
