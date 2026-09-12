/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the dead MSPI disable mini-tail at
 * 0x00425162..0x00425166 (4 B), the surviving executable end of
 * the replaced MSPI disable head ("unreachable disable tail"
 * in the survey). Registers on entry (set by the replaced head):
 * none live; the tail zeroes the return and restores the
 * head-owned register block:
 *   r0 = 0; restore r1, r4, r5; return via pop {r1, r4, r5, pc}
 *
 * The span sits in the region the whole-image retained survey
 * grades corroborated_unreachable_control_flow (five inbound
 * references, all from the replaced disable head span). A
 * whole-image `bl` sweep finds no caller of this entry. The
 * reconstruction documents the bytes from reviewed source and
 * pins the behavior the replaced head must cover; no live traffic
 * is claimed. The orphaned branch-fragment halfword before it
 * (0x00425160), the alignment halfword after it (0x00425166),
 * and the lifecycle literal word (0x00425168) are reproduced as
 * named in-place data in
 * runtime_bl006_tail_fragments_425160.c. See
 * docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_dt_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_DT_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_DT_ATTR __attribute__((used, noinline))
#endif

/* Disable mini-tail: zero the return, restore the head-owned
 * block, return. */
OPEN_CFW_BL006_DT_ATTR
void open_cfw_bootloader_mspi_disable_tail_425162(
    open_cfw_bl006_dt_u32 *sp,
    open_cfw_bl006_dt_u32 *out)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "movs r0, #0\n"
        "pop {r1, r4, r5, pc}\n");
#else
    /* Host twin: the stock tail pops the head-owned r1/r4/r5
     * slots and the return slot from the incoming stack and
     * forces r0 to zero. out[0] = r0, out[1] = r1, out[2] = r4,
     * out[3] = r5, out[4] = return slot. */
    out[0] = 0U;
    out[1] = sp[0];
    out[2] = sp[1];
    out[3] = sp[2];
    out[4] = sp[3];
#endif
}
