/* SPDX-License-Identifier: MIT
 * Stock option-control register operations 0x08004bf4, 0x08004b6c,
 * 0x08004b3c, 0x08004b50, and 0x08004b20. Callers ignore their R0 status.
 */
#include <stdint.h>
static volatile uint32_t *const flash=(volatile uint32_t *)(uintptr_t)0x40022000u;
void case_boot_option_prepare(void)
{if((flash[5]&0x80000000u)!=0u){flash[2]=0x45670123u;flash[2]=0xcdef89abu;}}
void case_boot_option_unlock(void)
{if((flash[5]&0x40000000u)!=0u){flash[3]=0x08192a3bu;flash[3]=0x4c5d6e7fu;}}
void case_boot_option_commit_a(void){flash[5]|=0x08000000u;}
void case_boot_option_commit_b(void){flash[5]|=0x40000000u;}
void case_boot_option_commit_c(void){flash[5]|=0x80000000u;}
