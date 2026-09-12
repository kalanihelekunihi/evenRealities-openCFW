/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the MSPI aperture-base mask word at
 * 0x0042644C..0x00426450.
 *
 * The word sits inside the retained 436-byte control-dispatcher
 * tail (0x0042612C..0x004262E0) after the source-owned MSPI control
 * dispatcher returns. It is the XIP aperture-base address mask
 * 0x1FFF0000, spelled in the reviewed OpenCFW AmbiqSuite adaptation
 * runtime_mspi_control_4251c0.c (`(pXipConfig->ui32APBaseAddr &
 * (uint32_t)0x1FFF0000)` when setting the DEV0AXI aperture base
 * address). The stock loader at 0x004257BC (`ldr.w r0, [pc,
 * #0xC8C]` then `ands r3, r0; orrs r1, r3`) performs exactly that
 * mask-and-merge step.
 *
 * The loader PC was verified by anchored per-span Capstone decode
 * of the routed spans plus a sync-independent whole-window encoding
 * sweep (see docs/research/g2-bootloader-bl006-cluster-427c80-
 * 42644c-source-closure.md): it is the only loader anywhere, it
 * sits in the replaced control-upstream span whose shipped
 * replacement carries only R_ARM_THM_CALL relocations (stale by
 * construction), and no image word anywhere equals the slot
 * address. Reproduced here as a named layout word, not as claimed
 * live traffic.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Word at 0x0042644C: XIP aperture-base address mask. */
struct __attribute__((packed)) open_cfw_bl006_word_42644c {
    open_cfw_bl006_u32 aperture_base_mask; /* 0x1FFF0000: XIP
        aperture-base mask (reviewed
        runtime_mspi_control_4251c0.c DEV0AXI setup; stale loader
        in the replaced control-upstream body at 0x004257BC). */
};

__attribute__((used, section(".rodata.bl006_word_42644c")))
const struct open_cfw_bl006_word_42644c open_cfw_bootloader_bl006_word_42644c = {
    0x1FFF0000u
};
