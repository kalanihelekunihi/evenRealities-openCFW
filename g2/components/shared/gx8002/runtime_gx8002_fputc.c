/* SPDX-License-Identifier: MIT */
/* Recovered console-backed libc port; console dependency not yet qualified. */
extern void open_cfw_gx8002_console_putc(int character);
int open_cfw_gx8002_fputc(int character, void *stream)
{
    (void)stream;
    open_cfw_gx8002_console_putc(character);
    return 0;
}
