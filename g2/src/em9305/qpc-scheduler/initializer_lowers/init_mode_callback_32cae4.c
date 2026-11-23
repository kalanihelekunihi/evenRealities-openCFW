#include <stdint.h>
#include "em9305_ram.h"

/* Full native table callback 0x32cae4..0x32cb0a. Native BL.D supplies
 * context+566 in R1; the authenticated radio-limit body is already selected. */
extern uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t context,
                                                    uintptr_t input);
uint32_t opencfw_em9305_mode_callback_32cae4(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t source=em9305_ram_805c5c.u32_805c6c;
    uint16_t first=*(volatile uint16_t *)(source+4u);
    *(volatile uint16_t *)(context+570u)=first;
    uint16_t second=*(volatile uint16_t *)(source+6u);
    *(volatile uint16_t *)(context+572u)=second;
    uint32_t result=opencfw_em9305_radio_limit_317b10(context,context+566u);
    *(volatile uint16_t *)(context+590u)=(uint16_t)result;
    return result;
}
