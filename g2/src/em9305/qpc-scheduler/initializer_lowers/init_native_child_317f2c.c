#include <stdint.h>

/* Native 0x317f2c..0x317f5c: subrate step for states 0 and 1 (+620): run
 * the selected action from the 0x334b98 table (record, action) and copy
 * the selected flag from 0x334ba0 into +624. Other states do nothing. */
extern uint32_t (*const opencfw_em9305_subrate_actions_334b98[2])(uintptr_t);
extern const uint8_t opencfw_em9305_subrate_flags_334ba0[4];

void opencfw_em9305_child_317f2c(uintptr_t record, uint32_t selector)
{
    uint32_t state=*(volatile uint8_t *)(record+620u);
    if(state>1u)return;
    uintptr_t action=(uintptr_t)opencfw_em9305_subrate_actions_334b98[selector];
    if(action!=0u)
        (void)((uint32_t (*)(uintptr_t,uintptr_t,uint32_t))action)(record,action,state);
    *(volatile uint8_t *)(record+624u)=opencfw_em9305_subrate_flags_334ba0[selector];
}
