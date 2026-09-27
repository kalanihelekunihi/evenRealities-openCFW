/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two dead bootloader remainder tails
 * with internal control flow but no literal load and no call:
 *
 *  C. command-queue status remainder at 0x00427ABE..0x00427AD6
 *     (24 B), the surviving end of the replaced command-queue
 *     status service. Registers on entry (set by the replaced
 *     head): r0 = status word, r4 = byte-state pointer,
 *     r5 = queue-state pointer. The tail clears the pending flag,
 *     tests the status word against the mask thread
 *     *(r5 + 0x24) -> *(... + 0x20), publishes the booleanized hit
 *     at r4 + 0x0E, zeroes r0, and returns through the head-owned
 *     register block:
 *       *(r4 + 0x0D) = 0
 *       hit = (status & *(mask_link + 0x20)) != 0 ? 1 : 0
 *       *(r4 + 0x0E) = hit
 *       return 0 via pop {r1, r4, r5, pc}
 *
 *  D. binary32 remainder-code remainder at 0x00427D84..0x00427D98
 *     (20 B), the surviving end of the replaced binary32
 *     remainder-code service. Registers on entry: r0..r3 carry the
 *     head's operands, r4 is head-owned and restored. The tail
 *     conditionally complements r0 under the incoming carry flag,
 *     restores r4 into the return slot, and either transfers to
 *     the range-error setter entry at 0x004275C4 (carry clear) or
 *     returns:
 *       if (C) r0 = ~r3
 *       else { apsr = r1 + r2; if (!Z) r0 = ~r3 }
 *       restore r4; (C clear) ? goto 0x004275C4 : return
 *     The `blo.w` target is the System-PLL alternate setter entry
 *     admitted in this same turn (identical bytes in the built
 *     image). It is expressed as a reviewed `R_ARM_THM_JUMP19`
 *     relocation against that fixed-address entry, so the source
 *     carries the conditional transfer semantics without a raw
 *     instruction transcript. The MVN/CMN flag detail is pinned by
 *     the host twin, which takes the incoming APSR explicitly
 *     because the HS path leaves the head's flags untouched.
 *
 * Both spans are unreachable in the built image: the status span
 * sits in a region the whole-image retained survey grades
 * corroborated_unreachable_control_flow, while the remainder-code
 * span grades `no_control_flow_reference_found` (zero inbound
 * references; its heads were already replaced). A whole-image
 * `bl` sweep finds no caller of either entry. The reconstructions
 * document the bytes from reviewed source and pin the behavior
 * the replaced heads must cover; no live traffic is claimed. See
 * docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_sb_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_SB_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_SB_ATTR __attribute__((used, noinline))
#endif

/* Tail C: command-queue status remainder. */
OPEN_CFW_BL006_SB_ATTR
open_cfw_bl006_sb_u32 open_cfw_bootloader_cmdq_status_rem_tail_427abe(
    open_cfw_bl006_sb_u32 status,
    void *ctx4,
    void *ctx5)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "movs r1, #0\n"
        "strb r1, [r4, #0xd]\n"
        "ldr r1, [r5, #0x24]\n"
        "ldr r1, [r1, #0x20]\n"
        "tst r0, r1\n"
        "beq 0f\n"
        "movs r0, #1\n"
        "b 1f\n"
        "0: movs r0, #0\n"
        "1: strb r0, [r4, #0xe]\n"
        "movs r0, #0\n"
        "pop {r1, r4, r5, pc}\n");
#else
    /* Host twin: r4/r5 arrive as explicit context pointers; the
     * stock tail threads r5 + 0x24 -> link + 0x20 for the mask. */
    open_cfw_bl006_sb_u32 *b4 = (open_cfw_bl006_sb_u32 *)ctx4;
    open_cfw_bl006_sb_u32 *b5 = (open_cfw_bl006_sb_u32 *)ctx5;
    unsigned char *c4 = (unsigned char *)ctx4;
    void *link = *(void **)(b5 + 0x24U / 4U);
    open_cfw_bl006_sb_u32 mask =
        *(open_cfw_bl006_sb_u32 *)((unsigned char *)link + 0x20U);
    c4[0x0DU] = 0;
    c4[0x0EU] = (unsigned char)((status & mask) != 0U ? 1U : 0U);
    (void)b4;
    return 0U;
#endif
}

/* Tail D: binary32 remainder-code remainder. */
OPEN_CFW_BL006_SB_ATTR
void open_cfw_bootloader_binary32_rem_tail_427d84(
    open_cfw_bl006_sb_u32 r0,
    open_cfw_bl006_sb_u32 r1,
    open_cfw_bl006_sb_u32 r2,
    open_cfw_bl006_sb_u32 r3,
    open_cfw_bl006_sb_u32 apsr_in,
    open_cfw_bl006_sb_u32 *r0_out,
    open_cfw_bl006_sb_u32 *branch_out)
{
#if defined(__arm__) || defined(__thumb__)
    /* The closing `blo.w` targets 0x004275C4, which lies outside
     * this section.  A reviewed fixed-address JUMP19 relocation is
     * attached to the canonical `blo.w .` placeholder; the in-place
     * extractor verifies the global undefined STT_NOTYPE symbol and
     * materializes the stock `ff f4 17 ac` conditional branch. */
    __asm__ volatile(
        "ite hs\n"
        "mvnhs r0, r3\n"
        "cmnlo r1, r2\n"
        "it ne\n"
        "mvnne r0, r3\n"
        "pop.w {r4, lr}\n"
        ".reloc ., R_ARM_THM_JUMP19, open_cfw_bootloader_syspll_alt_entry_4275c4\n"
        "blo.w .\n"
        "bx lr\n");
#else
    /* Host twin with an explicit APSR model (bit 29 = C, bit 30 =
     * Z). The HS path performs no flag-setting instruction, so
     * the head's incoming flags decide both the second IT block
     * and the final branch; the LO path re-derives them from
     * r1 + r2 exactly as the stock CMN does. */
    open_cfw_bl006_sb_u32 out = r0;
    open_cfw_bl006_sb_u32 carry = (apsr_in >> 29U) & 1U;
    open_cfw_bl006_sb_u32 zero = (apsr_in >> 30U) & 1U;
    if (carry == 0U) {
        unsigned long long sum =
            (unsigned long long)r1 + (unsigned long long)r2;
        open_cfw_bl006_sb_u32 s = (open_cfw_bl006_sb_u32)sum;
        zero = (s == 0U) ? 1U : 0U;
        carry = (sum >> 32U) & 1U;
        if (zero == 0U) {
            out = ~r3;
        }
    } else {
        out = ~r3;
    }
    *r0_out = out;
    *branch_out = (carry == 0U) ? 1U : 0U;
    (void)r1;
    (void)r2;
#endif
}
