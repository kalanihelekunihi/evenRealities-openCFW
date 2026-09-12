/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: three two-byte alignment halfwords between
 * exact source-owned bodies in 0x00422712..0x00422AD4.
 *
 * Assemblers pad odd-length code to the next halfword/word boundary so the
 * following entry stays aligned. Each constant below reproduces one
 * authenticated pad with its neighbors documented; see
 * docs/research/g2-bootloader-bl006-cluster-4220b2-422ad4-source-closure.md.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;

/* 0xBF00 (Thumb NOP): pads the double ldexp wrapper (ends 0x00422712) so
 * the ldexp core entry at 0x00422714 is word-aligned. */
__attribute__((used, section(".rodata.bl006_align_422712")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_align_422712 = 0xBF00u;

/* 0x0000: pads the double multiply leaf (ends 0x00422872) so the IAR
 * thread-pointer leaf entry at 0x00422874 is word-aligned. */
__attribute__((used, section(".rodata.bl006_align_422872")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_align_422872 = 0x0000u;

/* 0x0000: pads the retained query wrapper (ends 0x00422AD2) so the
 * four-instance hardware-service initializer entry at 0x00422AD4 is
 * word-aligned. */
__attribute__((used, section(".rodata.bl006_align_422ad2")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_align_422ad2 = 0x0000u;
