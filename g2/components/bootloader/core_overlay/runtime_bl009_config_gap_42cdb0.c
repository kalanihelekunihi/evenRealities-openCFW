/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: routed scalar cells of the 72-byte
 * configuration literal pool at 0x0042CDB0 between the hardware instance
 * validator (ends 0x0042CDB0) and the state-adjustment service (starts
 * 0x0042CDF8).
 *
 * This pool is consumed ~31 times by original literal loads in already
 * source-routed neighbours (ownership claim, context enable, interrupt
 * helpers, event service, configuration transaction, instance
 * configurator), whose successors embed equivalent constants in their
 * own pools. Only cells with an identified scalar meaning are routed
 * here; SRAM-table bases (0x2001455C), the range bound word 0x20080000
 * (kept with its unattributed-table walk), and the three two-word
 * 0x2301-tagged records (0x0042CDE0..0x0042CDF8) stay retained stock.
 *
 * Routed cells:
 * - 0x0042CDB0: 0x01123456, masked-identifier compare constant
 *   (original consumers, e.g. 0x0042C548, mask the loaded word with
 *   BIC #0xFE000000 and compare).
 * - 0x0042CDB8: 0x00123456, revision-pattern OR word (original
 *   consumer 0x0042C51C: keep top byte, ORR this word, store back).
 * - 0x0042CDBC: 0x00800040, configuration store word (original
 *   consumer 0x0042C592: `str.w r1, [r0, #0x238]`).
 * - 0x0042CDC0 / 0x0042CDC8: 0x40050000, peripheral register-block
 *   base (indexed field loads, same block as the 0x0042C6E8 cell).
 * - 0x0042CDC4: 0xFFFFFBFE, field-preserve bitmask (original consumer
 *   0x0042C800: read-modify-write AND over a register field).
 * - 0x0042CDCC: 0x02DC6C01, range-bound compare constant (original
 *   consumer 0x0042CC9C: `cmp r0, r1` / `blo`).
 * - 0x0042CDD0: 0x000F4240 = 1,000,000, clock-divisor constant
 *   (original consumer 0x0042CCCE: `udiv r0, r0, r1`).
 * - 0x0042CDD8: 0x000186A0 = 100,000, clock-divisor constant.
 * - 0x0042CDDC: 0x00061A80 = 400,000, clock-divisor constant
 *   (original consumer 0x0042CD4C).
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_42cdb0 {
    open_cfw_bl009_u32 id_compare;
    open_cfw_bl009_u32 revision_or;
    open_cfw_bl009_u32 config_store;
    open_cfw_bl009_u32 reg_block_base0;
    open_cfw_bl009_u32 field_mask;
    open_cfw_bl009_u32 reg_block_base1;
    open_cfw_bl009_u32 range_bound;
    open_cfw_bl009_u32 divisor_1m;
    open_cfw_bl009_u32 divisor_100k;
    open_cfw_bl009_u32 divisor_400k;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42cdb0
open_cfw_bootloader_bl009_gap_42cdb0 = {
    0x01123456u, 0x00123456u, 0x00800040u, 0x40050000u, 0xFFFFFBFEu,
    0x40050000u, 0x02DC6C01u, 0x000F4240u, 0x000186A0u, 0x00061A80u
};
