#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002d48 erase inactive OTA bank with four attempts.
 */
#include <stdint.h>
extern void case_boot_option_prepare(void); /* 0x4bf4 */
extern uint32_t case_boot_option_erase_execute(uint32_t,uint32_t *); /* 0x497c */
extern void case_boot_option_commit_c(void); /* 0x4b20 */
extern void case_policy_wait(uint32_t); /* 0xa7b0 */
uint32_t case_policy_box_erase_bank(void)
{
    volatile uint32_t *operation=(volatile uint32_t *)(uintptr_t)0x200001a4u;
    volatile uint8_t *box=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t error=0u;
    case_boot_option_prepare();
    operation[0]=2u;
    operation[1]=box[0x18u]==1u?0x8000u:4u;
    operation[2]=0u;
    operation[3]=128u;
    uint32_t retries=0u;
    while(case_boot_option_erase_execute((uint32_t)(uintptr_t)operation,&error)!=0u){
        if(retries++==3u){
            if(*quiet==0u){(void)case_policy_log(CASE_STRING_ADDR(08002dc8),128u,error,retries);(void)case_policy_log(CASE_STRING_ADDR(08002e00));}
            case_boot_option_commit_c();
            return 0u;
        }
        case_policy_wait(200u);
    }
    case_boot_option_commit_c();
    return 1u;
}
