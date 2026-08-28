/* SPDX-License-Identifier: BSD-3-Clause */
/* Source-equivalent adapter for AmbiqSuite 5.1.0 mspi_get_xip_off_min_delay. */

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_xip_off_delay_424a18(void)
{
    __asm__ volatile(
        "ldrb r1, [r0, #0xc]\n"
        "subs r1, r1, #6\n"
        "cmp r1, #3\n"
        "bls 4f\n"
        "subs r1, r1, #4\n"
        "cmp r1, #3\n"
        "bls 3f\n"
        "subs r1, r1, #4\n"
        "cmp r1, #1\n"
        "bls 2f\n"
        "subs r1, r1, #4\n"
        "cmp r1, #1\n"
        "bls 2f\n"
        "subs r1, r1, #2\n"
        "cmp r1, #3\n"
        "bhi 5f\n"
        "movs r1, #1\n"
        "str.w r1, [r0, #0x8cc]\n"
        "b 5f\n"
        "2:\nmovs r1, #2\nstr.w r1, [r0, #0x8cc]\nb 5f\n"
        "3:\nmovs r1, #4\nstr.w r1, [r0, #0x8cc]\nb 5f\n"
        "4:\nmovs r1, #8\nstr.w r1, [r0, #0x8cc]\nb 5f\n"
        "5:\nbx lr\n");
}
