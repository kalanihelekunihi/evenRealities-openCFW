#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800b7ec aging mode entry and exit callback.
 */
#include <stdint.h>
extern void case_boot_transport_left_aging(uint32_t enabled); /* 0x23f4 */
extern void case_boot_transport_right_aging(uint32_t enabled); /* 0x24c0 */
extern uint32_t case_policy_service_idle(void); /* 0xd154 */
extern uint32_t case_legacy_logger(const char *,...);
extern __attribute__((noreturn)) void case_init_display_reset(void); /* 0x502c */

void case_boot_transport_cb_b7ec(void)
{
    volatile uint8_t *device=(volatile uint8_t *)(uintptr_t)0x200000f4u;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    if(device[7u]==4u && device[4u]!=0u && device[5u]<3u){
        device[5u]++;
        if(device[2u]==0u)case_boot_transport_left_aging(1u);
        if(device[3u]==0u)case_boot_transport_right_aging(1u);
        if(shared[7u]==0u){
            (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800b948),device[2u],device[3u],device[5u]);
            (void)case_policy_log(CASE_STRING_ADDR(0800b988));
        }
        if(device[2u]!=0u && device[3u]!=0u){
            device[7u]=1u;shared[2u]=0u;
            if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(0800d690));(void)case_policy_log(CASE_STRING_ADDR(0800b988));}
            return;
        }
        if(device[5u]==3u){
            device[7u]=1u;shared[2u]=0u;
            if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(0800d6d8));(void)case_policy_log(CASE_STRING_ADDR(0800b988));}
            return;
        }
    }
    if(device[6u]!=2u && device[6u]!=3u)return;
    if(device[2u]!=0u || device[3u]!=0u){
        if(shared[7u]==0u){
            (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800b9a0),
                    (const char *)(uintptr_t)(device[6u]==2u?CASE_STRING_ADDR(0800b9a8):CASE_STRING_ADDR(0800b994)));
            if(shared[7u]==0u){
                (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800b9b4),device[2u],device[3u]);
                (void)case_policy_log(CASE_STRING_ADDR(0800b988));
            }
        }
        if(state[21u]==0u){
            state[21u]=1u;(void)case_policy_service_idle();state[16u]=0u;state[17u]=0u;
            if(shared[7u]==0u){
                (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800b9a0),
                        (const char *)(uintptr_t)(device[6u]==2u?CASE_STRING_ADDR(0800b9a8):CASE_STRING_ADDR(0800b994)));
                if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(0800b9e4));(void)case_policy_log(CASE_STRING_ADDR(0800b988));}
            }
        }
    }else if(device[6u]==3u){
        if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(0800ba04));(void)case_policy_log(CASE_STRING_ADDR(0800b988));}
        case_init_display_reset();
    }
    if(state[16u]!=0u && device[2u]!=0u)case_boot_transport_left_aging(0u);
    if(state[17u]!=0u && device[3u]!=0u)case_boot_transport_right_aging(0u);
}
