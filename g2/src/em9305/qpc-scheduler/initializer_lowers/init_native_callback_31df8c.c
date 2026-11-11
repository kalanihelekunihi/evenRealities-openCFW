#include <stdint.h>

/* Native 0x31df8c..0x31dfce: make the command current (0x805c6c) and run
 * 31e458 for its connection handle; handle 0xff (+2) instead walks every
 * handle below the configured count (+34 of 0x805cac), using the
 * halfword at +0 as the loop index. */
extern uint32_t opencfw_em9305_child_31e458(uintptr_t command);

uint32_t opencfw_em9305_callback_31df8c(uintptr_t command)
{
    volatile uint32_t *current=(volatile uint32_t *)(uintptr_t)0x805c6cu;
    volatile uint16_t *handle=(volatile uint16_t *)command;
    if(*(volatile uint8_t *)(command+2u)!=255u){
        *current=(uint32_t)command;
        return opencfw_em9305_child_31e458(command);
    }
    uint32_t index=0u;
    for(;;){
        *handle=(uint16_t)index;
        uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
        index&=0xffffu;
        if(index>=*(volatile uint8_t *)(config+34u))return index;
        *current=(uint32_t)command;
        (void)opencfw_em9305_child_31e458(command);
        index=*handle+1u;
    }
}
