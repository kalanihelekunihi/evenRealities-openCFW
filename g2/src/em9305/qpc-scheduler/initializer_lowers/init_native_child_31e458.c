#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31e458..0x31e49e: look up the connection entry for the
 * command's handle (base at ((uintptr_t)&em9305_ram_805c5c + 0x14u), 912 bytes each). If the entry is in
 * use, copy the command's halfword +86 to +892 and byte +84 to +890, make
 * the command current (((uintptr_t)&em9305_ram_805c5c + 0x10u)) and pass the entry and the command code
 * (+3) to 32a000 (entry role byte +2 set) or 31e4a0. Returns the entry
 * when it is unused. */
extern uint32_t opencfw_em9305_child_32a000(uintptr_t entry, uint32_t code);
extern uint32_t opencfw_em9305_child_31e4a0(uintptr_t entry, uint32_t code);

uint32_t opencfw_em9305_child_31e458(uintptr_t command)
{
    uint32_t handle=*(volatile uint16_t *)command;
    uintptr_t entry=*(volatile uint32_t *)(uintptr_t)((uintptr_t)&em9305_ram_805c5c + 0x14u)+handle*912u;
    if(*(volatile uint8_t *)entry==0u)return (uint32_t)entry;
    *(volatile uint16_t *)(entry+892u)=*(volatile uint16_t *)(command+86u);
    uint32_t value=*(volatile uint8_t *)(command+84u);
    uint32_t role=*(volatile uint8_t *)(entry+2u);
    em9305_ram_805c5c.u32_805c6c=(uint32_t)command;
    *(volatile uint8_t *)(entry+890u)=(uint8_t)value;
    uint32_t code=*(volatile uint8_t *)(command+3u);
    if(role!=0u)return opencfw_em9305_child_32a000(entry,code);
    return opencfw_em9305_child_31e4a0(entry,code);
}
