#include <stdint.h>
#include "em9305_ram.h"

/* Three complete callback-table leaves, native 0x32cb0c, 0x32cf50,
 * 0x32cf80. The table-cell argument in R1 is overwritten before use. */
uint32_t opencfw_em9305_mode_callback_32cb0c(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t source=em9305_ram_805c5c.u32_805c6c;
    uintptr_t target=context+606u;
    uint8_t first=*(volatile uint8_t *)(source+4u);
    *(volatile uint8_t *)target=first;
    uint8_t second=*(volatile uint8_t *)(source+5u);
    *(volatile uint8_t *)(target+1u)=second;
    return (uint32_t)target;
}

uint32_t opencfw_em9305_mode_callback_32cf80(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t source=em9305_ram_805c5c.u32_805c6c;
    uintptr_t target=context+744u;
    uint8_t value=*(volatile uint8_t *)(source+4u);
    *(volatile uint8_t *)target=value;
    return (uint32_t)target;
}

uint32_t opencfw_em9305_mode_callback_32cf50(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    if (*(volatile uint8_t *)(context+526u)!=0u)
        return (uint32_t)context;
    uint32_t word=em9305_ram_8027e0.u32_80281c;
    uint16_t half=em9305_ram_8027e0.u16_802820;
    *(volatile uint8_t *)(context+526u)=1u;
    *(volatile uint32_t *)(context+528u)=word;
    uintptr_t target=context+532u;
    *(volatile uint16_t *)target=half;
    return (uint32_t)target;
}
