#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_dispatch_316704_body(uint8_t *);
static const uintptr_t event=0x810000u,packet=0x820000u;
static unsigned scenario,stage,allocations;
uint32_t opencfw_em9305_radio_packet_check_303404(
    uint32_t p,uintptr_t descriptor,uint32_t one,uintptr_t snapshot)
{ assert(stage==0u&&p==packet&&descriptor==0x80537cu&&one==1u&&snapshot==0x8053b4u);stage=1u;return scenario==3u?0u:1u; }
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t size)
{ assert(size==(allocations?4u:88u));allocations++;return event; }
uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(uintptr_t out,uintptr_t in)
{ assert(out==event+4u&&in==packet+2u);return 0x57u; }
uint32_t opencfw_em9305_init_transition_packet_check_32e278(uintptr_t input)
{ assert(input==event+4u);return 1u; }
uint32_t opencfw_em9305_ll_stream_address_busy_318200(
    uint32_t flags,uint32_t low,uint32_t high)
{ assert(stage==1u&&flags==3u&&low==0x1111u&&high==0x2222u);stage=2u;return 0u; }
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t message)
{ assert(handler==7u&&message==event);stage=3u;return 0u; }
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p)
{ assert(p==event);stage=2u;return 0u; }
uint32_t opencfw_em9305_common_release_304588(uint32_t one)
{ assert(one==1u);stage=4u;return 0u; }
uint32_t opencfw_em9305_init_transition_gate_3168e4(void)
{ stage=5u;return 0x7654u; }
uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void)
{ stage=1u;return 0u; }
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n)
{ assert(v==0u&&n==36u);memset(p,0,n);return p; }
uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t p,uint32_t low,uint32_t high)
{ assert(low==0x2222u&&high==0x3333u);memset((void *)p,0x42,6);return p+6u; }
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p)
{ assert(((uint8_t *)p)[4]==60u);stage=2u;return 0u; }
static void setup(void)
{
    memset((void *)(uintptr_t)0x800000u,0,0x100000u);
    stage=0u;allocations=0u;
    *(uint8_t *)(uintptr_t)0x805a71u=(uint8_t)(scenario!=0u);
    *(uint8_t *)(uintptr_t)0x8052fcu=(uint8_t)(scenario>=2u);
    *(uint32_t *)(uintptr_t)0x805398u=(uint32_t)packet;
    *(uint8_t *)(uintptr_t)0x805b90u=1u;
    *(uint32_t *)(uintptr_t)0x805b94u=0x2222u;
    *(uint32_t *)(uintptr_t)0x805b98u=0x3333u;
    *(uint8_t *)(uintptr_t)0x805b92u=5u;
    *(uint32_t *)(uintptr_t)0x8053c0u=0x2222u;
    *(uint32_t *)(uintptr_t)0x8053bcu=0x1111u;
    *(uint8_t *)(uintptr_t)0x8053c7u=1u;
    *(uint8_t *)(uintptr_t)0x8053c6u=1u;
    *(uint32_t *)(uintptr_t)0x8053b4u=0xaaaau;
    *(uint32_t *)(uintptr_t)0x8053b8u=0xbbbbu;
    *(uint32_t *)(uintptr_t)0x8053bcu=0x1111u;
    *(uint32_t *)(uintptr_t)0x8053c0u=0x2222u;
    *(uint8_t *)(uintptr_t)0x805b18u=7u;
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(scenario=0u;scenario<4u;scenario++) {
        setup();uint8_t frame[40] __attribute__((aligned(4)));
        memset(frame,0xa5,sizeof frame);
        uint32_t result=opencfw_em9305_init_transition_dispatch_316704_body(frame);
        if(scenario==0u)assert(result==0u&&stage==0u);
        else assert(result==0x7654u&&stage==5u);
        if(scenario==1u) {
            assert(frame[38]==0xa5u&&frame[39]==0xa5u);
            assert(frame[36]==0xffu&&frame[37]==0xffu);
        }
        if(scenario==2u)assert(allocations==1u);
        if(scenario==3u)assert(allocations==2u);
    }
    return 0;
}
