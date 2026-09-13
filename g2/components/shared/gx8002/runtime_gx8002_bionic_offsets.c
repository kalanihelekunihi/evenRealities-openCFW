/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
/* Stock configuration enables BUNKWS adjustment and disables CTC adjustment. */
struct open_cfw_bionic_state {
    float ctc_offset, bunkws_offset;
    uint32_t ctc_counter, bunkws_counter;
};
_Static_assert(offsetof(struct open_cfw_bionic_state,bunkws_offset)==4,"offset ABI");
_Static_assert(offsetof(struct open_cfw_bionic_state,bunkws_counter)==12,"counter ABI");
extern struct open_cfw_bionic_state open_cfw_gx8002_bionic_state;
float open_cfw_gx8002_bunkws_offset(void *context, float threshold)
{
    (void)context; (void)threshold;
    return open_cfw_gx8002_bionic_state.bunkws_offset;
}
void open_cfw_gx8002_ctc_offset_clear(void) { }
void open_cfw_gx8002_bunkws_offset_clear(void)
{
    open_cfw_gx8002_bionic_state.bunkws_counter=0;
    open_cfw_gx8002_bionic_state.bunkws_offset=0.f;
}
