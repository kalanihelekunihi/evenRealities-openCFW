/* UART debug-shell console output, native 0x5415b4..0x5415e5 (between the eAT
 * core pool 0x54157c..0x5415b3 and the shell RX callback 0x5415e6). UART
 * channel 1 is the console; uart_shell_init_54171c (rtos/rtos-glue-gaps)
 * installs shell_puts_5415c2 as the log output hook and the FreeRTOS-Plus-CLI
 * "cat" command (system/u-07) streams bytes through cli_putchar_5415d8. */
#include <stdint.h>
#include <stddef.h>

#define SHELL_UART_CHANNEL 1u

/* Board UART TX (uart-channel layer); the length is stored as a full word in
 * the transfer descriptor, so it is not limited to 8 bits. */
extern uint32_t hal_uart_send_55e7fa(uint8_t uart, const uint8_t *data, uint32_t len);
extern uint32_t g2_log_module_length(const char *text); /* strlen 0x44a43c */

void shell_write_5415b4(const uint8_t *data, uint32_t len);
void shell_puts_5415c2(const char *text);
void cli_putchar_5415d8(int32_t c);

/* Caller at 0x5bf96a. */
void shell_write_5415b4(const uint8_t *data, uint32_t len)
{
    (void)hal_uart_send_55e7fa(SHELL_UART_CHANNEL, data, len);
}

void shell_puts_5415c2(const char *text)
{
    (void)hal_uart_send_55e7fa(SHELL_UART_CHANNEL, (const uint8_t *)text, g2_log_module_length(text));
}

/* Sends the low byte of c from its stack slot. */
void cli_putchar_5415d8(int32_t c)
{
    uint8_t byte = (uint8_t)c;
    (void)hal_uart_send_55e7fa(SHELL_UART_CHANNEL, &byte, 1u);
}
