/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the fixed SRAM critical-transfer staging base
 * address consumed by the authenticated critical word-transfer dispatcher
 * (open_cfw_bootloader_word_transfer_critical_430b10, already source-routed
 * in runtime_late_wrappers_42fff2.c) through its own PC-relative literal
 * load.  The dispatcher's naked asm computes `ldr r0, [pc, #0xc]` and passes
 * the loaded word as the fixed destination-region argument to
 * open_cfw_bootloader_alignment_dispatch_42e4f4 inside a PRIMASK-guarded
 * critical section.
 *
 * The value 0x200270C8 is four bytes below the already-attributed SRAM cell
 * at 0x200270CC (see runtime_store_200270cc.c and
 * docs/research/g2-bootloader-store-200270cc-source-closure.md): that cell
 * is set by a single-word setter whose sole caller passes zero during
 * bootloader initialization.  0x200270C8 is therefore the base of the same
 * small SRAM staging structure, four bytes ahead of its documented word
 * field.  No additional field semantics are asserted here.
 *
 * See
 * docs/research/g2-bootloader-critical-transfer-base-literal-430b0c-source-closure.md
 * for the full derivation.
 */
typedef __UINT32_TYPE__ open_cfw_critical_transfer_base_u32;

__attribute__((used))
const open_cfw_critical_transfer_base_u32
open_cfw_bootloader_critical_transfer_base = 0x200270C8u;
