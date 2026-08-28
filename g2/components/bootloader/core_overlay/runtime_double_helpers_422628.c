/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader IAR double-runtime leaves. */

typedef __UINT32_TYPE__ open_cfw_double_u32;
typedef __INT32_TYPE__ open_cfw_double_i32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_DOUBLE_ATTR __attribute__((used, naked, noinline))
extern void open_cfw_bootloader_double_frexp_core_alias_422634(void);
extern void open_cfw_bootloader_double_ldexp_core_alias_422714(void);
extern void open_cfw_bootloader_double_range_error_4275d2(void);

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_frexp_422628(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "mov r4, r2\n"
        "bl open_cfw_bootloader_double_frexp_core_alias_422634\n"
        "str r2, [r4]\n"
        "pop {r4, pc}\n");
}

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_frexp_core_422634(void)
{
    __asm__ volatile(
        "ubfx r3, r1, #20, #11\n"
        "cbz r3, 1f\n"
        "lsls r2, r1, #1\n"
        "cmn.w r2, #0x200000\n"
        "bhs 4f\n"
        "subw r2, r3, #0x3fe\n"
        "sub.w r1, r1, r2, lsl #20\n"
        "bx lr\n"
        "1:\n"
        "orrs.w r12, r0, r1, lsl #1\n"
        "beq 4f\n"
        "and r12, r1, #0x80000000\n"
        "bics.w r1, r1, r12\n"
        "clz r2, r1\n"
        "itt eq\n"
        "clzeq r3, r0\n"
        "addeq r2, r2, r3\n"
        "subs r2, #11\n"
        "subs.w r3, r2, #32\n"
        "ite hs\n"
        "lslhs.w r1, r0, r3\n"
        "lsllo r1, r2\n"
        "orr.w r1, r1, r12\n"
        "ittt lo\n"
        "rsblo.w r12, r2, #32\n"
        "lsrlo.w r3, r0, r12\n"
        "orrlo r1, r3\n"
        "lsls r0, r2\n"
        "rsbs r2, r2, #0\n"
        "movw r3, #0x3fd\n"
        "subs r2, r2, r3\n"
        "add.w r1, r1, r3, lsl #20\n"
        "bx lr\n"
        "4:\n"
        "movs r2, #0\n"
        "bx lr\n");
}

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_compare_422698(void)
{
    __asm__ volatile(
        "orr.w r12, r1, r3\n"
        "orrs.w r12, r0, r12, lsl #1\n"
        "orrs.w r12, r2, r12\n"
        "mov.w r12, #0x200000\n"
        "blo 1f\n"
        "beq 2f\n"
        "cmn.w r12, r1, lsl #1\n"
        "itt ls\n"
        "cmnls.w r12, r3, lsl #1\n"
        "cmpls r3, r1\n"
        "it eq\n"
        "cmpeq r2, r0\n"
        "2:\n"
        "bx lr\n"
        "1:\n"
        "cmn.w r12, r3, lsl #1\n"
        "bhi 2b\n"
        "cmp r1, r3\n"
        "it eq\n"
        "cmpeq r0, r2\n"
        "bx lr\n");
}

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_compare_reverse_4226cc(void)
{
    __asm__ volatile(
        "orr.w r12, r1, r3\n"
        "orrs.w r12, r0, r12, lsl #1\n"
        "orrs.w r12, r2, r12\n"
        "mov.w r12, #0x200000\n"
        "blo 1f\n"
        "beq 2f\n"
        "cmn.w r12, r1, lsl #1\n"
        "itt ls\n"
        "cmnls.w r12, r3, lsl #1\n"
        "cmpls r1, r3\n"
        "it eq\n"
        "cmpeq r0, r2\n"
        "2:\n"
        "bx lr\n"
        "1:\n"
        "cmn.w r12, r1, lsl #1\n"
        "bhi 2b\n"
        "cmp r3, r1\n"
        "it eq\n"
        "cmpeq r2, r0\n"
        "bx lr\n");
}

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_ldexp_422700(void)
{
    __asm__ volatile(
        "push {lr}\n"
        "vmov d0, r0, r1\n"
        "mov r0, r2\n"
        "bl open_cfw_bootloader_double_ldexp_core_alias_422714\n"
        "vmov r0, r1, d0\n"
        "pop {pc}\n");
}

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_ldexp_core_422714(void)
{
    __asm__ volatile(
        "movs r2, r0\n"
        "vmov.32 r1, d0[1]\n"
        "movw r12, #0x7ff\n"
        "bmi 5f\n"
        "ands.w r3, r12, r1, lsr #20\n"
        "beq 3f\n"
        "cmp r3, r12\n"
        "beq 11f\n"
        "adds r3, r3, r2\n"
        "1:\n"
        "cmp r3, r12\n"
        "bhs 2f\n"
        "add.w r1, r1, r2, lsl #20\n"
        "vmov.32 d0[1], r1\n"
        "bx lr\n"
        "2:\n"
        "and r1, r1, #0x80000000\n"
        "orr.w r1, r1, r12, lsl #20\n"
        "movs r0, #0\n"
        "vmov d0, r0, r1\n"
        "10:\n"
        "b.w open_cfw_bootloader_double_range_error_4275d2\n"
        "bx lr\n"
        "3:\n"
        "vmov.32 r0, d0[0]\n"
        "orrs.w r0, r0, r1, lsl #1\n"
        "beq 11f\n"
        "cmp.w r2, #0x3fc\n"
        "bhs 4f\n"
        "add.w r1, r2, r12, lsr #1\n"
        "lsls r1, r1, #20\n"
        "movs r0, #0\n"
        "vmov d1, r0, r1\n"
        "vmul.f64 d0, d0, d1\n"
        "bx lr\n"
        "4:\n"
        "mov.w r1, #0x7f000000\n"
        "movs r3, #0\n"
        "vmov d1, r3, r1\n"
        "vmul.f64 d0, d0, d1\n"
        "subs.w r2, r2, #0x3f8\n"
        "vmov.32 r1, d0[1]\n"
        "lsl.w r3, r1, #1\n"
        "adc.w r3, r2, r3, lsr #21\n"
        "b 1b\n"
        "5:\n"
        "rsbs r2, r2, #0\n"
        "ands.w r3, r12, r1, lsr #20\n"
        "beq 8f\n"
        "cmp r3, r12\n"
        "beq 11f\n"
        "cmp r2, r3\n"
        "bhs 6f\n"
        "sub.w r1, r1, r2, lsl #20\n"
        "vmov.32 d0[1], r1\n"
        "bx lr\n"
        "6:\n"
        "subs r3, r3, #1\n"
        "subs r2, r2, r3\n"
        "sub.w r1, r1, r3, lsl #20\n"
        "vmov.32 d0[1], r1\n"
        "cmp r2, #55\n"
        "blo 9f\n"
        "7:\n"
        "movs r0, #0\n"
        "and r1, r1, #0x80000000\n"
        "vmov d0, r0, r1\n"
        "b 10b\n"
        "8:\n"
        "vmov.32 r0, d0[0]\n"
        "orrs.w r0, r0, r1, lsl #1\n"
        "beq 11f\n"
        "cmp r2, #55\n"
        "bhs 7b\n"
        "9:\n"
        "rsb r2, r2, r12, lsr #1\n"
        "lsls r1, r2, #20\n"
        "movs r0, #0\n"
        "vmov d1, r0, r1\n"
        "vmrs r0, fpscr\n"
        "bic r1, r0, #0x1f\n"
        "bic r1, r1, #0x1f00\n"
        "vmsr fpscr, r1\n"
        "vmul.f64 d0, d0, d1\n"
        "vmrs r1, fpscr\n"
        "vmsr fpscr, r0\n"
        "tst.w r1, #8\n"
        "bne 10b\n"
        "11:\n"
        "bx lr\n"
        );
}

OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_to_i32_422804(void)
{
    __asm__ volatile("vmov d0, r0, r1\nvcvt.s32.f64 s0, d0\nvmov r0, s0\nbx lr\n");
}
OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_i32_to_double_422812(void)
{
    __asm__ volatile("vmov s0, r0\nvcvt.f64.s32 d0, s0\nvmov r0, r1, d0\nbx lr\n");
}
OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_subtract_422820(void)
{
    __asm__ volatile("vmov d0, r0, r1\nvmov d1, r2, r3\nvsub.f64 d0, d0, d1\nvmov r0, r1, d0\nbx lr\n");
}
OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_divide_422832(void)
{
    __asm__ volatile("vmov d0, r0, r1\nvmov d1, r2, r3\nvdiv.f64 d0, d0, d1\nvmov r0, r1, d0\nbx lr\n");
}
OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_to_u32_422844(void)
{
    __asm__ volatile("vmov d0, r0, r1\nvcvt.u32.f64 s0, d0\nvmov r0, s0\nbx lr\n");
}
OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_u32_to_double_422852(void)
{
    __asm__ volatile("vmov s0, r0\nvcvt.f64.u32 d0, s0\nvmov r0, r1, d0\nbx lr\n");
}
OPEN_CFW_DOUBLE_ATTR void open_cfw_bootloader_double_multiply_422860(void)
{
    __asm__ volatile("vmov d0, r0, r1\nvmov d1, r2, r3\nvmul.f64 d0, d0, d1\nvmov r0, r1, d0\nbx lr\n");
}

#else

typedef union { double d; unsigned long long u; } open_cfw_double_bits;

double open_cfw_bootloader_double_frexp_422628(double value, open_cfw_double_i32 *exponent)
{
    open_cfw_double_bits bits = { value };
    open_cfw_double_u32 exp = (open_cfw_double_u32)((bits.u >> 52) & 0x7ffU);
    if (exp == 0x7ffU || (bits.u << 1) == 0U) { *exponent = 0; return value; }
    if (exp == 0U) {
        value *= 0x1p54;
        bits.d = value;
        exp = (open_cfw_double_u32)((bits.u >> 52) & 0x7ffU);
        *exponent = (open_cfw_double_i32)exp - 1022 - 54;
    } else *exponent = (open_cfw_double_i32)exp - 1022;
    bits.u = (bits.u & 0x800fffffffffffffULL) | (0x3feULL << 52);
    return bits.d;
}

int open_cfw_bootloader_double_compare_422698(double left, double right) { return left < right; }
int open_cfw_bootloader_double_compare_reverse_4226cc(double left, double right) { return left > right; }

double open_cfw_bootloader_double_ldexp_422700(double value, open_cfw_double_i32 exponent)
{
    while (exponent > 0) { value *= 2.0; --exponent; }
    while (exponent < 0) { value *= 0.5; ++exponent; }
    return value;
}
open_cfw_double_i32 open_cfw_bootloader_double_to_i32_422804(double value) { return (open_cfw_double_i32)value; }
double open_cfw_bootloader_i32_to_double_422812(open_cfw_double_i32 value) { return (double)value; }
double open_cfw_bootloader_double_subtract_422820(double a, double b) { return a - b; }
double open_cfw_bootloader_double_divide_422832(double a, double b) { return a / b; }
open_cfw_double_u32 open_cfw_bootloader_double_to_u32_422844(double value) { return (open_cfw_double_u32)value; }
double open_cfw_bootloader_u32_to_double_422852(open_cfw_double_u32 value) { return (double)value; }
double open_cfw_bootloader_double_multiply_422860(double a, double b) { return a * b; }

#endif
