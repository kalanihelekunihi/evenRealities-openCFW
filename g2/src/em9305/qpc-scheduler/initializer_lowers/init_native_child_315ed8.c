#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x315ed8..0x315f0a: clear the record's pending word (+640) and bit
 * 17 of its flag word (+636), then report the procedure end through
 * 322fdc: reason 0x1a for opcode 7, the stored reason byte (((uintptr_t)&em9305_ram_8027e0 + 0x3du)) for
 * opcodes 0x11 and 0x0d, nothing for any other opcode (((uintptr_t)&em9305_ram_8027e0 + 0x38u)). */
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t,uint32_t);

void opencfw_em9305_child_315ed8(uintptr_t record)
{
    uint32_t flags=*(volatile uint32_t *)(record+636u);
    uint32_t opcode=em9305_ram_8027e0.u8_802818;
    *(volatile uint32_t *)(record+640u)=0u;
    *(volatile uint32_t *)(record+636u)=flags&~(1u<<17);
    if(opcode==7u)
        (void)opencfw_em9305_mode_event_322fdc(record,0x1au);
    else if(opcode==0x11u||opcode==0x0du)
        (void)opencfw_em9305_mode_event_322fdc(record,
            em9305_ram_8027e0.u8_80281d);
}
