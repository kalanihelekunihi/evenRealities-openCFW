/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of four dead G2 bootloader tails in the
 * BL-006 range, each surviving only as unreachable stock bytes after
 * a replaced head:
 *
 *  L. MSPI interrupt-status remainder at 0x004264F6..0x00426506
 *     (16 B). Registers on entry (set by the replaced head):
 *     r0 = instance index, r1 = out-slot pointer, r2 = register
 *     base; r4 is head-owned scratch restored by the epilogue.
 *     The tail publishes one status word and returns 0:
 *       r0 = [base + (index << 12) + 0x204]
 *       *out = r0
 *       return 0
 *     The leading `adds.w` also writes APSR flags from the scaled
 *     base; flags are not part of any return contract, so the host
 *     twin does not model them (same standing as the sibling
 *     interrupt-disable tail's flag-setting `adds`).
 *
 *  M. CLKGEN dual-clock-switch terminal tail at
 *     0x00426CC4..0x00426CCC (8 B). Registers on entry: r1 = value
 *     to publish, r4 = head-owned slot. The tail:
 *       [(slot << 4)] = value
 *       return 0
 *     via `pop {r1, pc}`. The host twin takes the slot explicitly
 *     plus a host region modelling the target address window, so
 *     the (slot << 4) byte-offset shape is testable (same pattern
 *     as the command-queue termination tail's head-owned slot).
 *
 *  N. command-queue initializer remainder at
 *     0x0042784C..0x00427878 (44 B). Registers on entry: r0 = input
 *     word pointer, r1 = configuration struct, r2 = out-slot
 *     pointer, r4 = head-owned queue state; r5 is scratch restored
 *     by the epilogue. With S = *(state + 0x24) the tail:
 *       acc = *in | *(S + 0x14)          (word value OR-ed in)
 *       **(S + 0x10) = acc               (word publish)
 *       **(S + 4) = cfg->u32[1]          (word publish)
 *       **S = (cfg->u8[8] << 1) & 2      (masked bit publish)
 *       *out = state
 *       return 0
 *     The host twin keeps the state -> link thread but represents
 *     the target link word as a native struct: the target's
 *     4-byte pointer slots at +0x00/+0x04 would overlap as 8-byte
 *     host pointers, so {value@0x14, ptr@0x10, ptr@0x04, ptr@0x00}
 *     becomes named native fields (documented divergence; the
 *     naked target body is the unmodified stock choreography).
 *
 *  O. command-queue block-release terminal return at
 *     0x004279EE..0x004279F0 (2 B): a bare `bx lr`. The replaced
 *     head leaves the status in r0; the tail passes it through.
 *     The host twin is the identity function, documenting the
 *     pass-through.
 *
 * All four spans are single-exit, call-free, branch-free, and
 * literal-free (the stock-internal branches that target into
 * them originate in the replaced head spans, which the
 * whole-image survey accounts for). The survey grades every span
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of any entry, so no tail executes in the
 * shipped image; the reconstructions document the bytes and pin
 * the behavior the replaced heads must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-4264f6-4279ee-source-closure.md.
 *
 * Deliberately excluded: the 10-byte retained slice at
 * 0x004264B0..0x004264BA starts mid-instruction (the authentic
 * stock stream has a 32-bit ADD.W at 0x004264AE spanning
 * 0x004264AE..0x004264B2), so it cannot be framed as a behavior
 * leaf entry; it needs the data/fill route as a follow-up.
 */

typedef __UINT8_TYPE__ open_cfw_bl006_t2_u8;
typedef __UINT32_TYPE__ open_cfw_bl006_t2_u32;

/* Host-only model of tail N's target link word (never emitted for
 * the target; the naked body above is the stock choreography). */
struct open_cfw_bl006_t2_link {
    open_cfw_bl006_t2_u32 v14;
    open_cfw_bl006_t2_u32 *p10;
    open_cfw_bl006_t2_u32 *p04;
    open_cfw_bl006_t2_u32 *p00;
};
typedef struct open_cfw_bl006_t2_link open_cfw_bl006_t2_link_t;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_T2_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_T2_ATTR __attribute__((used, noinline))
#endif

/* Tail L: MSPI interrupt-status remainder. */
OPEN_CFW_BL006_T2_ATTR
open_cfw_bl006_t2_u32 open_cfw_bootloader_mspi_irq_status_tail_4264f6(
    open_cfw_bl006_t2_u32 index,
    open_cfw_bl006_t2_u32 *out,
    open_cfw_bl006_t2_u8 *base)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "adds.w r2, r2, r0, lsl #12\n"
        "ldr.w r0, [r2, #0x204]\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "pop {r4}\n"
        "bx lr\n");
#else
    *(open_cfw_bl006_t2_u32 *)(void *)out =
        *(const open_cfw_bl006_t2_u32 *)(const void *)(base +
            (open_cfw_bl006_t2_u32)(index << 12U) + 0x204U);
    return 0U;
#endif
}

/* Tail M: CLKGEN dual-clock-switch terminal tail. */
OPEN_CFW_BL006_T2_ATTR
open_cfw_bl006_t2_u32 open_cfw_bootloader_clkgen_dualclock_term_tail_426cc4(
    open_cfw_bl006_t2_u32 value,
    open_cfw_bl006_t2_u32 slot,
    open_cfw_bl006_t2_u8 *region)
{
#if defined(__arm__) || defined(__thumb__)
    /* The stock tail derives the publish address from the
     * head-owned r4 register, which is not an incoming argument;
     * the host twin takes the slot explicitly (same pattern as
     * the command-queue termination tail). */
    __asm__ volatile(
        "lsls r0, r4, #4\n"
        "str r1, [r0]\n"
        "movs r0, #0\n"
        "pop {r1, pc}\n");
#else
    *(open_cfw_bl006_t2_u32 *)(void *)(region + slot * 16U) = value;
    return 0U;
#endif
}

/* Tail N: command-queue initializer remainder. */
OPEN_CFW_BL006_T2_ATTR
open_cfw_bl006_t2_u32 open_cfw_bootloader_cmdq_init_rem_tail_42784c(
    const open_cfw_bl006_t2_u32 *in,
    const open_cfw_bl006_t2_u8 *cfg,
    open_cfw_bl006_t2_u8 **out,
    open_cfw_bl006_t2_u8 *state)
{
#if defined(__arm__) || defined(__thumb__)
    /* The stock tail threads the queue state through the
     * head-owned r4 register; the host twin takes it explicitly. */
    __asm__ volatile(
        "ldr r3, [r0]\n"
        "ldr r0, [r4, #0x24]\n"
        "ldr r0, [r0, #0x14]\n"
        "orrs r3, r0\n"
        "ldr r0, [r4, #0x24]\n"
        "ldr r0, [r0, #0x10]\n"
        "str r3, [r0]\n"
        "ldr r0, [r1, #4]\n"
        "ldr r3, [r4, #0x24]\n"
        "ldr r3, [r3, #4]\n"
        "str r0, [r3]\n"
        "ldrb r0, [r1, #8]\n"
        "lsls r0, r0, #1\n"
        "ands r0, r0, #2\n"
        "ldr r1, [r4, #0x24]\n"
        "ldr r1, [r1]\n"
        "str r0, [r1]\n"
        "str r4, [r2]\n"
        "movs r0, #0\n"
        "pop {r4, r5}\n"
        "bx lr\n");
#else
    /* Host model of the target link word; see the header comment.
     * The state -> link thread is preserved exactly. */
    open_cfw_bl006_t2_link_t *link =
        *(open_cfw_bl006_t2_link_t **)(const void *)(state + 0x24U);
    open_cfw_bl006_t2_u32 acc = *in | link->v14;
    *link->p10 = acc;
    *link->p04 = *(const open_cfw_bl006_t2_u32 *)(const void *)(cfg + 4U);
    *link->p00 =
        (open_cfw_bl006_t2_u32)(((open_cfw_bl006_t2_u32)cfg[8U] << 1U) & 2U);
    *out = state;
    return 0U;
#endif
}

/* Tail O: command-queue block-release terminal return. */
OPEN_CFW_BL006_T2_ATTR
open_cfw_bl006_t2_u32 open_cfw_bootloader_cmdq_blockrel_term_4279ee(
    open_cfw_bl006_t2_u32 passthrough)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile("bx lr\n");
#else
    return passthrough;
#endif
}
