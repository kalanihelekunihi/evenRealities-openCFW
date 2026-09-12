/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: four retained two-byte zero-alignment
 * fills at 0x00426DB2, 0x00426F6A, 0x004276BA, and 0x00427752.
 *
 * Each halfword is stock assembler-emitted alignment between two
 * routed service spans and has no loader in any routed span of the
 * authenticated image (bounded Capstone decode; the verifier pins
 * this). They are reproduced here as explicit named zero fills, not
 * as claimed data; see
 * docs/research/g2-bootloader-bl006-cluster-426d2c-427754-source-closure.md.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;

/* Fill at 0x00426DB2: pads the replaced floating common-divisor span
 * (ends 0x00426DB2) before the floating-ratio redirect entry at
 * 0x00426DB4. */
__attribute__((used, section(".rodata.bl006_pad_426db2")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_pad_426db2 = 0x0000u;

/* Fill at 0x00426F6A: pads the replaced floating-multiplier span
 * (ends 0x00426F6A) before the floating encoding-selector redirect
 * entry at 0x00426F6C. */
__attribute__((used, section(".rodata.bl006_pad_426f6a")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_pad_426f6a = 0x0000u;

/* Fill at 0x004276BA: pads the source-owned queue item-get body end
 * (0x004276BA) before the memmove entry redirect at 0x004276BC. */
__attribute__((used, section(".rodata.bl006_pad_4276ba")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_pad_4276ba = 0x0000u;

/* Fill at 0x00427752: pads the memmove NOP-fill tail end
 * (0x00427752) before the command-queue index-updater redirect at
 * 0x00427754. */
__attribute__((used, section(".rodata.bl006_pad_427752")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_pad_427752 = 0x0000u;
