#include <stdint.h>

/* Native 0x32be78..0x32beb0: when the link at +36 has its report byte
 * (+67) set, notify 30e8dc with the link handle and the key-state byte
 * (+203 of the context at +44), with bit 1 added when that byte differs
 * from +202 or the two 64-bit values at +184 and +192 differ. Returns the
 * record pointer unchanged when no report is due. */
extern uint32_t opencfw_em9305_child_30e8dc(uint32_t handle, uint32_t state);

uint32_t opencfw_em9305_child_32be78(uintptr_t record)
{
    uintptr_t link=*(volatile uint32_t *)(record+36u);
    if(*(volatile uint8_t *)(link+67u)==0u)return (uint32_t)record;
    uintptr_t context=*(volatile uint32_t *)(record+44u);
    volatile uint32_t *values=(volatile uint32_t *)(context+184u);
    uint32_t state=*(volatile uint8_t *)(context+203u);
    uint32_t previous=*(volatile uint8_t *)(context+202u);
    if(state!=previous||values[0]!=values[2]||values[1]!=values[3])state|=2u;
    return opencfw_em9305_child_30e8dc(*(volatile uint8_t *)(link+1u),state);
}
