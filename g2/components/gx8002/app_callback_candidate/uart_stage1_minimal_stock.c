/* SPDX-License-Identifier: MIT
 * These are authentic minimal stock bodies: 0x10000130 is a self branch,
 * and 0x10000138 is a direct return. They do not stand in for omitted work.
 */

__attribute__((noreturn)) void gx8002_uart_stage1_traps(void)
{
    for (;;) { }
}

void gx8002_uart_stage1_clear_bss(void)
{
}
