#include <stdint.h>

/* Native 0x32a628..0x32a76e: encryption procedure event for a connection
 * record. While a link procedure is active (+403) opcodes 0x0d/0x0e go to
 * 31b714 (returns 1), and an LL_REJECT (0x0c) whose rejected opcode
 * (0x802818) is not encryption-related goes to 31b714 (returns 0). With
 * encryption supported (0x805a94 bit 0) the event (0x3e only in state
 * 0x13 -> 6, 0x19 -> 4, 0x1a -> 5, rejects of opcodes 3/6/10/11 through
 * the switch table at 0x3344b7) drives the procedure: idle (+620 = 0)
 * starts it, active (+620 = 1) records the pending state bits in +644 and
 * finishes it (+635 = 0xff, flag bit 1 of +13 cleared, PHY finish when no
 * link procedure). Returns 1 when the event was consumed, else 0. The
 * stock hook call (*0x805688) leaves the hook address in r1. */
extern const uint8_t opencfw_em9305_enc_switch_3344b7[];
extern uint32_t opencfw_em9305_child_31b714(uintptr_t);
extern uint32_t opencfw_em9305_child_32a5f4(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_329518(uintptr_t);
extern uint32_t opencfw_em9305_child_329508(uintptr_t);
extern uint32_t opencfw_em9305_child_329554(uintptr_t);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t);

uint32_t opencfw_em9305_callback_32a628(uintptr_t record,uint32_t opcode)
{
    volatile uint8_t *rec=(volatile uint8_t *)record;
    volatile uint32_t *pending=(volatile uint32_t *)(record+644u);
    if(rec[403]!=0u) {
        if(opcode-0xdu<2u) {
            (void)opencfw_em9305_child_31b714(record);
            return 1u;
        }
        if(opcode==0xcu) {
            uint32_t rejected=*(volatile uint8_t *)(uintptr_t)0x802818u;
            if(rejected>0x11u||((0x22c4cu>>rejected)&1u)==0u) {
                (void)opencfw_em9305_child_31b714(record);
                return 0u;
            }
        }
    }
    if((*(volatile uint8_t *)(uintptr_t)0x805a94u&1u)==0u) return 0u;
    uint32_t event;
    if(opcode==0x3eu) {
        if(rec[635]!=0x13u) return 0u;
        event=6u;
    } else if(opcode==0x19u) {
        event=4u;
    } else if(opcode==0x1au) {
        event=5u;
    } else if(opcode==0xcu) {
        uint32_t index=*(volatile uint8_t *)(uintptr_t)0x802818u-3u;
        if(index>=9u||((0x189u>>(index&0xffu))&1u)==0u) return 0u;
        event=opencfw_em9305_enc_switch_3344b7[(int8_t)index];
    } else {
        return 0u;
    }
    uint32_t phase=rec[620];
    if(phase==0u) {
        (void)opencfw_em9305_child_32a5f4(record,event);
        if((rec[621]|4u)!=4u) {
            rec[620]=1u;
            rec[635]=19u;
        }
        return 1u;
    }
    if(phase!=1u) return 1u;
    if((event|2u)==2u) {
        uint32_t busy=opencfw_em9305_child_329518(record)!=0u;
        if(!busy) busy=opencfw_em9305_child_329508(record)!=0u;
        if(!busy) {
            uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x805688u;
            if(hook!=0u) {
                busy=((uint32_t (*)(uintptr_t,uintptr_t))hook)(record,hook)!=0u;
                if(!busy) busy=opencfw_em9305_child_329554(record)!=0u;
            } else {
                busy=1u;
            }
        }
        if(busy) {
            uint32_t bit=rec[635];
            uint32_t mask=*pending;
            rec[635]=19u;
            *pending=mask|(1u<<(bit&31u));
        }
    }
    if(rec[635]!=0x13u) {
        *pending|=1u<<19;
        return 1u;
    }
    (void)opencfw_em9305_child_32a5f4(record,event);
    if((rec[621]|4u)!=4u) return 1u;
    uint32_t flags=rec[13];
    uint32_t active=rec[403];
    rec[635]=0xffu;
    rec[620]=0u;
    rec[13]=(uint8_t)(flags&~2u);
    if(active==0u) (void)opencfw_em9305_phy_finish_32c810(record);
    return 1u;
}
