/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two dead G2 bootloader epilogue tails:
 *
 *  C. MSPI enable epilogue at 0x004250E6..0x004250F0 (10 B), the
 *     surviving end of the replaced MSPI enable body ("unreachable
 *     stock tail after the source-owned MSPI enable return").
 *     Registers on entry (set by the replaced head): r0 = device
 *     control word, r4 = device-word pointer. The tail publishes
 *     bit 25 and returns success:
 *       r0 |= 0x2000000
 *       *reg = r0
 *       return 0
 *
 *  D. command-queue reset epilogue at 0x00427C72..0x00427C80
 *     (14 B), the surviving end of the replaced command-queue
 *     reset service. Registers on entry: r0 = status value,
 *     r2 = queue-state pointer. The tail narrows the value and
 *     publishes it through the register table:
 *       v = r0 & 0xFF
 *       t = *(r2 + 0x24); t = *(t + 0x0C); *t = v
 *       return 0
 *
 * Both tails are single-exit, call-free, and literal-free. The
 * whole-image survey grades both spans corroborated_unreachable_
 * control_flow and a whole-image `bl` sweep finds no caller of
 * either entry, so neither tail executes in the shipped image;
 * the reconstructions document the bytes and pin the behavior the
 * replaced heads must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-424ab2-4250e6-427c72-source-closure.md.
 */

typedef __UINT8_TYPE__ open_cfw_bl006_epi_u8;
typedef __UINT32_TYPE__ open_cfw_bl006_epi_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_EPI_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_EPI_ATTR __attribute__((used, noinline))
#endif

/* Tail C: MSPI enable epilogue. */
OPEN_CFW_BL006_EPI_ATTR
open_cfw_bl006_epi_u32 open_cfw_bootloader_mspi_enable_tail_4250e6(
    open_cfw_bl006_epi_u32 value,
    open_cfw_bl006_epi_u32 *reg)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "orrs r0, r0, #0x2000000\n"
        "str r0, [r4]\n"
        "movs r0, #0\n"
        "pop {r4, pc}\n");
#else
    /* The stock tail stores through the head-owned r4 slot, which
     * is not an incoming argument; the host twin takes the slot
     * explicitly so the merge-and-publish behavior is testable. */
    *reg = value | 0x2000000U;
    return 0U;
#endif
}

/* Tail D: command-queue reset epilogue. */
OPEN_CFW_BL006_EPI_ATTR
open_cfw_bl006_epi_u32 open_cfw_bootloader_cmdq_reset_tail_427c72(
    open_cfw_bl006_epi_u32 value,
    open_cfw_bl006_epi_u8 *ctx)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "and r0, r0, #0xff\n"
        "ldr r1, [r2, #0x24]\n"
        "ldr r1, [r1, #0xc]\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    open_cfw_bl006_epi_u32 v = value & 0xFFU;
    open_cfw_bl006_epi_u8 *t =
        *(open_cfw_bl006_epi_u8 **)(ctx + 0x24U);
    t = *(open_cfw_bl006_epi_u8 **)(t + 0x0CU);
    *(open_cfw_bl006_epi_u32 *)t = v;
    return 0U;
#endif
}
