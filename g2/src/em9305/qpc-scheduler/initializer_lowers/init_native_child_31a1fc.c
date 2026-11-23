#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31a1fc..0x31a258: PAwR response report. Only in state 1: for a
 * report without the bit-6 flag (+4), pack the six-byte address (+7),
 * build the match key with 316a68 (byte +6, address, flags +4, byte +15,
 * the object's halfword +174) and commit it to the match table at
 * ((uintptr_t)&em9305_ram_803560 + 0xcu). Then mark the state 2 and post event 0x100 to the task at
 * ((uintptr_t)&em9305_ram_805af0 + 0x28u). */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t);
extern uint32_t opencfw_em9305_child_316a68(uintptr_t,uint32_t,uint32_t,uint32_t,
                                            uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_pawr_match_commit_316984(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t,uint32_t);

void opencfw_em9305_child_31a1fc(uintptr_t object,uintptr_t report,uintptr_t state)
{
    if(*(volatile uint8_t *)state!=1u) return;
    if((*(volatile uint8_t *)(report+4u)&0x40u)==0u) {
        uint32_t key[2];
        uint32_t kind=*(volatile uint8_t *)(report+6u);
        uint64_t address=opencfw_em9305_controller_pack_address(report+7u);
        (void)opencfw_em9305_child_316a68((uintptr_t)key,kind,(uint32_t)address,
            (uint32_t)(address>>32),*(volatile uint8_t *)(report+4u),
            *(volatile uint8_t *)(report+15u),*(volatile uint16_t *)(object+174u));
        (void)opencfw_em9305_pawr_match_commit_316984((uintptr_t)((uintptr_t)&em9305_ram_803560 + 0xcu),key[0],key[1]);
    }
    *(volatile uint8_t *)state=2u;
    (void)opencfw_em9305_wsf_event_post(em9305_ram_805af0.u8_805b18,256u);
}
