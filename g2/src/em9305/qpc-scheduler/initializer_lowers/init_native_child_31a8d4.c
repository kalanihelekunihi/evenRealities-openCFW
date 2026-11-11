#include <stdint.h>

/* Native 0x31a8d4..0x31a900: when the scan state byte at 0x803561 is 2 or
 * more report error 0x0c; otherwise stop the two timers at 0x8035bc and
 * 0x8035cc. */
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t);

uint32_t opencfw_em9305_child_31a8d4(void)
{
    if(*(volatile uint8_t *)(uintptr_t)0x803561u>=2u)
        return opencfw_em9305_scan_error_30e7f8(0x0cu);
    (void)opencfw_em9305_wsf_timer_stop((uintptr_t)0x8035bcu);
    return opencfw_em9305_wsf_timer_stop((uintptr_t)0x8035ccu);
}
