/* SPDX-License-Identifier: MIT */
typedef __UINT8_TYPE__ open_cfw_orphan_u8;
typedef __UINT32_TYPE__ open_cfw_orphan_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_orphan_u32 open_cfw_bootloader_mode_provider_430a60(
    open_cfw_orphan_u32 handle, open_cfw_orphan_u32 mode);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_orphan_u32 open_cfw_bootloader_mode_four_wrapper_430aec(
    open_cfw_orphan_u32 handle)
{
    __asm volatile(
        "push {r4, lr}\nmovs r4, r0\nmovs r1, #4\nmovs r0, r4\n"
        "bl open_cfw_bootloader_mode_provider_430a60\ncmp r0, #0\nbeq 1f\n"
        "movs r0, r4\nmov r8, r8\nmov r8, r8\nmovs r0, #0\nb 2f\n"
        "1:\nmovs.w r0, #-1\n2:\npop {r4, pc}\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_zero_table_431e38(const open_cfw_orphan_u32 *table)
{
    __asm volatile(
        "push {r4, r5}\nmovs r5, #0\nb 3f\n"
        "1:\nldr r2, [r0], #4\nlsls r3, r2, #31\nitt mi\n"
        "addmi r2, r9\nsubmi r2, r2, #1\n"
        "2:\nsubs r1, r1, #4\ncmp r1, #4\nstr r5, [r2], #4\nbhs 2b\n"
        "mov r3, r2\nlsls r4, r1, #30\nitt mi\nstrhmi r5, [r2]\n"
        "addmi r3, r3, #2\nlsls r1, r1, #31\nit mi\nstrbmi r5, [r3]\n"
        "3:\nldr r1, [r0], #4\ncmp r1, #0\nbne 1b\n"
        "pop {r4, r5}\nbx lr\n"
    );
}
#else
typedef open_cfw_orphan_u32 (*open_cfw_mode_provider)(open_cfw_orphan_u32 handle,
                                                       open_cfw_orphan_u32 mode,
                                                       void *context);
__attribute__((used, noinline, visibility("default")))
open_cfw_orphan_u32 open_cfw_bootloader_mode_four_wrapper_430aec_portable(
    open_cfw_orphan_u32 handle, open_cfw_mode_provider provider, void *context)
{
    return provider(handle, 4U, context) != 0U ? 0U : 0xFFFFFFFFU;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_orphan_u32 open_cfw_bootloader_zero_table_431e38_portable(
    const open_cfw_orphan_u32 *table, open_cfw_orphan_u8 *memory,
    open_cfw_orphan_u32 memory_size, open_cfw_orphan_u32 relative_base)
{
    for (;;) {
        open_cfw_orphan_u32 length = *table++;
        open_cfw_orphan_u32 descriptor;
        open_cfw_orphan_u32 offset;
        open_cfw_orphan_u32 index;
        if (length == 0U) return 0U;
        descriptor = *table++;
        offset = (descriptor & 1U) != 0U
            ? relative_base + descriptor - 1U : descriptor;
        if (offset > memory_size || length > memory_size - offset) return 1U;
        for (index = 0U; index < length; ++index) memory[offset + index] = 0U;
    }
}
#endif
