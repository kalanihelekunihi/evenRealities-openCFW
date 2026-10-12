#include <assert.h>
#include <stdint.h>
extern uint32_t opencfw_em9305_init_callback_3245ec(uint32_t,uintptr_t,uintptr_t,uint32_t);
static unsigned calls;
uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t record,uint32_t forced,
    uint32_t allowed,uint32_t prefix,uintptr_t header,uintptr_t source,
    uintptr_t output,uint32_t type,uint32_t count)
{
    assert(record==0u&&forced==0u&&prefix==0u);
    assert(allowed==0xabu&&source==0x1234u&&output==0x5678u);
    assert(type==8u&&count==0x9abcu);
    const volatile uint8_t *h=(const volatile uint8_t *)header;
    assert(h[0]==7u&&h[1]==0u&&h[2]==0u&&h[3]==0u&&h[4]==0u);
    ++calls;return 0x8765u;
}
int main(void)
{
    for (unsigned n=0;n<256u;++n)
        assert(opencfw_em9305_init_callback_3245ec(0x100ab,0x5678u,0x1234u,0x9abcu)==0x8765u);
    assert(calls==256u);return 0;
}
