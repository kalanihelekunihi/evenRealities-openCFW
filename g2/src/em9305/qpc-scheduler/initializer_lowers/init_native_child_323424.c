#include <stdint.h>

/* Native 0x323424..0x323498: finish the pending LL procedure whose bit is
 * set in the record's pending mask (+636): clear the bit and the procedure
 * timer word (+640). For opcode 7 (0x802818) procedure 0x1b only clears
 * flag bit 2 of +548, and procedure 0x1c clears flag bit 1; otherwise the
 * reason is the stored byte (0x80281d) for opcodes 0x11/0x0d, else 0x1a.
 * Procedure 0x1c then reports the reason through 323620 when the
 * record's report enable (+745) is set. */
extern uint32_t opencfw_em9305_callback_323620(uintptr_t,uint32_t,uint32_t,uint32_t,
                                               int32_t,uint32_t,int32_t);

void opencfw_em9305_child_323424(uintptr_t record,uint32_t procedure)
{
    uint32_t pending=*(volatile uint32_t *)(record+636u);
    uint32_t mask=1u<<(procedure&31u);
    if((pending&mask)==0u) return;
    uint32_t opcode=*(volatile uint8_t *)(uintptr_t)0x802818u;
    uint32_t reason=0x1au;
    *(volatile uint32_t *)(record+640u)=0u;
    *(volatile uint32_t *)(record+636u)=pending&~mask;
    volatile uint32_t *flags=(volatile uint32_t *)(record+548u);
    if(opcode==7u) {
        if(procedure==0x1bu) {
            *flags&=~4u;
            return;
        }
        if(procedure!=0x1cu) return;
        *flags&=~2u;
    } else {
        if(opcode==0x11u||opcode==0x0du)
            reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
        if(procedure!=0x1cu) return;
    }
    if(*(volatile uint8_t *)(record+745u)==0u) return;
    (void)opencfw_em9305_callback_323620(record,reason,2u,0u,0,0u,0);
}
