/* SPDX-License-Identifier: MIT
 * Native CASE boot logger at 0x9170, with caller-provided format arguments.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format,...);
void case_boot_log(uint32_t format,uint32_t a,uint32_t b)
{(void)case_legacy_logger((const char *)(uintptr_t)format,a,b);}
