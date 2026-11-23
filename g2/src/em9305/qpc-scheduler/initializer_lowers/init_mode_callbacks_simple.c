#include <stdint.h>
#include "em9305_ram.h"

/* Table callbacks from native 0x32ca90, 0x32c86c, 0x32cfe8. The second
 * callback argument is the address of the selected table cell (native R1),
 * overwritten before use in each of these three bodies. */
uint32_t opencfw_em9305_mode_callback_32ca90(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t source=em9305_ram_805c5c.u32_805c6c;
    uint8_t value=*(volatile uint8_t *)(source+4u);
    *(volatile uint8_t *)(context+12u)=value;
    return (uint32_t)context;
}

uint32_t opencfw_em9305_mode_callback_32c86c(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t source=em9305_ram_805c5c.u32_805c6c;
    uint32_t first=*(volatile uint32_t *)(source+8u);
    uint32_t second=*(volatile uint32_t *)(source+4u);
    *(volatile uint32_t *)(context+712u)=first;
    *(volatile uint32_t *)(context+708u)=second;
    return (uint32_t)context;
}

uint32_t opencfw_em9305_mode_callback_32cfe8(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uint8_t value=em9305_ram_8027e0.u8_80281c;
    *(volatile uint8_t *)(context+12u)=value;
    uintptr_t target=context+629u;
    *(volatile uint8_t *)target=1u;
    return (uint32_t)target;
}
