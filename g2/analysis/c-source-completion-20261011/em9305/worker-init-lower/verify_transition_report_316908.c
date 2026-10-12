#include <assert.h>
#include <stdint.h>
#include <string.h>

uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
static unsigned calls;
void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t bytes)
{
    assert(value==0u && bytes==36u && calls==0u);
    calls=1u;
    return memset(dst,0,bytes);
}
uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t output,uint32_t low,uint32_t high)
{
    assert(low==0x11223344u && high==0x55667788u);
    uint8_t *bytes=(uint8_t *)output;
    assert(bytes[-8]==5u); /* Native call delay slot already ran. */
    bytes[-8]=7u; /* Call-side mutation detects any post-call overwrite. */
    for (unsigned i=0;i<6;i++) bytes[i]=(uint8_t)(0xa0u+i);
    calls=2u;
    return output+6u;
}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t packet)
{
    const uint8_t *p=(const uint8_t *)packet;
    assert(calls==2u);
    assert(p[0]==0 && p[1]==0 && p[2]==7u);
    assert(p[3]==0xabu && p[4]==0xabu && p[9]==0x34u);
    for (unsigned i=0;i<6;i++) assert(p[10+i]==(uint8_t)(0xa0u+i));
    assert(p[35]==0xefu && p[36]==0xffu && p[37]==0xffu);
    assert(p[5]==0 && p[6]==0 && p[8]==0 && p[16]==0 && p[34]==0);
    calls=3u;
    return 0x13579bdfu;
}
int main(void)
{
    assert(opencfw_em9305_init_transition_report_316908(
        0x1234ef,0xab,0x1234,0x11223344u,0x55667788u)==0x13579bdfu);
    assert(calls==3u);
    return 0;
}
