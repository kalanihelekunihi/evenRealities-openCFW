/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800bb4c transport side-toggle callback.
 */
#include <stdint.h>
extern void case_boot_transport_stop_clock(uint32_t value); /* 0x6b80 */
void case_boot_transport_cb_bb4c(uint32_t argument)
{
    /* Native trampoline supplies pair[1] in R0; this callback ignores it. */
    (void)argument;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    uint8_t mode=state[2u];
    if(mode==3u || mode==4u){
        volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
        uint8_t next=shared[12u]^1u;
        shared[12u]=next;
        case_boot_transport_stop_clock(next);
    }
}
