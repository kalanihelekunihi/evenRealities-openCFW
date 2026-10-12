#include <assert.h>
#include <stdint.h>

uint32_t opencfw_em9305_init_transition_event_30e988(uint32_t);
static uint16_t expected_id;
static unsigned calls;
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
    const uint8_t *b=(const uint8_t *)event;
    assert(b[0]==0u&&b[1]==0u&&b[2]==31u&&b[3]==0u);
    assert((uint16_t)(b[4]|((uint16_t)b[5]<<8u))==expected_id);
    calls++;
    return 0x12345678u;
}
int main(void)
{
    for(uint32_t id=0u;id<65536u;id+=257u){
        expected_id=(uint16_t)id;
        assert(opencfw_em9305_init_transition_event_30e988(id)==0x12345678u);
    }
    assert(calls==256u);
    return 0;
}
