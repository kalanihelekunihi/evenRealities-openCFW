#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002b4c copy serial/identity words into OTA bank.
 */
#include <stdint.h>
extern void case_policy_box_read_serial(uint8_t *); /* 0x2f60 */
extern void case_policy_box_read_identity(uint8_t *); /* 0x2f88 */
extern void case_boot_option_prepare(void); /* 0x4bf4 */
extern uint32_t case_binary_5e_flash_program(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x4b94 */
extern void case_boot_option_commit_c(void); /* 0x4b20 */
static uint32_t be32(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
uint32_t case_policy_box_copy_sn(void)
{
    uint8_t serial[8],identity[16];
    case_policy_box_read_serial(serial);
    case_policy_box_read_identity(identity);
    case_boot_option_prepare();
    const uint32_t target=0x0807f000u;
    if(case_binary_5e_flash_program(1u,0x0807f800u,be32(serial+4u),be32(serial))!=0u)goto fail;
    if(case_binary_5e_flash_program(1u,target,be32(identity+4u),be32(identity))!=0u)goto fail;
    if(case_binary_5e_flash_program(1u,target+8u,be32(identity+12u),be32(identity+8u))!=0u)goto fail;
    case_boot_option_commit_c();return 1u;
fail:
    if(*(volatile const uint8_t *)(uintptr_t)0x200000bfu==0u){
        (void)case_policy_log(CASE_STRING_ADDR(08002c10));(void)case_policy_log(CASE_STRING_ADDR(08002c2c));
    }
    case_boot_option_commit_c();return 0u;
}
