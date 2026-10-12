#include <stdint.h>

/* Native 0x3246c0..0x3246f4. ADD2 0x34 means 0xd0 byte displacement. */
extern uint32_t opencfw_em9305_init_callback_32468c(uint32_t);
extern uint32_t opencfw_em9305_init_callback_324698(uintptr_t);

uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t packet)
{
    uintptr_t slot=packet+208u;
    uint32_t result=0u;
    for(uint32_t index=0u;index<4u;++index,slot+=4u){
        result=*(volatile uint32_t *)slot;
        if(result==0u){
            result=opencfw_em9305_init_callback_32468c(0u);
            *(volatile uint32_t *)slot=result;
        }
    }
    return result;
}

uint32_t opencfw_em9305_init_callback_child_3246dc(uintptr_t packet)
{
    uintptr_t slot=packet+208u;
    uint32_t result=0u;
    for(uint32_t index=0u;index<4u;++index,slot+=4u){
        result=*(volatile uint32_t *)slot;
        if(result!=0u)result=opencfw_em9305_init_callback_324698(slot);
    }
    return result;
}
