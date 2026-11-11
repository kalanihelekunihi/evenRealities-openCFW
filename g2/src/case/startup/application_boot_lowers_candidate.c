/* SPDX-License-Identifier: MIT
 * Stock option-control register operations 0x08004bf4, 0x08004b6c,
 * 0x08004b3c, 0x08004b50, and 0x08004b20.
 */
#include <stdint.h>
static volatile uint32_t *const flash=(volatile uint32_t *)(uintptr_t)0x40022000u;
/* Stock 0x08004BF4 (HAL_FLASH_Unlock, KEYR at +0x08) */
uint32_t case_boot_option_prepare(void)
{
    if((flash[5]&0x80000000u)!=0u){
        flash[2]=0x45670123u;
        flash[2]=0xcdef89abu;
        if((flash[5]&0x80000000u)!=0u)return 1u;
    }
    return 0u;
}
/* Stock 0x08004B6C (HAL_FLASH_OB_Unlock, OPTKEYR at +0x0C) */
uint32_t case_boot_option_unlock(void)
{
    if((flash[5]&0x40000000u)!=0u){
        flash[3]=0x08192a3bu;
        flash[3]=0x4c5d6e7fu;
        if((flash[5]&0x40000000u)==0u)return 0u;
    }
    return 1u;
}
/* Stock 0x08004B3C (case_flag27_set) */
uint32_t case_boot_option_commit_a(void){flash[5]|=0x08000000u;return 1u;}
/* Stock 0x08004B50 (case_flag30_set) */
uint32_t case_boot_option_commit_b(void)
{flash[5]|=0x40000000u;return (flash[5]&0x40000000u)!=0u?0u:1u;}
uint32_t case_boot_option_commit_c(void)
{flash[5]|=0x80000000u;return (flash[5]&0x80000000u)!=0u?0u:1u;}
/* Dedup (0x08004b20): case_binary_5e_flash_finish (was legacy-default/flash_lock_helpers_candidate.c). */
uint32_t case_binary_5e_flash_finish(void) __attribute__((alias("case_boot_option_commit_c")));
/* Dedup (0x08004bf4): case_binary_5e_flash_init (was legacy-default/flash_lock_helpers_candidate.c). */
uint32_t case_binary_5e_flash_init(void) __attribute__((alias("case_boot_option_prepare")));
