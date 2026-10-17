/* Experimental stock 0x080012e4 clear-LED wrapper: native ADR references
 * both address-named strings at 0x0800131c and 0x08001330. */
#include <stdint.h>

extern uint32_t case_binary_56_cancel(uint32_t task);
extern void case_binary_56_clear_a(uint32_t value);
extern void case_binary_56_clear_b(uint32_t value);
extern uint32_t case_binary_56_exit_log(const char *format, ...);
extern const char case_string_0800131c[];
extern const char case_string_08001330[];

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
    case_binary_56_exit_log(case_string_0800131c);
    return case_binary_56_exit_log(case_string_08001330);
}
