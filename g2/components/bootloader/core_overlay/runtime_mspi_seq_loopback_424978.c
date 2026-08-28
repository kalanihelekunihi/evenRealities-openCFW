/* SPDX-License-Identifier: BSD-3-Clause */
/* Source-equivalent adapter for AmbiqSuite 5.1.0 mspi_seq_loopback. */

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_seq_loopback_424978(void)
{
    __asm__ volatile(
        "ldr.w r1, [r0, #0x830]\n"
        "adds r1, r1, #1\n"
        "str r1, [r0, #0x20]\n"
        "movs r1, #0\n"
        "str r1, [r0, #0x1c]\n"
        "movs r1, #1\n"
        "strb.w r1, [r0, #0x834]\n"
        "movs r1, #0x40\n"
        "ldr r0, [r0, #4]\n"
        "ldr.w r2, [pc, #0x814]\n"
        "adds.w r2, r2, r0, lsl #12\n"
        "str.w r1, [r2, #0x2b4]\n"
        "bx lr\n");
}
