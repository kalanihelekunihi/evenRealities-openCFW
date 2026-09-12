/* SPDX-License-Identifier: MIT */
/*
 * Reviewed PMU descriptor-fill leaf for the GX8002 UART boot stage 1
 * (IRAM) image.
 *
 * Clean-room C implementing the decoded stock behavior of the
 * descriptor-fill routine at runtime 0x10000780, identified against the
 * pinned NationalChip grus SDK `arch/soc/grus/include/base_addr.h`
 * (commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5; SDK repo-level MIT
 * LICENSE blob 37a1e362999f2040c2c0cda1a3231b6b5913efbf): only the
 * numeric domain bases cross the boundary --
 * GX_REG_BASE_MCU_CONFIG (0xA0300000) with MCU_CFG_SOURCE_SEL (+0x88)
 * and the MEPG_CLK_INHIBIT_NORM/1SET/1CLR triple (+0x18/+0x1C/+0x20),
 * and GX_REG_BASE_PMU_CONFIG (0xA0010000) with PMU_CFG_SOURCE_SEL0
 * (+0x8C) and the same inhibit triple. The 26-entry table base
 * (0x20002018), the 16-byte entry stride, the direct/index-0/scan match
 * order, and the id < 10 domain select were recovered from the decoded
 * stock control flow. No SDK text is reproduced. See
 * docs/research/gx8002-uart-stage1-pmufill-source.md and
 * NATIONALCHIP-UART-BOOT-STAGE1-PMUFILL-NOTICE.txt.
 *
 * The routine fills a six-word clock descriptor for a peripheral id in
 * 0..25: word[0] receives the matching 16-byte table entry's address
 * (direct hit at entry id, else entry 0 on match, else a linear scan of
 * entries 1..25), words[1..5] receive the domain base, the domain's
 * source-select register, and the inhibit NORM/1SET/1CLR triple with
 * bit 5 set in the last word (already set by the +0x20 offset, matching
 * the stock `bseti`). Ids below 10 select the PMU config domain, ids
 * 10..25 the MCU config domain (the stock falls through to the MCU
 * stores when `cmphsi id, 10` holds). Ids above 25, a null descriptor,
 * and a failed scan return 0xFFFFFFFF; success returns 0. The stock's
 * redundant null check on the computed (never null) entry address is
 * dead and is not reproduced; the leading `desc[0] = 0` store is.
 *
 * Stock envelope (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_pmu_fill_desc  runtime 0x10000780, package 0x7D0, 84 bytes
 * (the 12-byte literal pool at runtime 0x10000834 stays retained stock).
 */
#include <stdint.h>

#ifndef GX8002_STAGE1_DESC_TABLE_BASE
#define GX8002_STAGE1_DESC_TABLE_BASE ((uintptr_t)0x20002018u)
#endif
#define GX8002_STAGE1_DESC_MAX_ID 25u
#define GX8002_STAGE1_DESC_PMU_ID_MAX 10u
#define GX8002_STAGE1_DESC_MCU_BASE 0xA0300000u
#define GX8002_STAGE1_DESC_PMU_BASE 0xA0010000u

uint32_t open_cfw_gx8002_uart_stage1_pmu_fill_desc(uint32_t id,
    volatile uint32_t *desc)
{
    const uint32_t *table =
        (const uint32_t *)GX8002_STAGE1_DESC_TABLE_BASE;
    uint32_t base;
    uint32_t select;
    uint32_t slot;

    if (id > GX8002_STAGE1_DESC_MAX_ID || desc == (uint32_t *)0)
        return 0xffffffffu;
    desc[0] = 0u;
    if (table[id * 4u] == id)
        slot = id;
    else if (table[0] == id)
        slot = 0u;
    else {
        slot = 1u;
        for (;;) {
            if (table[slot * 4u] == id)
                break;
            if (slot == GX8002_STAGE1_DESC_MAX_ID)
                return 0xffffffffu;
            slot++;
        }
    }
    desc[0] = (uint32_t)(uintptr_t)(table + slot * 4u);
    if (id < GX8002_STAGE1_DESC_PMU_ID_MAX) {
        base = GX8002_STAGE1_DESC_PMU_BASE;
        select = 0x8cu;
    } else {
        base = GX8002_STAGE1_DESC_MCU_BASE;
        select = 0x88u;
    }
    desc[1] = base;
    desc[2] = base | select;
    desc[3] = base | 0x18u;
    desc[4] = base | 0x1cu;
    desc[5] = base | 0x20u;
    return 0u;
}
