/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader double-ldexp
 * range-error tail at 0x004275D2..0x004275E4.
 *
 * The stock tail runs on the soft-float ldexp overflow/underflow
 * paths (reached by tail-branch from the byte-exact ldexp scaling
 * core at 0x00422748): it publishes 0x22 to the range-error status
 * cell at 0x20027194 and returns to the ldexp wrapper's caller with
 * the scaled result already in d0. The stock body preserves r0-r3
 * (push {r0-r3, lr} / pop {r0-r3, pc}); this reconstruction
 * preserves r0 and r3 untouched and saves/restores the two scratch
 * registers it uses, so the observable register and memory behavior
 * matches. The stock `mov r8, r8` is an IAR code-alignment no-op
 * and is not reproduced.
 *
 * The cell address is overridable for host testing without touching
 * the reviewed target spelling.
 */

typedef __UINT32_TYPE__ open_cfw_range_error_u32;

#ifndef OPEN_CFW_BOOTLOADER_RANGE_ERROR_4275D2_TARGET
#define OPEN_CFW_BOOTLOADER_RANGE_ERROR_4275D2_TARGET \
    ((volatile open_cfw_range_error_u32 *)(__UINTPTR_TYPE__)0x20027194U)
#endif
#define OPEN_CFW_BOOTLOADER_RANGE_ERROR_4275D2_CODE 0x22U

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, noinline))
void open_cfw_bootloader_double_range_error_4275d2(void)
{
    __asm__ volatile(
        "push {r1, r2}\n"
        "movw r1, #0x7194\n"
        "movt r1, #0x2002\n"
        "movs r2, #0x22\n"
        "str r2, [r1]\n"
        "pop {r1, r2}\n");
}
#else
__attribute__((used, noinline))
void open_cfw_bootloader_double_range_error_4275d2(void)
{
    *OPEN_CFW_BOOTLOADER_RANGE_ERROR_4275D2_TARGET =
        (open_cfw_range_error_u32)OPEN_CFW_BOOTLOADER_RANGE_ERROR_4275D2_CODE;
}
#endif
