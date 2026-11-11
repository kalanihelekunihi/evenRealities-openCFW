/* Stock 0x948d8: descriptor is reloaded for every appended sample. */
#include <stdint.h>
extern uint32_t r1_gomore_filter_native(uint32_t,uint32_t,uint32_t);
static uint32_t word(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
uint32_t r1_gomore_optical_append_native(uint32_t state,uint32_t input,uint32_t missing)
{
    for(uint32_t i=0;i<250;i++) {
        float value;
        if(i<225) value=*(volatile float *)(uintptr_t)(state+728u+(i+25u)*4u);
        else if(missing) value=0.0f;
        else value=-*(volatile float *)(uintptr_t)(word(input)+(i-225u)*4u);
        *(volatile float *)(uintptr_t)(state+728u+i*4u)=value;
    }
    if(!missing) (void)r1_gomore_filter_native(state,state+1628u,25);
    return 0;
}
