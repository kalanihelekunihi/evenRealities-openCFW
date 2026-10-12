#include <stdint.h>

/* Three complete callback-table leaves, native 0x32cb0c, 0x32cf50,
 * 0x32cf80. The table-cell argument in R1 is overwritten before use. */
uint32_t opencfw_em9305_mode_callback_32cb0c(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t source=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
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
    uintptr_t source=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
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
    uint32_t word=*(volatile uint32_t *)(uintptr_t)0x80281cu;
    uint16_t half=*(volatile uint16_t *)(uintptr_t)0x802820u;
    *(volatile uint8_t *)(context+526u)=1u;
    *(volatile uint32_t *)(context+528u)=word;
    uintptr_t target=context+532u;
    *(volatile uint16_t *)target=half;
    return (uint32_t)target;
}
