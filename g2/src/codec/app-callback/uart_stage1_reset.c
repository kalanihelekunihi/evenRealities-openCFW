/* SPDX-License-Identifier: MIT
 * UART boot stage-1 reset at 0x10000100. A naked entry is required before
 * stack initialization. The second call targets the distinct UART stage-2
 * reset at 0x10002900 (stage-2 image base 0x10002800, offset 0x100).
 */

extern void gx8002_uart_stage1_startup_dispatch(void);
extern void gx8002_uart_stage1_second_entry(void);

/* Stock 0x10000100 (gx8002_uart_boot_stage1_reset) */
__attribute__((naked, noreturn)) void gx8002_uart_stage1_reset(void)
{
    __asm__ volatile(
        "lrw r0, 0x80000200\n"
        "mtcr r0, cr<0,0>\n"
        "mfcr r1, cr<31,0>\n"
        "bclri r1, 3\n"
        "mtcr r1, cr<31,0>\n"
        "lrw r0, 0x10000000\n"
        "mtcr r0, cr<1,0>\n"
        "lrw r14, 0x200027fc\n"
        "bsr gx8002_uart_stage1_startup_dispatch\n"
        "bsr gx8002_uart_stage1_second_entry\n"
        "bkpt\n");
}
