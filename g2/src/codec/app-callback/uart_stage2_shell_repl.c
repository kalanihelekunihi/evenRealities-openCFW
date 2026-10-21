/* SPDX-License-Identifier: MIT
 * Stock shell read/evaluate loop at 0x10005bf8. Native `bhz` is signed
 * greater-than-zero and `mvcv` yields the inverted compare flag; those
 * controls are preserved in the retry paths below.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_read_line_5e60(const char *prompt);
extern uint32_t gx8002_uart_stage2_copy_bounded_64dc(
    char *destination, const char *source, uint32_t count);
extern int32_t gx8002_uart_stage2_report_5c64(
    const char *message, uint32_t mode);
extern void gx8002_uart_stage2_prepare_lower_618c(const void *literal);

__attribute__((noreturn)) void gx8002_uart_stage2_prepare_lower_5bf8(void)
{
    char *const command = (char *)(uintptr_t)UINT32_C(0x20009984);
    const char *const input = (const char *)(uintptr_t)UINT32_C(0x2000a158);
    int32_t previous = 1;
    int32_t received;
read_again:
    received = gx8002_uart_stage2_read_line_5e60("boot> ");
    if (received > 0) goto process_line;
    goto handle_nonpositive;
process_line:
    (void)gx8002_uart_stage2_copy_bounded_64dc(command, input, 65u);
    previous = gx8002_uart_stage2_report_5c64(command, 0u);
    if (previous > 0) goto read_again;
retry:
    command[0] = '\0';
    received = gx8002_uart_stage2_read_line_5e60("boot> ");
    if (received > 0) goto process_line;
handle_nonpositive:
    if (received == -1) {
        gx8002_uart_stage2_prepare_lower_618c("<INTERRUPT>\n");
    } else {
        previous = gx8002_uart_stage2_report_5c64(command,
                                                    received == 0 ? 1u : 0u);
    }
    if (previous > 0) goto read_again;
    goto retry;
}
