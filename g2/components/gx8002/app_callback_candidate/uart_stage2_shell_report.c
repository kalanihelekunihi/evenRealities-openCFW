/* SPDX-License-Identifier: MIT
 * Stage-2 shell command-list evaluator at stock 0x10005b28. The native
 * 140-byte frame places a status word immediately before the 64-byte
 * text buffer, so the first quote's preceding byte is initialized zero.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_shell_clear_interrupt_5ab4(void);
extern uint32_t gx8002_uart_stage2_shell_interrupted_5aa8(void);
extern uint32_t gx8002_uart_stage2_strlen_62fc(const char *);
extern void gx8002_uart_stage2_copy_string_6260(char *, const char *);
extern uint32_t gx8002_uart_stage2_split_args_5ac0(char *, char **);
extern int32_t gx8002_uart_stage2_dispatch_6018(uint32_t, uint32_t,
                                                 char **, uint32_t *);
extern void gx8002_uart_stage2_prepare_lower_618c(const void *);

int32_t gx8002_uart_stage2_report_lower_5b28(const char *message,
                                               uint32_t mode)
{
    uint32_t status = 1u;
    gx8002_uart_stage2_shell_clear_interrupt_5ab4();
    if (message == 0 || *message == '\0') return -1;
    if (gx8002_uart_stage2_strlen_62fc(message) >= 64u) {
        gx8002_uart_stage2_prepare_lower_618c("## Command too long!\n");
        return -1;
    }
    char text[64];
    gx8002_uart_stage2_copy_string_6260(text, message);
    char *segment = text;
    int32_t last_result = 0;
    for (;;) {
        char *scan = segment;
        uint32_t quoted = 0;
        while (*scan != '\0') {
            char previous = scan == text ? '\0' : scan[-1];
            if (*scan == '\'' && previous != '\\')
                quoted ^= 1u;
            if (!quoted && *scan == ';') {
                if (scan == segment || previous == '\\') {
                    ++scan;
                    continue;
                }
                *scan++ = '\0';
                break;
            }
            ++scan;
        }
        char *arguments[17];
        uint32_t argc = gx8002_uart_stage2_split_args_5ac0(segment,
                                                               arguments);
        if (argc == 0u) {
            last_result = -1;
        } else {
            last_result = gx8002_uart_stage2_dispatch_6018(
                mode, argc, arguments, &status) != 0 ? -1 : 0;
            if (gx8002_uart_stage2_shell_interrupted_5aa8() != 0u)
                return -1;
        }
        segment = scan;
        if (*segment == '\0') return last_result != 0 ? -1 : (int32_t)status;
    }
}
