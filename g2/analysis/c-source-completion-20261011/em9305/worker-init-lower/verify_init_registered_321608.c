#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_registered_321608(uintptr_t);
uintptr_t opencfw_em9305_init_transition_callbacks_335398[20];
uint8_t opencfw_em9305_init_transition_states_3353e8[20];
static unsigned calls;
static volatile uint8_t *live_event;
static uint32_t cb(uintptr_t row,uintptr_t self,uint32_t state)
{
    assert(self==(uintptr_t)cb && state==1u);
    ++calls;
    *(volatile uint8_t *)(row+1u)=3u;
    return 0xffffffffu;
}
static uint32_t change_selector(uintptr_t row,uintptr_t self,uint32_t state)
{
    assert(row==0x803d78u && self==(uintptr_t)change_selector && state==0u);
    live_event[3]=3u;
    return 0u;
}
int main(void)
{
    for(uintptr_t base=0x803000u;base<=0x806000u;base+=0x1000u)
        assert(mmap((void *)base,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)base);
    uint8_t *event=(uint8_t *)(uintptr_t)0x806000u;
    uintptr_t row=0x803d78u+784u;
    *(uint16_t *)event=1u;event[2]=1u;event[3]=2u;
    *(uint8_t *)(row+1u)=1u;
    opencfw_em9305_init_transition_callbacks_335398[1u*5u+2u]=(uintptr_t)cb;
    opencfw_em9305_init_transition_states_3353e8[3u*5u+2u]=4u;
    assert(opencfw_em9305_init_registered_321608((uintptr_t)event)==4u);
    assert(calls==1u&&*(uint8_t *)(row+1u)==4u);
    assert(*(uint32_t *)(uintptr_t)0x805c80u==0x806000u);
    /* Broadcast runs exactly six 784-byte records and returns the last
     * child's next state, with no callback entries active. */
    event[2]=255u;event[3]=0u;calls=0u;
    for(unsigned i=0;i<6u;++i) {
        uintptr_t item=0x803d78u+i*784u;
        *(uint8_t *)(item+1u)=0u;
    }
    opencfw_em9305_init_transition_states_3353e8[0]=2u;
    assert(opencfw_em9305_init_registered_321608((uintptr_t)event)==2u);
    assert(calls==0u);
    for(unsigned i=0;i<6u;++i)
        assert(*(uint8_t *)(uintptr_t)(0x803d78u+i*784u+1u)==2u);
    /* Native 0x321634 reloads event+3 on every broadcast iteration. */
    event[3]=2u;live_event=event;
    for(unsigned i=0;i<6u;++i)
        *(uint8_t *)(uintptr_t)(0x803d78u+i*784u+1u)=0u;
    opencfw_em9305_init_transition_callbacks_335398[2]=(uintptr_t)change_selector;
    opencfw_em9305_init_transition_states_3353e8[2]=1u;
    opencfw_em9305_init_transition_states_3353e8[3]=4u;
    assert(opencfw_em9305_init_registered_321608((uintptr_t)event)==4u);
    assert(event[3]==3u);
    assert(*(uint8_t *)(uintptr_t)(0x803d78u+1u)==1u);
    for(unsigned i=1;i<6u;++i)
        assert(*(uint8_t *)(uintptr_t)(0x803d78u+i*784u+1u)==4u);
    return 0;
}
