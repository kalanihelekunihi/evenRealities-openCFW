/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader unsigned 64-bit
 * divmod divide-by-zero tail at 0x004275E8..0x004275EA.
 *
 * The stock tail is a shared two-byte return (`bx lr`) reached by
 * tail-branch from the byte-exact divmod loader at 0x004228E0 on
 * the zero-divisor path: it returns to the divmod caller's caller
 * with the dividend registers undisturbed. There is no store,
 * literal, call, or status effect; the reconstruction is the same
 * single return instruction at the same address.
 */

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_u64_divzero_4275e8(void)
{
    __asm__ volatile("bx lr\n");
}
#else
__attribute__((used, noinline))
void open_cfw_bootloader_u64_divzero_4275e8(void)
{
}
#endif
