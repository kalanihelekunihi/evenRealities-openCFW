/* SPDX-License-Identifier: MIT
 * Stock 0x080012e4 clear-LED exit wrapper; control and logger are lower cuts.
 */
#include <stdint.h>

extern uint32_t case_binary_56_cancel(uint32_t task);
extern void case_binary_56_clear_a(uint32_t value);
extern void case_binary_56_clear_b(uint32_t value);
extern uint32_t case_binary_56_exit_log(const char *format, ...);

uint32_t case_binary_56_exit(void)
{
    uint32_t task = *(volatile uint32_t *)(uintptr_t)0x200000d0u;
    case_binary_56_cancel(task);
    case_binary_56_clear_a(0u);
    case_binary_56_clear_b(0u);
    *(volatile uint8_t *)(uintptr_t)0x2000087eu = 0u;
    uint32_t flag = *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (flag != 0u)
        return flag;
    case_binary_56_exit_log("clear led status.");
    return case_binary_56_exit_log("\r\n");
}
