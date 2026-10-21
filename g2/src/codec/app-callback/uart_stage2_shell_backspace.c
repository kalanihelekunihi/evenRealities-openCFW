/* SPDX-License-Identifier: MIT
 * Native line-editor backspace helper 0x10005c84. The fifth argument is
 * the prompt width passed on the stack by 0x10005d1c.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_prepare_lower_618c(const void *);
extern void gx8002_uart_stage2_console_putc_2a84(uint32_t);

char *gx8002_uart_stage2_backspace_5c84(char *begin, char *end,
                                         uint32_t *columns,
                                         uint32_t *characters,
                                         uint32_t prompt_width)
{
    char *last = end - 1;
    if (*last != '\t') {
        gx8002_uart_stage2_prepare_lower_618c("\b \b");
        --*columns;
        --*characters;
        return last;
    }
    while (prompt_width < *columns) {
        gx8002_uart_stage2_prepare_lower_618c("\b \b");
        --*columns;
    }
    for (char *p = begin; p < last; ++p) {
        if (*p == '\t') {
            static const char spaces[] = "        ";
            gx8002_uart_stage2_prepare_lower_618c(spaces + (*columns & 7u));
            *columns = (*columns & ~UINT32_C(7)) + 8u;
        } else {
            ++*columns;
            gx8002_uart_stage2_console_putc_2a84((uint8_t)*p);
        }
    }
    --*characters;
    return last;
}
