/* SPDX-License-Identifier: MIT */
/*
 * Reviewed millisecond-delay leaf for the GX8002 UART boot stage 1
 * (IRAM) image.
 *
 * Clean-room C implementing the decoded stock behavior of the delay
 * routine at runtime 0x100003FC (package 0x44C, 112 bytes of code),
 * identified against the pinned NationalChip grus SDK
 * `arch/soc/grus/spl/spl_counter.c` (commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5; SDK repo-level MIT
 * LICENSE blob 37a1e362999f2040c2c0cda1a3231b6b5913efbf) as an
 * inlined `spl_mdelay`/`spl_udelay(1000)` pair: the outer
 * post-decrement loop, the single 64-bit counter-2 snapshot plus 1000
 * per millisecond, and the strict-less-than poll
 * (`while (now < tmp + 1)`, constant-folded to a +1001 deadline with a
 * greater-or-equal exit) are the SDK shapes; the counter-2 register
 * addresses (VALUE +0x04, ACCSNAP +0x08 under GX_REG_BASE_COUNTER
 * 0xA0400000) and the 1 MHz rate (1 tick per microsecond) are the only
 * numeric facts crossing the boundary. No SDK text is reproduced. See
 * docs/research/gx8002-uart-stage1-mdelay-source.md and
 * NATIONALCHIP-UART-BOOT-STAGE1-MDELAY-NOTICE.txt.
 *
 * Behavior: waits n milliseconds (n times ~1001 counter ticks), then
 * restores its saved registers and tail-chains into the retained
 * rail-configure flow at 0x1000046C (a genuine external boundary, same
 * precedent as the reviewed reset entry's chain-load into retained
 * stage two). The argument register reads 0xFFFFFFFF at the handoff on
 * every path (the post-decrement can only exit through the wrapped
 * value) and is carried as the handoff argument. The millisecond
 * count, the +1000/+1 deadline arithmetic, and the snapshot/poll read
 * counts match stock exactly.
 *
 * The single inline assembly statement reproduces the stock
 * pop-then-chain transfer: the toolchain keeps this leaf's deadline
 * state in callee-saved registers across the call-free poll loop and,
 * for a noreturn tail call, would otherwise skip its own epilogue,
 * leaving saved caller registers unrestored where stock has already
 * popped them. The statement restores exactly the registers the
 * prologue saved (the verifier rejects any other prologue shape, so a
 * toolchain change fails closed instead of silently unbalancing the
 * stack); the chained call then runs with the caller registers in
 * place, as in stock. The link register clobbered by the chaining
 * branch is dead: the 0x1000046C flow saves it on entry and never
 * returns, so it is excluded from the comparison (documented, not
 * ignored).
 *
 * Stock envelope (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_mdelay  runtime 0x100003FC,
 *   package 0x44C, 112 bytes
 */
#include <stdint.h>

#ifndef GX8002_STAGE1_COUNTER_BASE
#define GX8002_STAGE1_COUNTER_BASE ((uintptr_t)0xA0400000u)
#endif
#define GX8002_STAGE1_COUNTER_VALUE ((volatile uint32_t *)(GX8002_STAGE1_COUNTER_BASE + 0x04u))
#define GX8002_STAGE1_COUNTER_ACCSNAP ((volatile uint32_t *)(GX8002_STAGE1_COUNTER_BASE + 0x08u))
#define GX8002_STAGE1_MDELAY_USEC_PER_MSEC 1000u

extern __attribute__((noreturn)) void
open_cfw_gx8002_uart_boot_stage1_46c_entry(uint32_t r0carry);

static uint64_t gx8002_stage1_counter_us(void)
{
    uint32_t lo = *GX8002_STAGE1_COUNTER_VALUE;
    uint64_t hi = *GX8002_STAGE1_COUNTER_ACCSNAP;
    return (hi << 32) | lo;
}

__attribute__((noreturn)) void
open_cfw_gx8002_uart_stage1_mdelay(uint32_t msec)
{
    while (msec--) {
        uint64_t tmp = gx8002_stage1_counter_us() +
            GX8002_STAGE1_MDELAY_USEC_PER_MSEC;
        while (gx8002_stage1_counter_us() < tmp + 1u)
            ;
    }
    /* Target-only machine-state restore; the host test build omits it
     * (same wait logic, stub handoff) via GX8002_STAGE1_MDELAY_HOST. */
#ifndef GX8002_STAGE1_MDELAY_HOST
    __asm__ volatile ("pop r4-r5, r15" ::: "r4", "r5", "r15", "memory");
#endif
    open_cfw_gx8002_uart_boot_stage1_46c_entry(msec);
}
