#include "native_gomore_history_record.h"
uintptr_t r1_gomore_modulo5_native(volatile void *record,uint32_t secondary,uint32_t primary)
{
    uintptr_t state=(uintptr_t)record;
    uint32_t counter=*(volatile uint8_t *)(uintptr_t)(state+40u);
    if (counter%5u==0) {
        *(volatile uint8_t *)(uintptr_t)(state+41u+counter/5u)=(uint8_t)(primary==255u?1u:primary);
        counter=*(volatile uint8_t *)(uintptr_t)(state+40u);
        *(volatile uint8_t *)(uintptr_t)(state+45u+((counter/5u)&1u))=(uint8_t)(secondary==255u?1u:secondary);
    }
    counter=*(volatile uint8_t *)(uintptr_t)(state+40u);
    *(volatile uint8_t *)(uintptr_t)(state+40u)=(uint8_t)((counter+1u)%20u);
    return state+40u;
}
