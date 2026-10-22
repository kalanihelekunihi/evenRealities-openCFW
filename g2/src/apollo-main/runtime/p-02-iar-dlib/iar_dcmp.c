/* IAR runtime double comparisons, firmware 2.2.6.10:
 *   0x43c0b0..0x43c0e4  reversed compare returning only APSR flags (__aeabi_cdrcmple shape)
 *   0x43baf4..0x43bb00  __aeabi_dcmpgt-style boolean wrapper around it
 *
 * The comparator returns its result in the condition flags, so it cannot be
 * written in C. The bodies are naked functions that use the stock instructions in
 * the same order. Arguments are soft-float register pairs: a = r0:r1, b = r2:r3.
 *
 * Flag contract (from the instructions): the flags describe "b compared with a".
 * C is clear exactly when b < a (ordered). Z is set when a == b, including
 * +0 == -0. An operand whose |high word| exceeds 0x7ff00000 (a NaN with a nonzero
 * upper mantissa) gives C=1, Z=0. A NaN whose upper mantissa is zero passes the
 * screen and is compared by its words like any other value. When both operands
 * are non-negative, the unsigned (hi, lo) words of b are compared against a. If
 * either is negative, the words of a are compared against b, which reverses the
 * order for sign-magnitude values.
 * The screen adds 0x00200000 to (hi << 1). In the non-negative path only a's
 * high word is screened, because a NaN b already compares above any finite a.
 *
 * The callers are printf_core (0x481e88, direct) and the closed nrf_fuel_gauge
 * library (via 0x43baf4). Suffixed names are used because generic compiler-rt
 * __aeabi_dcmp* bodies already exist in ui/lvgl/display-lv/display_lv_init_children.c. */
#include <stdint.h>

__attribute__((naked, noinline)) void iar_aeabi_cdrcmple_43c0b0(void)
{
    __asm__ volatile(
        "orr.w ip, r1, r3\n\t"
        "orrs.w ip, r0, ip, lsl #1\n\t"   /* C = sign(a)|sign(b) */
        "orrs.w ip, r2, ip\n\t"           /* Z = both are +-0 */
        "mov.w ip, #0x200000\n\t"
        "bcc 1f\n\t"
        "beq 0f\n\t"
        "cmn.w ip, r1, lsl #1\n\t"        /* a NaN screen */
        "itt ls\n\t"
        "cmnls.w ip, r3, lsl #1\n\t"      /* b NaN screen */
        "cmpls r1, r3\n\t"
        "it eq\n\t"
        "cmpeq r0, r2\n"
        "0:\n\t"
        "bx lr\n"
        "1:\n\t"
        "cmn.w ip, r1, lsl #1\n\t"
        "bhi 0b\n\t"
        "cmp r3, r1\n\t"
        "it eq\n\t"
        "cmpeq r2, r0\n\t"
        "bx lr\n");
}

/* Returns 1 when a > b, otherwise 0 (also 0 for NaN): r0 = !C. */
__attribute__((naked, noinline, pcs("aapcs")))
int32_t iar_aeabi_dcmpgt_43baf4(double a __attribute__((unused)),
                                double b __attribute__((unused)))
{
    __asm__ volatile(
        "push {lr}\n\t"
        "bl iar_aeabi_cdrcmple_43c0b0\n\t"
        "sbcs r0, r0, r0\n\t"
        "negs r0, r0\n\t"
        "pop {pc}\n");
}
