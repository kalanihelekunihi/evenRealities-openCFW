/* SPDX-License-Identifier: MIT */
/* Recovered backup console forwarding; driver and port storage remain external. */
extern int backup_console_port;
extern void backup_uart_putc(int port, int character);
void backup_console_putc(int character)
{
    backup_uart_putc(backup_console_port, character);
}
void backup_putchar(char character)
{
    backup_console_putc(character);
}
