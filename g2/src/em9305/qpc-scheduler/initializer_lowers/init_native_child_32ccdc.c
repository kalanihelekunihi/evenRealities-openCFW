#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32ccdc..0x32cd8c: apply a power-control sample (bytes 0..3 at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x3cu)) to the record's current PHY slot (+766). When reporting is on
 * (+768) and the level changed, report LL event 0x2f (native 0x323620) with
 * the new level and the delta. Store level/limit/flags in the slot tables
 * (+553/+557/+561); unless the level is a sentinel (0x7e/0x7f), clear the
 * pending byte +771 and, for an active request (+769 == 1, +784 set),
 * re-derive (+782) and refresh the command. Byte +764 takes sample byte 1. */
extern uint32_t opencfw_em9305_callback_323620(uintptr_t entry, uint32_t status, uint32_t p0,
                                               uint32_t p1, uint32_t p2, uint32_t p3, uint32_t p4);
extern uint32_t opencfw_em9305_command_derive_317ba8(uintptr_t);
extern uint32_t opencfw_em9305_command_refresh_323268(uintptr_t);

void opencfw_em9305_child_32ccdc(uintptr_t record)
{
    const volatile uint8_t *sample = (const volatile uint8_t *)(uintptr_t)((uintptr_t)&em9305_ram_8027e0 + 0x3cu);
    volatile uint8_t *control = (volatile uint8_t *)(record + 768u);
    uint32_t flags = sample[3];
    uint32_t level = sample[2];
    uint32_t status = sample[1];
    uint32_t limit = sample[0];
    if (control[0] != 0u) {
        uint32_t phy = control[-2];
        uint32_t previous = *(volatile uint8_t *)(record + phy + 553u);
        if (level != previous)
            (void)opencfw_em9305_callback_323620(record, 0u, 1u, phy, (uint32_t)(int8_t)level,
                                                 limit, (uint32_t)(int8_t)(level - previous));
    }
    *(volatile uint8_t *)(record + control[-2] + 553u) = (uint8_t)level;
    *(volatile uint8_t *)(record + control[-2] + 557u) = (uint8_t)limit;
    *(volatile uint8_t *)(record + control[-2] + 561u) = (uint8_t)flags;
    uint32_t stored = *(volatile uint8_t *)(record + control[-2] + 553u);
    if (stored != 0x7fu && stored != 0x7eu) {
        if (control[3] != 0u) control[3] = 0u;
        if (control[1] == 1u && control[16] != 0u) {
            control[16] = 0u;
            control[14] = (uint8_t)opencfw_em9305_command_derive_317ba8(record);
            (void)opencfw_em9305_command_refresh_323268(record);
        }
    }
    *(volatile uint8_t *)(record + 764u) = (uint8_t)status;
}
