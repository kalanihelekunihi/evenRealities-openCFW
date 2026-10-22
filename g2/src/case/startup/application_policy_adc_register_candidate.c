/* SPDX-License-Identifier: MIT
 * Native CASE 0x4eac, 0x678a, 0x6792 register readers.
 */
#include <stdint.h>
uint32_t case_policy_adc_tick(void)
{return *(volatile uint32_t *)(uintptr_t)0x20000120u;}
/* Stock 0x0800678A (case_status_word2_bit2) */
uint32_t case_policy_adc_ready(uint32_t base)
{return (*(volatile uint32_t *)(uintptr_t)(base+8u)>>2)&1u;}
/* Stock 0x0800677A (case_status_word2_bit0) */
uint32_t case_policy_adc_enabled(uint32_t base)
{return (*(volatile uint32_t *)(uintptr_t)(base+8u))&1u;}
/* Stock 0x08006792 (case_status_word3_field10_clear) */
uint32_t case_policy_adc_special(uint32_t base)
{return ((*(volatile uint32_t *)(uintptr_t)(base+12u)>>10)&3u)==0u;}
