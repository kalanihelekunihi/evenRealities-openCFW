#include <stdint.h>

/* Native 0x31a32c..0x31a34c: report the fixed extended-init LL event whose
 * three halfwords live in ROM at 0x33444c. */
extern const uint16_t opencfw_em9305_ext_init_event_33444c[3];
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

uint32_t opencfw_em9305_child_31a32c(void)
{
    uint16_t event[3];
    event[0] = opencfw_em9305_ext_init_event_33444c[0];
    event[1] = opencfw_em9305_ext_init_event_33444c[1];
    event[2] = opencfw_em9305_ext_init_event_33444c[2];
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
