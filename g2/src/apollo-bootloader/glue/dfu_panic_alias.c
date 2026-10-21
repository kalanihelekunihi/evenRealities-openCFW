/* SPDX-License-Identifier: MIT
 * DFU context's no-argument panic entry binds to stock Thumb 0x41b2f9.
 * The selected mask provider is byte-identical to that stock body.
 */
__attribute__((naked)) void opencfw_boot_dfu_panic(void)
{
    __asm__ volatile("b.w opencfw_bl_mask_interrupts");
}
