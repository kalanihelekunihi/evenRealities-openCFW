#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x323b10..0x323bac: compose a type-6 PDU (forced 3) with an
 * 8-byte header. For a set, the header lives at set+0xae4 (starting with
 * 8) and is filled by 318440/3184f4 from the set's +0x9d4 data. Without a
 * set, the stack header {8, 0, 0, 0, 0} is filled by the two registered
 * hooks (*((uintptr_t)&em9305_ram_805c5c + 0x4u) then *(uintptr_t)&em9305_ram_805c5c, both required) from the ready
 * auxiliary object's +0x2c / +0x24 fields. */
extern uint32_t opencfw_em9305_child_318440(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_3184f4(uintptr_t,uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_auxiliary_ready_303f68(void);
extern uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t,uint32_t,uint32_t,uint32_t,
                                                    uintptr_t,uintptr_t,uintptr_t,uint32_t,
                                                    uint32_t);

struct init_header_323b10 {
    uint32_t word;
    uint8_t byte;
};

uint32_t opencfw_em9305_child_323b10(uintptr_t set,uintptr_t output,uint32_t count)
{
    struct init_header_323b10 local;
    local.byte=0u;
    local.word=0u;
    uintptr_t header;
    if(set!=0u) {
        header=set+0xae4u;
        *(volatile uint8_t *)header=8u;
        (void)opencfw_em9305_child_318440(header,set+0x9d4u,set);
        (void)opencfw_em9305_child_3184f4(header,set+0x9d4u,set);
    } else {
        header=(uintptr_t)&local;
        volatile uint32_t *first_hook=&em9305_ram_805c5c.u32_805c60;
        volatile uint32_t *second_hook=&em9305_ram_805c5c.u32_805c5c;
        if(*first_hook!=0u&&*second_hook!=0u) {
            uintptr_t object=opencfw_em9305_auxiliary_ready_303f68();
            uintptr_t hook=*first_hook;
            uint32_t data=*(volatile uint32_t *)(object+0x24u);
            *(volatile uint8_t *)header=8u;
            ((void (*)(uintptr_t,uint32_t,uint32_t))hook)(header,
                *(volatile uint32_t *)(object+0x2cu),data);
            ((void (*)(uintptr_t,uint32_t,uint32_t))*second_hook)(header,
                *(volatile uint32_t *)(object+44u),data);
        }
    }
    return opencfw_em9305_radio_compose_323dc0(set,3u,0u,0u,header,0u,output,6u,count);
}
