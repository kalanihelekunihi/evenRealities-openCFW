/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002f46 running-bank selection from option words.
 */
#include <stdint.h>
extern void case_boot_read_option_words(uint32_t *words); /* 0x4a00 */
uint32_t case_policy_box_running_bank(void)
{
    uint32_t words[7];
    case_boot_read_option_words(words);
    return (words[6]&0x00100000u)!=0u?1u:2u;
}
