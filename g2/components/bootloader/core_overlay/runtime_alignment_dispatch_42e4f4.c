/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room alignment-gated dispatch authenticated at G2
 * bootloader address 0x0042E4F4.
 */

typedef __UINT32_TYPE__ open_cfw_align_u32;

#define OPEN_CFW_ALIGNMENT_ERROR 0x08000140U

#if defined(__arm__) || defined(__thumb__)

extern open_cfw_align_u32 open_cfw_bootloader_aligned_provider_42e4a0(
    open_cfw_align_u32 first, open_cfw_align_u32 second,
    open_cfw_align_u32 length, open_cfw_align_u32 destination);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_align_u32 open_cfw_bootloader_alignment_dispatch_42e4f4(
    open_cfw_align_u32 first, open_cfw_align_u32 second,
    open_cfw_align_u32 length, open_cfw_align_u32 destination)
{
    __asm volatile(
        "push {r4, lr}\n"
        "ands r4, r2, #15\n"
        "cmp r4, #0\n"
        "bne 1f\n"
        "tst.w r3, #3\n"
        "beq 2f\n"
        "1:\n"
        "ldr r0, [pc, #8]\n"
        "b 3f\n"
        "2:\n"
        "bl open_cfw_bootloader_aligned_provider_42e4a0\n"
        "3:\n"
        "pop {r4, pc}\n"
    );
}

#else

typedef open_cfw_align_u32 (*open_cfw_aligned_provider)(
    open_cfw_align_u32 first, open_cfw_align_u32 second,
    open_cfw_align_u32 length, open_cfw_align_u32 destination,
    void *context);

__attribute__((used, noinline, visibility("default")))
open_cfw_align_u32 open_cfw_bootloader_alignment_dispatch_42e4f4_portable(
    open_cfw_align_u32 first, open_cfw_align_u32 second,
    open_cfw_align_u32 length, open_cfw_align_u32 destination,
    open_cfw_aligned_provider provider, void *context)
{
    if ((length & 15U) != 0U || (destination & 3U) != 0U) {
        return OPEN_CFW_ALIGNMENT_ERROR;
    }
    return provider(first, second, length, destination, context);
}

#endif
