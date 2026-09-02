/* SPDX-License-Identifier: BSD-3-Clause */
/* Apollo510 SPOT-manager profile-to-register application at 0x0042AB7C. */

typedef __UINT32_TYPE__ open_cfw_spotmgr_profile_u32;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_spotmgr_profile_u32
open_cfw_bootloader_spotmgr_profile_apply_42ab7c(void)
{
    __asm volatile(
        "ldr r0, [pc, #0xd0]\n"
        "ldr r1, [r0]\n"
        "ldr r2, [pc, #0x160]\n"
        "cmp r1, r2\n"
        "bne.n .Lprofile_done\n"
        "ldr r1, [pc, #0x1a4]\n"
        "ldr r2, [r0, #0x20]\n"
        "lsrs r2, r2, #7\n"
        "ldr r3, [r1]\n"
        "bfi r3, r2, #0, #10\n"
        "str r3, [r1]\n"
        "ldr r1, [pc, #0x198]\n"
        "ldr r2, [r0, #0x68]\n"
        "lsrs r2, r2, #2\n"
        "ldr r3, [r1]\n"
        "bfi r3, r2, #0, #6\n"
        "str r3, [r1]\n"
        "ldr r1, [pc, #0x190]\n"
        "ldr r0, [r0, #0x68]\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #15, #2\n"
        "str r2, [r1]\n"
        ".Lprofile_done:\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

#else

typedef struct open_cfw_spotmgr_profile_state {
    open_cfw_spotmgr_profile_u32 magic;
    open_cfw_spotmgr_profile_u32 reserved_04_1c[7];
    open_cfw_spotmgr_profile_u32 profile_word_20;
    open_cfw_spotmgr_profile_u32 reserved_24_64[17];
    open_cfw_spotmgr_profile_u32 profile_word_68;
} open_cfw_spotmgr_profile_state;

__attribute__((used, noinline, visibility("default")))
open_cfw_spotmgr_profile_u32
open_cfw_bootloader_spotmgr_profile_apply_42ab7c(
    const open_cfw_spotmgr_profile_state *state,
    open_cfw_spotmgr_profile_u32 *profile_register,
    open_cfw_spotmgr_profile_u32 *core_register,
    open_cfw_spotmgr_profile_u32 *memory_register)
{
    if (state->magic == 0x1F01600DU) {
        *profile_register = (*profile_register & ~0x3FFU) |
                            ((state->profile_word_20 >> 7) & 0x3FFU);
        *core_register = (*core_register & ~0x3FU) |
                         ((state->profile_word_68 >> 2) & 0x3FU);
        *memory_register = (*memory_register & ~(3U << 15)) |
                           ((state->profile_word_68 & 3U) << 15);
    }
    return 0U;
}

#endif
