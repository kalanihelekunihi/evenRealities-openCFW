/* SPDX-License-Identifier: MIT
 * UART stage-2 reset at 0x10002900. Stage 1 calls this entry directly.
 * Native control-register setup, stack 0x2000e7fc, and three startup calls
 * are retained; the three child bodies are separate stage-2 source work.
 */

extern void gx8002_uart_stage2_init_clock(void);
extern void gx8002_uart_stage2_init_runtime(void);
extern void gx8002_uart_stage2_enter_application(void);

__attribute__((naked, noreturn)) void gx8002_uart_stage1_second_entry(void)
{
    __asm__ volatile(
        "lrw r0, 0x80000200\n"
        "mtcr r0, cr<0,0>\n"
        "mfcr r1, cr<31,0>\n"
        "bclri r1, 3\n"
        "mtcr r1, cr<31,0>\n"
        "lrw r14, 0x2000e7fc\n"
        "bsr gx8002_uart_stage2_init_clock\n"
        "bsr gx8002_uart_stage2_init_runtime\n"
        "bsr gx8002_uart_stage2_enter_application\n"
        "1: br 1b\n");
}
