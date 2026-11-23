#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31a8d4..0x31a900: when the scan state byte at ((uintptr_t)&em9305_ram_803560 + 0x1u) is 2 or
 * more report error 0x0c; otherwise stop the two timers at ((uintptr_t)&em9305_ram_803560 + 0x5cu) and
 * ((uintptr_t)&em9305_ram_8035c0 + 0xcu). */
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t);

uint32_t opencfw_em9305_child_31a8d4(void)
{
    if(em9305_ram_803560.u8_803561>=2u)
        return opencfw_em9305_scan_error_30e7f8(0x0cu);
    (void)opencfw_em9305_wsf_timer_stop((uintptr_t)((uintptr_t)&em9305_ram_803560 + 0x5cu));
    return opencfw_em9305_wsf_timer_stop((uintptr_t)((uintptr_t)&em9305_ram_8035c0 + 0xcu));
}
