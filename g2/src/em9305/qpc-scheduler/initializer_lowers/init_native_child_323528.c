#include <stdint.h>

/* Native 0x323528..0x323574: clear a pending-procedure bit in the record
 * mask at +636 (and the word at +640). Clearing bit 28 while the report
 * byte at +745 is set reports the PHY update through 323620 and clears
 * the report byte. Returns the record unless the report runs. */
extern uint32_t opencfw_em9305_callback_323620(uintptr_t record, uint32_t status,
                                               uint32_t kind, uint32_t index,
                                               int32_t previous, uint32_t current,
                                               int32_t phy);

uint32_t opencfw_em9305_child_323528(uintptr_t record, uint32_t bit)
{
    volatile uint32_t *mask=(volatile uint32_t *)(record+636u);
    uint32_t pending=*mask;
    if(((pending>>(bit&31u))&1u)==0u)return (uint32_t)record;
    *(volatile uint32_t *)(record+640u)=0u;
    *mask=pending&~(1u<<(bit&31u));
    if(bit!=28u)return (uint32_t)record;
    volatile uint8_t *report=(volatile uint8_t *)(record+745u);
    if(*report==0u)return (uint32_t)record;
    uint32_t index=*(volatile uint8_t *)(record+766u);
    int32_t phy=*(volatile int8_t *)(record+764u);
    uintptr_t slot=record+index+557u;
    uint32_t current=*(volatile uint8_t *)slot;
    int32_t previous=*(volatile int8_t *)(slot-4u);
    uint32_t status=opencfw_em9305_callback_323620(record,0u,2u,index,previous,current,phy);
    *report=0u;
    return status;
}
