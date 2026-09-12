/* SPDX-License-Identifier: MIT */
/*
 * Reviewed PMU rail-sequencing leaf for the GX8002 UART boot stage 1
 * (IRAM) image.
 *
 * Clean-room C implementing the decoded stock behavior of the rail
 * operation at runtime 0x10000B90 (package 0xBE0, 266 bytes of code):
 * one `pmu_fill_desc` call into a stack descriptor, entry-word gating,
 * a polled rail/status bit body with two MMIO store sequences, and the
 * shared pop-and-check spinner (no `rts`; the function never returns).
 * No SDK text is reproduced; only numeric MMIO patterns observed in the
 * decoded flow appear. See docs/research/gx8002-uart-stage1-railc-source.md.
 *
 * Behavior: fill(id, desc); on fill failure or null entry words the
 * first pass ends at the spinner. Otherwise a selector word is composed
 * from desc[1] plus the entry's low byte; when arg1 differs from its
 * low 25 bits the poll body runs: the desc[3] bit (entry byte 4) sets
 * desc[5] when present, the desc[2] cell bit (entry byte 6) selects one
 * of two seven-store sequences to the selector address with merged
 * arg1/status words, and a set desc[3] bit latches desc[4]. Every path
 * ends in the pop-and-check spinner, which re-pops the caller frame
 * and re-tests bit 27 of a carried word (handled by re-polling in
 * stock; this C remains in the spinner, see below).
 *
 * The checked word and observer depend on the path, all decoded from
 * stock: the skip arm jumps to the check without popping, so its first
 * check observes the live arg2 against the selector word; body paths
 * pop first, so theirs observes the popped caller r5 against
 * (cond<<27)|arg1, except that the desc[4] reload repoints the checked
 * word at the desc[4] address itself (a per-domain-constant address
 * bit). Past the first check r2 has decayed to 0/1, so later checks
 * always expect 1; the run re-polls by the third check at the latest.
 *
 * The spinner is an inline assembly loop that performs exactly the
 * stock 0xC5E sequence per pass (free the 24-byte frame, restore the
 * saved registers, repeat): the toolchain keeps no C state across it
 * (all locals are dead after the body; the verifier rejects any extra
 * prologue shape, so a toolchain change fails closed instead of
 * silently unbalancing the stack). The stock re-poll edge (branch back
 * into the body on a mismatching check) is intentionally not
 * reproduced: past the pops the body would re-read the caller frame
 * as descriptor words, which needs the caller (0xDDC orchestrator)
 * frame context owned by a later tranche. The admitted battery runs
 * stock through its re-poll decision (zero to two pops, exact
 * unfiltered traces) and matches the source through the same pops; the
 * divergence past that window is recorded as a followup, not silently
 * equated.
 *
 * Stock envelope (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_railc  runtime 0x10000B90,
 *   package 0xBE0, 266 bytes
 */
#include <stdint.h>

extern uint32_t open_cfw_gx8002_uart_stage1_pmu_fill_desc(uint32_t id,
                                                          volatile uint32_t *desc);

#define GX8002_STAGE1_RAILC_ZEXT_MASK 0x1FFFFFFu
#define GX8002_STAGE1_RAILC_SEQ_WORD 0x04000000u

#ifdef GX8002_STAGE1_RAILC_HOST
#define GX8002_STAGE1_RAILC_NORETURN
#else
#define GX8002_STAGE1_RAILC_NORETURN __attribute__((noreturn))
#endif

GX8002_STAGE1_RAILC_NORETURN void
open_cfw_gx8002_uart_stage1_railc(uint32_t id, uint32_t arg1, uint32_t arg2)
{
    volatile uint32_t desc[6];

    if (open_cfw_gx8002_uart_stage1_pmu_fill_desc(id, desc) == 0u) {
        /* desc[0] is read once (stock reads [sp+0] once); entry is
         * word-aligned (16-byte table stride) so +12 is one ld.w. */
        uint32_t e0 = desc[0];
        uint8_t *entry = (uint8_t *)(uintptr_t)e0;
        uint32_t w3 = ((volatile uint32_t *)(uintptr_t)e0)[3];
        /* Single volatile read: stock samples the entry byte once and
         * reuses it for the gate and the selector. */
        uint8_t b0 = (w3 != 0u) ? *(volatile uint8_t *)(uintptr_t)w3 : 0u;
        if (w3 != 0u && b0 != 0u) {
            uint32_t sel = desc[1] + b0;
            volatile uint32_t *selp = (volatile uint32_t *)(uintptr_t)sel;
            uint32_t v = *selp;
            if (arg1 != (v & GX8002_STAGE1_RAILC_ZEXT_MASK)) {
                /* Entry/status bytes are volatile: the stock poll order
                 * (entry+4, then desc[3]-bit arm, then desc[2]-cell
                 * status) is observable MMIO order and must not be
                 * reordered or merged. */
                int8_t b4 = *(volatile int8_t *)(entry + 4);
                uint32_t cond = (arg2 == 0u) ? 1u : 0u;
                volatile uint32_t *mcell = (volatile uint32_t *)(uintptr_t)desc[2];
                int8_t b6 = *(volatile int8_t *)(entry + 6);
                uint32_t r0bit;
                uint32_t m;
                uint32_t r1bit;
                uint32_t r2c;
                uint32_t r2b;
                if (b4 < 0) {
                    r0bit = 0u;
                } else {
                    r0bit = ((*(volatile uint32_t *)(uintptr_t)desc[3] >>
                              (uint32_t)b4) & 1u);
                    if (r0bit != 0u)
                        *(volatile uint32_t *)(uintptr_t)desc[5] =
                            (1u << (uint32_t)b4);
                }
                /* Pin the status read after the arm: without this the
                 * toolchain hoists the desc[2]-cell load above the
                 * desc[3]/desc[5] traffic, changing observable order. */
                __asm__ volatile ("" ::: "memory");
                m = *mcell;
                r1bit = ((m >> ((uint32_t)b6 & 31u)) & 1u);
                r2c = ((cond << 27) | arg1);
                r2b = (r2c | 0x06000000u);
                if (r1bit != 0u) {
                    uint32_t one = (1u << ((uint32_t)b6 & 31u));
                    uint32_t merged = (r2c | GX8002_STAGE1_RAILC_SEQ_WORD);
                    /* Stock re-reads the cell before clearing (fresh
                     * status, not the bit-test snapshot). */
                    *mcell = (*mcell & (uint32_t)(~(uint32_t)one));
                    *selp = GX8002_STAGE1_RAILC_SEQ_WORD;
                    *selp = 0u;
                    *selp = GX8002_STAGE1_RAILC_SEQ_WORD;
                    *selp = merged;
                    *selp = r2b;
                    *selp = r2b;
                    *selp = merged;
                    m = *mcell;
                    *mcell = (one | (m & (uint32_t)(~(uint32_t)one)));
                } else {
                    uint32_t merged = (r2c | GX8002_STAGE1_RAILC_SEQ_WORD);
                    *selp = GX8002_STAGE1_RAILC_SEQ_WORD;
                    *selp = 0u;
                    *selp = GX8002_STAGE1_RAILC_SEQ_WORD;
                    *selp = merged;
                    *selp = r2b;
                    *selp = r2b;
                    *selp = merged;
                }
                if (r0bit != 0u)
                    *(volatile uint32_t *)(uintptr_t)desc[4] =
                        (1u << (uint32_t)b4);
            }
        }
    }
    /* Target-only pop-and-check spinner (stock 0xC5E): free the frame,
     * restore exactly the registers the prologue saved, and repeat.
     * The host test build omits it (same body, plain return) via
     * GX8002_STAGE1_RAILC_HOST. */
#ifndef GX8002_STAGE1_RAILC_HOST
    __asm__ volatile (
        "1:\n\t"
        "addi r14, r14, 24\n\t"
        "pop r4-r5, r15\n\t"
        "br 1b\n\t"
        ::: "r4", "r5", "r15", "memory");
    __builtin_unreachable();
#else
    return;
#endif
}
