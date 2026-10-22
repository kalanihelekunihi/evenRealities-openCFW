/* SPDX-License-Identifier: MIT
 * Native CASE 0x08006782 alternate enable reader and 0x080067a2
 * bitfield write, recovered from direct-call census.
 */
#include <stdint.h>
/* Stock 0x08006782 (case_status_word2_bit0_alias) */
uint32_t case_policy_adc_enabled_alias_6782(uint32_t base)
{return *(volatile uint32_t *)(uintptr_t)(base+8u)&1u;}
/* Stock 0x080067A2 (case_control_word0_replace_field22) */
void case_policy_adc_write_control_67a2(uint32_t base,uint32_t bits)
{
    volatile uint32_t *register_word=(volatile uint32_t *)(uintptr_t)base;
    *register_word=(*register_word&~(7u<<22))|bits;
}
