#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32cf94..0x32cfbe. ARC LP_COUNT=3 spans three iterations at
 * 0x32cfa4..0x32cfba; GCC's ARC doloop_end tests count!=1 then decrements.
 * Each enabled pass refreshes the mask byte after its store. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,
                                                           uint32_t);
uint32_t opencfw_em9305_mode_callback_32cf94(uintptr_t context,
                                               uintptr_t callback_code)
{
    (void)callback_code;
    uint8_t mask=em9305_ram_8027e0.u8_80281c;
    for (uint32_t index=0;index<3u;++index) {
        if ((mask&(uint8_t)(1u<<index))!=0u) {
            uint8_t value=em9305_ram_8027e0.u8_80281d;
            *(volatile uint8_t *)(context+598u+index)=value;
            mask=em9305_ram_8027e0.u8_80281c;
        }
    }
    return opencfw_em9305_receive_terminate_325c08(context,110u);
}
