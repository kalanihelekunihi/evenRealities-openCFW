/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009d70 transport clock-error callback.
 */
#include <stdint.h>
extern void case_boot_transport_stop_clock(uint32_t channel); /* 0x6b80 */
extern void case_boot_transport_stop_link(uint32_t channel); /* 0x6b98 */
extern uint32_t case_policy_log(uint32_t message); /* 0x9170 */
void case_boot_transport_cb_9d70(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint8_t mode=state[2u];
    if(mode!=4u && mode!=3u){
        case_boot_transport_stop_clock(0u);
        case_boot_transport_stop_link(0u);
        state[2u]=0u;
        if(shared[7u]==0u){
            (void)case_policy_log(0x08009dbcu);
            (void)case_policy_log(0x08009dc8u);
        }
    }else if(shared[7u]==0u){
        (void)case_policy_log(0x08009dccu);
        (void)case_policy_log(0x08009dc8u);
    }
}
