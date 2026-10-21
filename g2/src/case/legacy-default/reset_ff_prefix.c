/* SPDX-License-Identifier: MIT
 * Native 0xff logging and reset entry. The sourced child writes AIRCR and
 * stays in the stock idle loop; physical reset is outside emulator proof.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
extern uint32_t case_legacy_reset_first(uint32_t prior);
static const char case_ff_reason[]="Reset, reason: cmd.";
static const char case_ff_newline[]="\r\n";
uint32_t case_legacy_ff_prefix(const uint8_t *command,uint32_t length)
{
    (void)command;(void)length;
    const uint8_t flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t prior=flag;
    if(flag==0u){
        (void)case_legacy_logger(case_ff_reason);
        prior=case_legacy_logger(case_ff_newline);
    }
    return case_legacy_reset_first(prior);
}
