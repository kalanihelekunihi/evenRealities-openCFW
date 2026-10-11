/* SPDX-License-Identifier: MIT
 * Direct native shell helpers 0x10005aa8/0x10005ab4 (interrupt flag),
 * 0x10005ac0 (in-place argument split), and 0x10006260 (string copy).
 */
#include <stdint.h>

static const char too_many_args_format[] =
    "** Too many args (max. %d) **\n";
extern int32_t gx8002_uart_stage2_launch_61a4(const char *format, ...);

uint32_t gx8002_uart_stage2_shell_interrupted_5aa8(void)
{
    return *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x20009980);
}

void gx8002_uart_stage2_shell_clear_interrupt_5ab4(void)
{
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20009980) = 0;
}

void gx8002_uart_stage2_copy_string_6260(char *destination,
                                           const char *source)
{
    for (;;) {
        const char byte = *source++;
        *destination++ = byte;
        if (byte == 0) break;
    }
}

uint32_t gx8002_uart_stage2_split_args_5ac0(char *text, char **arguments)
{
    uint32_t count = 0;
    for (;;) {
        while (*text == ' ' || *text == '\t') ++text;
        if (*text == '\0') {
            arguments[count] = 0;
            return count;
        }
        arguments[count++] = text;
        uint32_t quoted = 0;
        char *p = text;
        while (*p != '\0') {
            if (*p == '\'' && (p == text || p[-1] != '\\'))
                quoted ^= 1u;
            if (!quoted && (*p == ' ' || *p == '\t')) break;
            ++p;
        }
        if (*p == '\0') {
            arguments[count] = 0;
            return count;
        }
        *p = '\0';
        text = p + 1;
        if (count == 16u) {
            gx8002_uart_stage2_launch_61a4(too_many_args_format, 16);
            return count;
        }
    }
}
