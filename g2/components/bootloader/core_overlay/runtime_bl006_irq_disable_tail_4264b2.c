/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the dead MSPI interrupt-disable
 * publish tail at 0x004264B2..0x004264BA (8 B), the surviving
 * executable end of the replaced MSPI interrupt-disable head
 * ("unreachable stock tail after the source-owned MSPI
 * interrupt-disable return"). Registers on entry (set by the
 * replaced head): r1 = status word to publish, r2 = scaled
 * register base (the head's orphaned `adds.w r2, r2, r0,
 * lsl #12` at 0x004264AE built it; its second halfword survives
 * as the named fragment in
 * runtime_bl006_tail_fragments_425160.c). The tail publishes the
 * word, zeroes the return, and returns:
 *   *(r2 + 0x200) = r1; r0 = 0; return via bx lr
 *
 * The span sits in the region the whole-image retained survey
 * grades corroborated_unreachable_control_flow (one inbound
 * reference, from the replaced disable head span). A
 * whole-image `bl` sweep finds no caller of this entry. The
 * reconstruction documents the bytes from reviewed source and
 * pins the behavior the replaced head must cover; no live traffic
 * is claimed. See
 * docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_id_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_ID_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_ID_ATTR __attribute__((used, noinline))
#endif

/* Interrupt-disable publish tail. */
OPEN_CFW_BL006_ID_ATTR
open_cfw_bl006_id_u32 open_cfw_bootloader_mspi_irq_disable_tail_4264b2(
    open_cfw_bl006_id_u32 value,
    void *base)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "str.w r1, [r2, #0x200]\n"
        "movs r0, #0\n"
        "bx lr\n");
#else
    /* Host twin: the stock tail stores the incoming r1 word
     * through the head-owned scaled base slot (taken explicitly
     * here) at word offset 0x200 and returns zero. */
    *(open_cfw_bl006_id_u32 *)((unsigned char *)base + 0x200U) = value;
    return 0U;
#endif
}
