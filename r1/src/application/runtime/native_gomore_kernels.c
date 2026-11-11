/* Stock four-word entry points. Lower providers are intentionally unconditional. */
#include <stdint.h>
extern void r1_gomore_linear_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_filter_native(uint32_t,uint32_t,uint32_t);
uint32_t r1_gomore_acc_kernel_native(uint32_t state,uint32_t source,uint32_t count,uint32_t output)
{
    r1_gomore_linear_native(source,count,25,count,output);
    (void)r1_gomore_filter_native(state,output,25);
    return 0;
}
uint32_t r1_gomore_ppg_kernel_native(uint32_t state,uint32_t source,uint32_t count,uint32_t output)
{
    r1_gomore_linear_native(source,count,25,count,output);
    return r1_gomore_filter_native(state,output,25);
}
