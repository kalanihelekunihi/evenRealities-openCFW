/* SPDX-License-Identifier: MIT
 * Stock 0x08002c8e packs enable/disable into one-byte control frames.
 * Caller instructions show R2 points at a stack byte for both 0x9004 calls.
 */
#include <stdint.h>
extern uint32_t case_watchdog_frame_pack(uint32_t code,uint32_t count,
                                         const uint8_t *byte); /* 0x08009004 */
uint32_t case_legacy_watchdog_set(uint32_t enabled)
{
    uint8_t byte=0u;
    if(enabled!=0u){
        byte=0x3bu;
        (void)case_watchdog_frame_pack(5u,1u,&byte);
        byte=7u;
    }
    return case_watchdog_frame_pack(4u,1u,&byte);
}
