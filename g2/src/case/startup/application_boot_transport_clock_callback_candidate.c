#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009d70 transport clock-error callback.
 */
#include <stdint.h>
extern void case_boot_transport_stop_clock(uint32_t channel); /* 0x6b80 */
extern void case_boot_transport_stop_link(uint32_t channel); /* 0x6b98 */
void case_boot_transport_cb_9d70(uint32_t argument)
{
    /* Native trampoline supplies pair[1] in R0; this callback ignores it. */
    (void)argument;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint8_t mode=state[2u];
    if(mode!=4u && mode!=3u){
        case_boot_transport_stop_clock(0u);
        case_boot_transport_stop_link(0u);
        state[2u]=0u;
        if(shared[7u]==0u){
            (void)case_policy_log(CASE_STRING_ADDR(08009dbc));
            (void)case_policy_log(CASE_STRING_ADDR(08009dc8));
        }
    }else if(shared[7u]==0u){
        (void)case_policy_log(CASE_STRING_ADDR(08009dcc));
        (void)case_policy_log(CASE_STRING_ADDR(08009dc8));
    }
}
