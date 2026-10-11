/* SPDX-License-Identifier: MIT
 * Isolated 0xa5 Set SN request with explicit hex and apply children.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
extern void case_legacy_hex_log(const uint8_t *bytes, uint32_t count);
extern uint32_t case_legacy_set_sn(const uint8_t *bytes);
static const char case_a5_label[] = "Set SN:";
uint32_t case_legacy_a5_branch(const uint8_t *command, uint32_t length)
{
    const uint8_t flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(length<8u)return flag;
    if(flag==0u)(void)case_legacy_logger(case_a5_label);
    case_legacy_hex_log(command,8u);
    return case_legacy_set_sn(command);
}
