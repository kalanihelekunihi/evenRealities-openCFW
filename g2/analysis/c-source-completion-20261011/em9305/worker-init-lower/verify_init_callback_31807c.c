#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_callback_31807c(uintptr_t);
uintptr_t opencfw_em9305_init_transition_callbacks_334e80[16];
uint8_t opencfw_em9305_init_transition_states_334ec0[16];
static uintptr_t found;
static uint32_t searched,called,mutate;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id)
{
    searched=(uint8_t)id;
    return found;
}
static uint32_t on_transition(uintptr_t record,uintptr_t identity,
                              uint32_t state,uintptr_t nested)
{
    assert(record==0x810000u && identity==(uintptr_t)on_transition);
    assert(state==1u && nested==0x811000u);
    ++called;
    if(mutate) {
        *(volatile uint32_t *)(record+0xafcu)=0x812000u;
        *(volatile uint8_t *)(uintptr_t)0x812050u=3u;
    }
    return 0xbadbeefu;
}
int main(void)
{
    uintptr_t bases[]={0x805000u,0x806000u,0x810000u,0x811000u,0x812000u};
    for(unsigned i=0;i<sizeof bases/sizeof bases[0];++i)
        assert(mmap((void *)bases[i],4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)bases[i]);
    uint8_t *event=(uint8_t *)(uintptr_t)0x806000u;
    event[0]=7u;event[2]=3u;event[3]=2u;
    *(uint32_t *)(uintptr_t)0x805cacu=0x806000u;
    event[13]=1u;
    found=0u;
    assert(opencfw_em9305_init_callback_31807c((uintptr_t)event)==0u);
    assert(searched==7u);
    found=0x810000u;
    assert(opencfw_em9305_init_callback_31807c((uintptr_t)event)==0x810000u);
    *(uint32_t *)(uintptr_t)0x810afcu=0x811000u;
    *(uint8_t *)(uintptr_t)0x811050u=1u;
    opencfw_em9305_init_transition_states_334ec0[1u*4u+2u]=3u;
    assert(opencfw_em9305_init_callback_31807c((uintptr_t)event)==3u);
    assert(*(uint8_t *)(uintptr_t)0x811050u==3u&&called==0u);
    *(uint8_t *)(uintptr_t)0x811050u=1u;
    opencfw_em9305_init_transition_callbacks_334e80[1u*4u+2u]=(uintptr_t)on_transition;
    opencfw_em9305_init_transition_states_334ec0[3u*4u+2u]=2u;
    mutate=1u;
    assert(opencfw_em9305_init_callback_31807c((uintptr_t)event)==2u);
    assert(called==1u && *(uint8_t *)(uintptr_t)0x812050u==2u);
    /* Broadcast event takes IDs 0..count-1; count rechecked each turn. */
    event[2]=255u;event[13]=2u;
    found=0u;
    assert(opencfw_em9305_init_callback_31807c((uintptr_t)event)==2u);
    assert(searched==1u);
    return 0;
}
