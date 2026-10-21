/* SPDX-License-Identifier: MIT
 * Native interactive line editor at stock 0x10005d1c. Its input source
 * is the selected UART getc wrapper; control bytes and width limit are
 * retained from the authenticated instruction stream.
 */
#include <stdint.h>

extern uint32_t gx8002_uart_stage2_shell_getc_6184(void);
extern void gx8002_uart_stage2_prepare_lower_618c(const void *);
extern void gx8002_uart_stage2_console_putc_2a84(uint32_t);
extern char *gx8002_uart_stage2_backspace_5c84(
    char *, char *, uint32_t *, uint32_t *, uint32_t);

int32_t gx8002_uart_stage2_read_line_core_5d1c(
    const char *prompt, char *buffer, uint32_t mode)
{
    (void)mode; /* Native entry r2 is unused. */
    uint32_t prompt_width = 0;
    if (prompt != 0) {
        const char *p = prompt;
        while (*p++ != '\0') ++prompt_width;
        gx8002_uart_stage2_prepare_lower_618c(prompt);
    }
    char *cursor = buffer;
    uint32_t characters = 0;
    uint32_t columns = prompt_width;
    static const char spaces[] = "        ";
    for (;;) {
        uint32_t raw = gx8002_uart_stage2_shell_getc_6184();
        uint8_t key = (uint8_t)raw;
        if (key == 10u || key == 13u) {
            *cursor = '\0';
            gx8002_uart_stage2_prepare_lower_618c("\r\n");
            return (int32_t)(cursor - buffer);
        }
        if (key == 3u) {
            buffer[0] = '\0';
            return -1;
        }
        if (key == 8u || key == 127u) {
            if (characters != 0u)
                cursor = gx8002_uart_stage2_backspace_5c84(
                    buffer, cursor, &columns, &characters, prompt_width);
            continue;
        }
        if (key == 0u) continue;
        if (key == 21u) {
            while (prompt_width < columns) {
                gx8002_uart_stage2_prepare_lower_618c("\b \b");
                --columns;
            }
            characters = 0;
            cursor = buffer;
            continue;
        }
        if (key == 23u) {
            while (characters != 0u) {
                cursor = gx8002_uart_stage2_backspace_5c84(
                    buffer, cursor, &columns, &characters, prompt_width);
                if (characters <= 0u || *cursor == ' ') break;
            }
            continue;
        }
        if (characters >= 62u) {
            gx8002_uart_stage2_console_putc_2a84(7u);
            continue;
        }
        if (key == 9u) {
            gx8002_uart_stage2_prepare_lower_618c(
                spaces + (columns & 7u));
            columns = (columns & ~UINT32_C(7)) + 8u;
        } else {
            char echo[2] = {(char)key, '\0'};
            ++columns;
            gx8002_uart_stage2_prepare_lower_618c(echo);
        }
        *cursor++ = (char)key;
        ++characters;
    }
}
