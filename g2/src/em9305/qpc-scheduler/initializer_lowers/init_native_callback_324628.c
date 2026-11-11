#include <stdint.h>

/* Native 0x324628..0x324672: command state debounce (fields at +776).
 * Unless the update is locked (+784), derive the requested value; a value
 * equal to the current one (+782) or different from the pending one (+783)
 * becomes the new pending value and resets the counter (+781). A repeat of
 * the pending value counts up; once the counter reaches the limit (+780)
 * the value becomes current, the counter resets and 323268 refreshes the
 * command state. */
extern uint32_t opencfw_em9305_command_derive_317ba8(uintptr_t);
extern uint32_t opencfw_em9305_command_refresh_323268(uintptr_t);

void opencfw_em9305_callback_324628(uintptr_t row)
{
    volatile uint8_t *state=(volatile uint8_t *)(row+776u);
    if(state[8]!=0u) return;
    uint32_t value=opencfw_em9305_command_derive_317ba8(row);
    if(value==state[6]||value!=state[7]) {
        state[7]=(uint8_t)value;
        state[5]=0u;
        return;
    }
    uint32_t count=state[5]+1u;
    uint32_t limit=state[4];
    state[5]=(uint8_t)count;
    if((uint8_t)count<limit) return;
    state[6]=(uint8_t)value;
    state[5]=0u;
    (void)opencfw_em9305_command_refresh_323268(row);
}
