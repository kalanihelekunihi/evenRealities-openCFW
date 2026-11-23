#include <stdint.h>
#include "em9305_ram.h"

/* Complete native 0x318168..0x3181b2. The dynamic ((uintptr_t)&em9305_ram_805c5c + 0x80u) callback
 * receives R0=object+44, R1=0, R2=its code identity and R3=object.
 * Both row object and configuration pointer are reread after the call. */
extern uint32_t opencfw_em9305_ll_stream_gate_30e510(void);
uint32_t opencfw_em9305_init_callback_318168(uint32_t incoming)
{
    (void)incoming;
    uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
    if (gate==0u) return 0u;
    uintptr_t config=em9305_ram_805c5c.u32_805cac;
    uintptr_t row=((uintptr_t)&em9305_ram_80517c + 0x4u);
    for (uint32_t index=0;;++index,row+=12u) {
        uint32_t count=*(volatile uint8_t *)(config+13u);
        if (index>=count) return count;
        uint32_t active=*(volatile uint8_t *)(row+4u);
        if (active==0u) continue;
        uintptr_t object=*(volatile uint32_t *)row;
        uint32_t kind=*(volatile uint8_t *)(object+64u);
        if (kind!=2u) continue;
        uintptr_t callback=em9305_ram_805c5c.u32_805cdc;
        if (callback==0u) continue;
        (void)((uint32_t (*)(uintptr_t,uint32_t,uintptr_t,uintptr_t))callback)
            (object+44u,0u,callback,object);
        object=*(volatile uint32_t *)row;
        config=em9305_ram_805c5c.u32_805cac;
        *(volatile uint8_t *)(object+64u)=0u;
    }
}
