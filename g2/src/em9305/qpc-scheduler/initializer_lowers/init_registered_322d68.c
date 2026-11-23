#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x322d68..0x322da8. The incoming R3 is ambient at registration;
 * pass its actual register value through the typed fourth parameter. The
 * ROM tables at 0x335730 and 0x335790 cover four states x six selectors. */
extern const uintptr_t opencfw_em9305_init_transition_callbacks_335730[24];
extern const uint8_t opencfw_em9305_init_secondary_transitions_335790[24];

uint32_t opencfw_em9305_init_registered_322d68(uintptr_t event,
                                                 uint32_t incoming_r1,
                                                 uint32_t incoming_r2,
                                                 uintptr_t ambient_r3)
{
    (void)incoming_r1;
    (void)incoming_r2;
    em9305_ram_805c5c.u32_805c80=(uint32_t)event;
    uint32_t selector=*(volatile uint8_t *)(event+3u);
    uint32_t state=em9305_ram_8051b8.u8_8051c0;
    uint32_t byte_offset=state*24u+selector*4u;
    uintptr_t callback=opencfw_em9305_init_transition_callbacks_335730[byte_offset/4u];
    if(callback!=0u) {
        (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uintptr_t))callback)
            (callback,byte_offset,state,ambient_r3);
        state=em9305_ram_8051b8.u8_8051c0;
    }
    uint32_t next=opencfw_em9305_init_secondary_transitions_335790[state*6u+selector];
    em9305_ram_8051b8.u8_8051c0=(uint8_t)next;
    return next;
}
