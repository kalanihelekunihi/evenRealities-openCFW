/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room return-zero tail authenticated at G2
 * bootloader address 0x0042D848.
 *
 * The tail is a two-instruction leaf (`movs r0, #0; bx lr`) between
 * the state-flag dispatcher literal pool (ends 0x0042D848) and the
 * stream-mode selection primitive (starts 0x0042D84C) inside the
 * retained span 0x0042D5C2..0x0042D84C (BL-009). Its Thumb entry
 * 0x0042D849 is stored at vector index 14 of the 0x0041D150 dispatch
 * vector alongside the routed dispatcher, trim leaves and SPOTmgr
 * entries, which attributes it as a callable leaf rather than pool
 * padding. It takes no arguments, touches no memory and reports
 * success (0). No Apollo main twin exists: the main vector differs
 * at this index, so corroboration here is the stored-pointer entry
 * plus dual-toolchain byte-exactness.
 */

typedef __UINT32_TYPE__ open_cfw_zero_tail_u32;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_zero_tail_u32 open_cfw_bootloader_zero_tail_42d848(void)
{
    __asm volatile(
        "movs r0, #0\n"
        "bx lr\n"
    );
}

#else

__attribute__((used, noinline, visibility("default")))
open_cfw_zero_tail_u32 open_cfw_bootloader_zero_tail_42d848_portable(void)
{
    return 0u;
}

#endif
