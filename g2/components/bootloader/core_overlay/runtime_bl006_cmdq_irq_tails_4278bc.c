/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of six dead G2 bootloader tails:
 *
 *  E. command-queue enable remainder at 0x004278BC..0x004278C8
 *     (12 B), the surviving end of the replaced command-queue
 *     enable service. Registers on entry: r1 = enable-word
 *     pointer. The tail merges bit 25 and returns success:
 *       r0 = *r1
 *       r0 |= 0x2000000
 *       *r1 = r0
 *       return 0
 *
 *  F. command-queue disable remainder at 0x004278FC..0x0042790A
 *     (14 B), the surviving end of the replaced command-queue
 *     disable service. Registers on entry: r0 = status value,
 *     r1 = enable-word pointer, r2 = destination slot. The tail
 *     publishes the value, then clears bit 25 and returns
 *     success:
 *       *r2 = r0
 *       r0 = *r1
 *       r0 &= ~0x2000000
 *       *r1 = r0
 *       return 0
 *
 *  G. command-queue block-post remainder at 0x00427A4C..0x00427A56
 *     (10 B), the surviving end of the replaced command-queue
 *     block-post service. Registers on entry: r0 = status value,
 *     r2 = queue-state pointer. The tail narrows the value
 *     through the register table and returns success:
 *       t = *(r2 + 0x24); t = *(t + 0x0C); *t = r0
 *       return 0
 *
 *  H. command-queue termination remainder at 0x00427B2E..0x00427B38
 *     (10 B), the surviving end of the replaced command-queue
 *     termination service. Registers on entry (set by the
 *     replaced head): r1 = value, r4 = head-owned state slot.
 *     The tail publishes the value through the state table and
 *     returns success:
 *       t = *(r4 + 0x24); t = *(t + 0x10); *t = r1
 *       return 0
 *
 *  I. command-queue reset remainder at 0x00427C02..0x00427C12
 *     (16 B), a second surviving end of the replaced
 *     command-queue reset service (tail D covers the
 *     narrow-and-publish end at 0x00427C72). Registers on
 *     entry: r0 = status value, r1 = enable-word pointer,
 *     r2 = queue-state pointer. The tail publishes the value,
 *     then clears bit 25 and returns success:
 *       t = *(r2 + 4); *t = r0
 *       r0 = *r1
 *       r0 &= ~0x2000000
 *       *r1 = r0
 *       return 0
 *
 *  J. MSPI interrupt-enable remainder at 0x0042647C..0x00426484
 *     (8 B), the surviving end of the replaced MSPI
 *     interrupt-enable service. Registers on entry: r1 = value,
 *     r2 = register base. The tail publishes the value and
 *     returns success:
 *       *(r2 + 0x200) = r1
 *       return 0
 *
 * All six tails are single-exit, call-free, branch-free, and
 * literal-free. The whole-image survey grades every span
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of any entry, so no tail executes in the
 * shipped image; the reconstructions document the bytes and pin
 * the behavior the replaced heads must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-42647c-427c02-source-closure.md.
 */

typedef __UINT8_TYPE__ open_cfw_bl006_cq_u8;
typedef __UINT32_TYPE__ open_cfw_bl006_cq_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_CQ_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_CQ_ATTR __attribute__((used, noinline))
#endif

/* Tail E: command-queue enable remainder (bit-25 merge). */
OPEN_CFW_BL006_CQ_ATTR
open_cfw_bl006_cq_u32 open_cfw_bootloader_cmdq_enable_tail_4278bc(
    open_cfw_bl006_cq_u32 *reg)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "ldr r0, [r1]\n"
        "orrs r0, r0, #0x2000000\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    *reg |= 0x2000000U;
    return 0U;
#endif
}

/* Tail F: command-queue disable remainder (publish, bit-25 clear). */
OPEN_CFW_BL006_CQ_ATTR
open_cfw_bl006_cq_u32 open_cfw_bootloader_cmdq_disable_tail_4278fc(
    open_cfw_bl006_cq_u32 value,
    open_cfw_bl006_cq_u32 *reg,
    open_cfw_bl006_cq_u32 *dst)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "str r0, [r2]\n"
        "ldr r0, [r1]\n"
        "bics r0, r0, #0x2000000\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    *dst = value;
    *reg &= (open_cfw_bl006_cq_u32)~0x2000000U;
    return 0U;
#endif
}

/* Tail G: command-queue block-post remainder (table publish). */
OPEN_CFW_BL006_CQ_ATTR
open_cfw_bl006_cq_u32 open_cfw_bootloader_cmdq_post_tail_427a4c(
    open_cfw_bl006_cq_u32 value,
    open_cfw_bl006_cq_u8 *ctx)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "ldr r1, [r2, #0x24]\n"
        "ldr r1, [r1, #0xc]\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    open_cfw_bl006_cq_u8 *t =
        *(open_cfw_bl006_cq_u8 **)(ctx + 0x24U);
    t = *(open_cfw_bl006_cq_u8 **)(t + 0x0CU);
    *(open_cfw_bl006_cq_u32 *)t = value;
    return 0U;
#endif
}

/* Tail H: command-queue termination remainder (state publish). */
OPEN_CFW_BL006_CQ_ATTR
open_cfw_bl006_cq_u32 open_cfw_bootloader_cmdq_term_tail_427b2e(
    open_cfw_bl006_cq_u32 value,
    open_cfw_bl006_cq_u8 *slot)
{
#if defined(__arm__) || defined(__thumb__)
    /* The stock tail reads the state slot through the head-owned
     * r4 register, which is not an incoming argument; the host
     * twin takes the slot explicitly so the publish behavior is
     * testable (same pattern as the MSPI enable epilogue). */
    __asm__ volatile(
        "ldr r0, [r4, #0x24]\n"
        "ldr r0, [r0, #0x10]\n"
        "str r1, [r0]\n"
        "movs r0, #0\n"
        "pop {r1, r4, r5, pc}\n");
#else
    open_cfw_bl006_cq_u8 *t =
        *(open_cfw_bl006_cq_u8 **)(slot + 0x24U);
    t = *(open_cfw_bl006_cq_u8 **)(t + 0x10U);
    *(open_cfw_bl006_cq_u32 *)t = value;
    return 0U;
#endif
}

/* Tail I: command-queue reset remainder (publish, bit-25 clear). */
OPEN_CFW_BL006_CQ_ATTR
open_cfw_bl006_cq_u32 open_cfw_bootloader_cmdq_reset_rem_tail_427c02(
    open_cfw_bl006_cq_u32 value,
    open_cfw_bl006_cq_u32 *reg,
    open_cfw_bl006_cq_u8 *ctx)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "ldr r2, [r2, #4]\n"
        "str r0, [r2]\n"
        "ldr r0, [r1]\n"
        "bics r0, r0, #0x2000000\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    open_cfw_bl006_cq_u8 *t =
        *(open_cfw_bl006_cq_u8 **)(ctx + 4U);
    *(open_cfw_bl006_cq_u32 *)t = value;
    *reg &= (open_cfw_bl006_cq_u32)~0x2000000U;
    return 0U;
#endif
}

/* Tail J: MSPI interrupt-enable remainder (register publish). */
OPEN_CFW_BL006_CQ_ATTR
open_cfw_bl006_cq_u32 open_cfw_bootloader_mspi_irq_enable_tail_42647c(
    open_cfw_bl006_cq_u32 value,
    open_cfw_bl006_cq_u8 *base)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "str.w r1, [r2, #0x200]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    *(open_cfw_bl006_cq_u32 *)(base + 0x200U) = value;
    return 0U;
#endif
}
