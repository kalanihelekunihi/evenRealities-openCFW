/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two dead bootloader terminal-return
 * tails, each a single 2-byte exit with no literal load:
 *
 *  A. memset-wrapper terminal return at 0x00426C22..0x00426C24
 *     (`pop {r4, pc}`): restores the head-owned r4 slot and
 *     returns to the head-owned link slot. The replaced memset
 *     wrapper head returns/jumps away in the built image, so this
 *     span never executes there.
 *
 *  B. CLKGEN HFADJ-enable terminal return at 0x00426C70..0x00426C72
 *     (`bx lr`): bare return with r0 passing through from the
 *     replaced head.
 *
 * Both spans sit in regions the whole-image retained survey grades
 * `no_control_flow_reference_found` (zero inbound references, not
 * the stronger corroborated-unreachable verdict: the heads that
 * fall through to them were already replaced, leaving no
 * reference at all). A whole-image `bl` sweep finds no caller of
 * either entry. The reconstructions document the bytes from
 * reviewed source and pin the behavior the replaced heads must
 * cover; no live traffic is claimed. See
 * docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_tr_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_TR_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_TR_ATTR __attribute__((used, noinline))
#endif

/* Tail A: memset-wrapper terminal return. */
OPEN_CFW_BL006_TR_ATTR
void open_cfw_bootloader_memset_term_tail_426c22(
    open_cfw_bl006_tr_u32 *sp,
    open_cfw_bl006_tr_u32 *r4_out,
    open_cfw_bl006_tr_u32 *ret_out)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "pop {r4, pc}\n");
#else
    /* Host twin: the stock tail pops the head-owned r4 slot and
     * the return slot from the incoming stack. */
    *r4_out = sp[0];
    *ret_out = sp[1];
    (void)sp;
#endif
}

/* Tail B: CLKGEN HFADJ-enable terminal return. */
OPEN_CFW_BL006_TR_ATTR
open_cfw_bl006_tr_u32 open_cfw_bootloader_clkgen_hfadj_term_426c70(
    open_cfw_bl006_tr_u32 value)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "bx lr\n");
#else
    /* Host twin: bare return, r0 passes through. */
    return value;
#endif
}
