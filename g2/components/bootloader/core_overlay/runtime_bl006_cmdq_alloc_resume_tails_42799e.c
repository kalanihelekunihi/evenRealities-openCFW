/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two dead G2 bootloader interiors:
 *
 *  K. command-queue allocator remainder at 0x0042799E..0x004279BE
 *     (32 B), the surviving interior of the replaced stock block
 *     allocator (live replacement:
 *     open_cfw_bootloader_cmdq_alloc_block_42790a in
 *     runtime_cmdq_services_427794.c). Registers on entry are
 *     head-owned (r4-r7 hold the allocator frame; r6 is the
 *     command count). Three entries, all fed only from the
 *     replaced head:
 *       K1 at 0x0042799E (fallthrough from the head wrap-load):
 *         r0 = wrap slot, r1 = buffer-start word. Publishes the
 *         word, reloads the base into r0, and rejoins the head
 *         success path:
 *           slot[1] = r1; r0 = frame[1]; (b 0x00427970)
 *       K2 at 0x004279A4 (head range-check miss):
 *         returns the allocator failure code 5, then leaves
 *         through the head epilogue:
 *           r0 = 5; (b 0x00427984)
 *       K3 at 0x004279A8 (head slow-path bounds check):
 *         with base = frame[4], lim = frame[3], idx = r6:
 *           t = base + ((idx + 1) << 3)
 *           r0 = (t >= lim) ? 5 : base
 *         then rejoins the head success path (base) or the head
 *         epilogue (5):
 *           (b 0x00427970 / b 0x00427984)
 *     All arithmetic is unsigned 32-bit wrap; the bounds compare
 *     is unsigned (bhs).
 *
 *  L. command-queue error-resume remainder at 0x00427B90..0x00427BAA
 *     (26 B), the surviving end of the replaced stock error-resume
 *     service (live replacement:
 *     open_cfw_bootloader_cmdq_error_resume_427b38 in
 *     runtime_cmdq_services_427794.c). Two entries, both fed only
 *     from the replaced head:
 *       L1 at 0x00427B90 (head scan-loop fallthrough): loops back
 *         into the head scan (b 0x00427B76). Non-returning.
 *       L2 at 0x00427B92 (head match exit): r0 = found entry,
 *         r1 = queue handle. Publishes the queue-address register
 *         value into the entry, publishes the entry pointer into
 *         its register slot, clears prefix bit 25 (the
 *         command-queue ENABLED word, same bit the
 *         enable/disable/reset tails maintain), and returns
 *         success:
 *           *entry = qaddr_val; *qaddr_slot = entry
 *           prefix &= ~0x2000000; return 0
 *
 * Out-of-span branches: the relocatable object assembles at
 * address 0, so the five narrow unconditional exits into the
 * replaced heads cannot name far-absolute mnemonic operands
 * ("branch target out of range"). Each is spelled with its
 * reviewed 16-bit encoding (`.inst.n`); the internal `bhs` names
 * a local label normally. The six assembler probes below prove
 * the reference assembler emits the identical bytes for an
 * identical branch at the identical offset (same precedent as
 * the binary32 remainder tail's `.inst.w`). The byte-exact
 * rebuild test pins every emission.
 *
 * The whole-image survey grades both spans
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of any entry, so no leaf executes in the
 * shipped image; the reconstructions document the bytes and pin
 * the behavior the replaced AmbiqSuite-adapted heads already
 * cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-42799e-427b90-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_ax_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_AX_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_AX_ATTR __attribute__((used, noinline))
#endif

/* Leaf K: allocator wrap/fail/bounds remainder (32 B). */
OPEN_CFW_BL006_AX_ATTR
open_cfw_bl006_ax_u32 open_cfw_bootloader_cmdq_alloc_rem_tail_42799e(
    open_cfw_bl006_ax_u32 frame_w1,
    open_cfw_bl006_ax_u32 frame_base,
    open_cfw_bl006_ax_u32 frame_limit,
    open_cfw_bl006_ax_u32 index,
    open_cfw_bl006_ax_u32 *slot,
    unsigned entry,
    open_cfw_bl006_ax_u32 *exit_kind)
{
#if defined(__arm__) || defined(__thumb__)
    /* Exits into the replaced head: 0x427970 (success path) and
     * 0x427984 (function epilogue). Offsets from each branch PC:
     * 0x4279A2: -54 (e5 e7); 0x4279A6: -38 (ed e7);
     * 0x4279B8: -76 (da e7); 0x4279BC: -60 (e2 e7). */
    __asm__ volatile(
        "str r1, [r0, #4]\n"
        "ldr r0, [r7, #4]\n"
        ".inst.n 0xE7E5\n"
        "movs r0, #5\n"
        ".inst.n 0xE7ED\n"
        "ldr r0, [r7, #0x10]\n"
        "adds r1, r6, #1\n"
        "adds.w r0, r0, r1, lsl #3\n"
        "ldr r1, [r7, #0xc]\n"
        "cmp r0, r1\n"
        "bhs 0f\n"
        "ldr r0, [r7, #0x10]\n"
        ".inst.n 0xE7DA\n"
        "0: movs r0, #5\n"
        ".inst.n 0xE7E2\n");
#else
    /* Host twin: the entry selector names the stock entry (0 =
     * K1, 1 = K2, 2 = K3); exit_kind reports which replaced-head
     * address the path rejoins (0 = 0x00427970 success path,
     * 1 = 0x00427984 epilogue). Frame words arrive explicitly
     * because r4-r7 are head-owned. */
    switch (entry) {
    case 0U:
        slot[1] = frame_w1;
        *exit_kind = 0U;
        return frame_w1;
    case 1U:
        *exit_kind = 1U;
        return 5U;
    default:
        break;
    }
    {
        open_cfw_bl006_ax_u32 end =
            frame_base + ((index + 1U) << 3U);
        if (end >= frame_limit) {
            *exit_kind = 1U;
            return 5U;
        }
        *exit_kind = 0U;
        return frame_base;
    }
#endif
}

/* Leaf L: error-resume loop-back plus match epilogue (26 B). */
OPEN_CFW_BL006_AX_ATTR
open_cfw_bl006_ax_u32 open_cfw_bootloader_cmdq_errresume_rem_tail_427b90(
    open_cfw_bl006_ax_u32 *entry,
    open_cfw_bl006_ax_u32 qaddr_value,
    open_cfw_bl006_ax_u32 **qaddr_slot,
    open_cfw_bl006_ax_u32 *prefix)
{
#if defined(__arm__) || defined(__thumb__)
    /* L1 exit back into the replaced head scan: 0x427B76 sits 30
     * bytes below the branch PC (f1 e7). */
    __asm__ volatile(
        ".inst.n 0xE7F1\n"
        "ldr r2, [r1, #0x24]\n"
        "ldr r2, [r2, #8]\n"
        "str r2, [r0]\n"
        "ldr r2, [r1, #0x24]\n"
        "ldr r2, [r2, #4]\n"
        "str r0, [r2]\n"
        "ldr r0, [r1]\n"
        "bics r0, r0, #0x2000000\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    /* Host twin models the returning L2 entry: the L1 loop-back
     * branch does not return, so it has no host path (same
     * standing as the head-owned frame registers, which the
     * twin takes explicitly). */
    *entry = qaddr_value;
    *qaddr_slot = entry;
    *prefix &= (open_cfw_bl006_ax_u32)~0x2000000U;
    return 0U;
#endif
}

/* Assembler probes: each emits one narrow branch at the identical
 * byte offset as a stock out-of-span exit, proving the reviewed
 * `.inst.n` spelling above. Probe sections are discarded from the
 * firmware image; the verifier extracts them. */
#if defined(__arm__) || defined(__thumb__)
OPEN_CFW_BL006_AX_ATTR
void open_cfw_bl006_ax_probe_b_54_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 50\n"
        "b 0b\n");
}

OPEN_CFW_BL006_AX_ATTR
void open_cfw_bl006_ax_probe_b_38_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 34\n"
        "b 0b\n");
}

OPEN_CFW_BL006_AX_ATTR
void open_cfw_bl006_ax_probe_bhs_2_fwd(void)
{
    __asm__ volatile(
        "bhs 0f\n"
        "nop\n"
        "nop\n"
        "0:\n");
}

OPEN_CFW_BL006_AX_ATTR
void open_cfw_bl006_ax_probe_b_76_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 72\n"
        "b 0b\n");
}

OPEN_CFW_BL006_AX_ATTR
void open_cfw_bl006_ax_probe_b_60_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 56\n"
        "b 0b\n");
}

OPEN_CFW_BL006_AX_ATTR
void open_cfw_bl006_ax_probe_b_30_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 26\n"
        "b 0b\n");
}
#endif
