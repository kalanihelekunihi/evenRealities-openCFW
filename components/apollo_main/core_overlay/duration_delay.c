/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Exact source-assembled replacement for the G2 2.2.6.10 Apollo510
 * microsecond-delay primitive at 0x004807A0. This is a bounded adaptation of
 * AmbiqSuite SDK 5.1.0 am_hal_delay_us and br_util_delay_cycles. Exact stock
 * boundaries, callers, scatter-load evidence, and ITCM placement are recorded
 * in EVIDENCE.md.
 */

#ifdef OPEN_CFW_DURATION_DELAY_HOST

#ifndef OPEN_CFW_DURATION_DELAY_PERF_STATUS
#define OPEN_CFW_DURATION_DELAY_PERF_STATUS() \
    ((*(const volatile unsigned int *)(const void *)0x40021000U >> 3U) & 3U)
#endif

#ifndef OPEN_CFW_DURATION_DELAY_CYCLES
#define OPEN_CFW_DURATION_DELAY_CYCLES(iterations) \
    (((void (*)(unsigned int))0x00000041U)(iterations))
#endif

/*
 * Host-testable rendering of Ambiq's policy. Target builds use the exact
 * source assembly below so compiler scheduling cannot change its calibrated
 * overhead or floating-point conversion behavior.
 */
__attribute__((used, noinline))
void open_cfw_delay_cycles(unsigned int iterations)
{
    OPEN_CFW_DURATION_DELAY_CYCLES(iterations);
}

__attribute__((used, noinline))
void open_cfw_delay_us(unsigned int usec)
{
    unsigned int iterations = (unsigned int)(usec * (96.0f / 3.0f));
    unsigned int adjustment;

    if (OPEN_CFW_DURATION_DELAY_PERF_STATUS() == 2U) {
        iterations =
            (unsigned int)(iterations * 1.0f * 250.0f / 96.0f);
        adjustment = ((13U * 250U / 96U) + 40U) / 3U;
    } else {
        adjustment = ((13U * 1U) + 32U) / 3U;
    }

    if (iterations > adjustment) {
        open_cfw_delay_cycles(iterations - adjustment);
    }
}

__attribute__((used, noinline))
void open_cfw_delay_ms(unsigned int milliseconds)
{
    open_cfw_delay_us(milliseconds * 1000U);
}

__attribute__((used, noinline))
void open_cfw_delay_us_passthrough(unsigned int microseconds)
{
    open_cfw_delay_us(microseconds);
}

#else

/*
 * The startup scatter-load stream at 0x0079430E emits its first 14 bytes
 * literally to ITCM 0x00000040. The builder copies this six-byte function
 * over stream bytes 0x00794310...0x00794315, making the runtime loop itself
 * source-generated while leaving the neighboring compressed ITCM routines
 * unchanged.
 */
__attribute__((used, noinline, naked))
void open_cfw_delay_cycles(unsigned int iterations)
{
    __asm volatile(
        ".syntax unified\n"
        "1:\n"
        "subs r0, #1\n"
        "bne 1b\n"
        "bx lr\n"
    );
}

/*
 * This function is copied in place to 0x004807A0 by the overlay builder.
 * The explicit BL encoding at offset 0x4A therefore continues to target
 * 0x00000040, the source-generated three-cycle loop in Apollo510 ITCM.
 * Keeping the original placement also keeps both PC-relative literals and
 * the SDK's timing-overhead calibration exact.
 */
__attribute__((used, noinline, naked))
void open_cfw_delay_us(unsigned int usec)
{
    __asm volatile(
        ".syntax unified\n"
        ".fpu fpv5-sp-d16\n"
        "push {r7, lr}\n"
        "vmov s0, r0\n"
        "vcvt.f32.u32 s0, s0\n"
        "vcvt.u32.f32 s0, s0, #5\n"
        "vmov r0, s0\n"
        "ldr r1, 3f\n"
        "ldr r1, [r1]\n"
        "ubfx r1, r1, #3, #2\n"
        "cmp r1, #2\n"
        "beq 1f\n"
        "movs r1, #15\n"
        "b 2f\n"
        "1:\n"
        "vmov s0, r0\n"
        "vcvt.f32.u32 s0, s0\n"
        "vldr s1, 4f\n"
        "vmul.f32 s0, s0, s1\n"
        "vldr s1, 5f\n"
        "vdiv.f32 s0, s0, s1\n"
        "vcvt.u32.f32 s0, s0\n"
        "vmov r0, s0\n"
        "movs r1, #24\n"
        "2:\n"
        "cmp r1, r0\n"
        "bhs 6f\n"
        "subs r0, r0, r1\n"
        /*
         * BL 0x00000040 when installed at 0x004807EA. The source-copy patch
         * and exact-span hash prevent this placement-specific encoding from
         * being installed anywhere else.
         */
        ".short 0xf77f, 0xf429\n"
        "6:\n"
        "pop {r0, pc}\n"
        ".p2align 2\n"
        "4: .word 0x437a0000\n"
        "5: .word 0x42c00000\n"
        "3: .word 0x40021000\n"
    );
}

/*
 * Exact source copies of the adjacent application wrappers at 0x004910F4 and
 * 0x00491102. Their raw BL encodings are placement-specific, so these overlay
 * symbols exist only as builder inputs for exact in-place copy patches.
 */
__attribute__((used, noinline, naked))
void open_cfw_delay_ms(unsigned int milliseconds)
{
    __asm volatile(
        ".syntax unified\n"
        "push {r7, lr}\n"
        "mov.w r1, #1000\n"
        "muls r0, r1, r0\n"
        ".short 0xf7ef, 0xfb50\n"
        "pop {r0, pc}\n"
    );
}

__attribute__((used, noinline, naked))
void open_cfw_delay_us_passthrough(unsigned int microseconds)
{
    __asm volatile(
        ".syntax unified\n"
        "push {r7, lr}\n"
        ".short 0xf7ef, 0xfb4c\n"
        "pop {r0, pc}\n"
    );
}

#endif
