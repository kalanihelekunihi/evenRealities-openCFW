#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_registered_322d68(uintptr_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_callback_327de0(uintptr_t,uint32_t,uint32_t,uintptr_t);
uintptr_t opencfw_em9305_init_transition_callbacks_335730[24],opencfw_em9305_init_transition_callbacks_334b1c[20];
uint8_t opencfw_em9305_init_secondary_transitions_335790[24],opencfw_em9305_init_transition_states_334b6c[20];
static uint32_t calls,expected_offset;
static uintptr_t expected_ambient,state_slot;
static uint32_t cb(uintptr_t self,uint32_t offset,uint32_t state,uintptr_t ambient)
{
    assert(self==(uintptr_t)cb&&offset==expected_offset);
    assert(state==1u&&ambient==expected_ambient);
    ++calls;
    *(volatile uint8_t *)state_slot=3u;
    return 0xffffffffu;
}
int main(void)
{
    assert(mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x805000u);
    assert(mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x806000u);
    uint8_t *event=(uint8_t *)(uintptr_t)0x806000u;
    event[3]=2u;
    expected_ambient=0x12345678u;
    expected_offset=32u;state_slot=0x8051c0u;
    *(uint8_t *)state_slot=1u;
    opencfw_em9305_init_transition_callbacks_335730[8]=(uintptr_t)cb;
    opencfw_em9305_init_secondary_transitions_335790[20]=2u;
    assert(opencfw_em9305_init_registered_322d68((uintptr_t)event,7u,8u,
                                                  expected_ambient)==2u);
    assert(calls==1u&&*(uint8_t *)state_slot==2u);
    assert(*(uint32_t *)(uintptr_t)0x805c80u==0x806000u);
    expected_offset=28u;state_slot=0x8052fbu;
    *(uint8_t *)state_slot=1u;
    opencfw_em9305_init_transition_callbacks_334b1c[7]=(uintptr_t)cb;
    opencfw_em9305_init_transition_states_334b6c[17]=2u;
    assert(opencfw_em9305_init_callback_327de0((uintptr_t)event,7u,8u,
                                                expected_ambient)==2u);
    assert(calls==2u&&*(uint8_t *)state_slot==2u);
    /* Empty cell follows direct transition with no callback. */
    event[3]=0u;state_slot=0x8052fbu;*(uint8_t *)state_slot=0u;
    opencfw_em9305_init_transition_states_334b6c[0]=1u;
    assert(opencfw_em9305_init_callback_327de0((uintptr_t)event,7u,8u,
                                                expected_ambient)==1u);
    assert(calls==2u);
    return 0;
}
