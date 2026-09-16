/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned helpers from the AM-002 retained island.
 */

#if defined(OPEN_CFW_AM002_EXPAND_COPY_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am002_expand_copy(void)
{
    __asm__ volatile(
        "push {r4, r5, r6, r7}\n"
        "mov r2, r0\n"
        "ldr r0, [r2]\n"
        "ldr r5, [r2, #8]\n"
        "adds r3, r2, r0\n"
        "ldr r0, [r2, #4]\n"
        "add.w r4, r3, r0, lsr #1\n"
        "lsls r0, r0, #0x1f\n"
        "it mi\n"
        "addmi r5, sb\n"
        "1:\n"
        "cmp r3, r4\n"
        "beq.n 7f\n"
        "ldrb r6, [r3], #1\n"
        "ands r0, r6, #3\n"
        "itt eq\n"
        "ldrbeq r0, [r3], #1\n"
        "addeq r0, r0, #3\n"
        "lsrs r1, r6, #4\n"
        "cmp r1, #0xf\n"
        "bne.n 2f\n"
        "ldrb r1, [r3], #1\n"
        "adds r1, #0xf\n"
        "b.n 2f\n"
        "3:\n"
        "ldrb r7, [r3], #1\n"
        "strb r7, [r5], #1\n"
        "2:\n"
        "subs r0, r0, #1\n"
        "bne.n 3b\n"
        "cmp r1, #0\n"
        "beq.n 1b\n"
        "ldrb r0, [r3], #1\n"
        "ubfx r6, r6, #2, #2\n"
        "cmp r6, #3\n"
        "it eq\n"
        "ldrbeq r6, [r3], #1\n"
        "add.w r0, r0, r6, lsl #8\n"
        "rsbs r0, r0, #0\n"
        "add r0, r5\n"
        "movs r6, #0\n"
        "4:\n"
        "subs r7, r6, #2\n"
        "cmp r7, r1\n"
        "ittt ne\n"
        "ldrbne r7, [r0], #1\n"
        "strbne r7, [r5], #1\n"
        "addne r6, r6, #1\n"
        "bne.n 4b\n"
        "b.n 1b\n"
        "7:\n"
        "pop {r4, r5, r6, r7}\n"
        "add.w r0, r2, #0xc\n"
        "bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM002_DOUBLE_RANGE_PREDICATE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am002_double_range_predicate(void)
{
    __asm__ volatile(
        "mov.w ip, #0x100000\n"
        "cmn.w ip, r1, lsl #1\n"
        "itte ls\n"
        "cmnls.w ip, r3, lsl #1\n"
        "movls r0, #0\n"
        "movhi r0, #1\n"
        "bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM002_FLOAT_HELPER_WRAPPER_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am002_float_helper_wrapper(void)
{
    __asm__ volatile(
        "vmov r0, s0\n"
        "mov ip, lr\n"
        "bl open_cfw_runtime_am002_integer_float_helper\n"
        "vmov s0, r0\n"
        "bx ip\n"
    );
}
#endif

#if defined(OPEN_CFW_AM002_INTEGER_FLOAT_HELPER_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am002_integer_float_helper(void)
{
    __asm__ volatile(
        "ubfx r2, r0, #0x17, #8\n"
        "subs r2, #0x7e\n"
        "ble.n 1f\n"
        "cmp r2, #0x18\n"
        "bge.n 2f\n"
        "mvn r1, #0xff000000\n"
        "lsrs r1, r2\n"
        "tst r0, r0\n"
        "it mi\n"
        "addmi r0, r0, r1\n"
        "bics r0, r1\n"
        "bx lr\n"
        "1:\n"
        "cmn r0, r0\n"
        "itt ne\n"
        "movne r0, #0\n"
        "movtne r0, #0xbf80\n"
        "it lo\n"
        "movlo r0, #0\n"
        "2:\n"
        "bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM002_QUADRATIC_FLOAT_INTERPOLATE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am002_quadratic_float_interpolate(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "vpush {d8, d9, d10, d11}\n"
        "mov r4, r0\n"
        "mov r5, r1\n"
        "vmov.f32 s17, s0\n"
        "vldr s20, [r0]\n"
        "vldr s21, [r1]\n"
        "vldr s19, [r1, #8]\n"
        "vldr s18, [r0, #8]\n"
        "mov r6, r0\n"
        "add.w r7, r0, #0xc\n"
        "1:\n"
        "vldmia r6!, {s0}\n"
        "bl open_cfw_runtime_liblc3_float_classify_wrapper\n"
        "cbnz r0, 4f\n"
        "cmp r7, r6\n"
        "bne.n 1b\n"
        "vldr s16, [r4, #4]\n"
        "vldr s15, [r4]\n"
        "vcmpe.f32 s16, s15\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bpl.n 2f\n"
        "vldr s20, [r4, #8]\n"
        "vldr s21, [r5, #8]\n"
        "vldr s19, [r5]\n"
        "vmov.f32 s18, s15\n"
        "2:\n"
        "vmov.f32 s0, s17\n"
        "vldr s22, [r5, #4]\n"
        "bl open_cfw_runtime_liblc3_float_classify_wrapper\n"
        "cbz r0, 5f\n"
        "ldr r3, [pc, #0x50]\n"
        "vldr s16, [r3]\n"
        "4:\n"
        "vmov.f32 s0, s16\n"
        "vpop {d8, d9, d10, d11}\n"
        "pop {r3, r4, r5, r6, r7, pc}\n"
        "5:\n"
        "vsub.f32 s12, s16, s20\n"
        "vsub.f32 s14, s22, s21\n"
        "vsub.f32 s16, s18, s16\n"
        "vsub.f32 s19, s19, s22\n"
        "vdiv.f32 s15, s14, s12\n"
        "vdiv.f32 s14, s19, s16\n"
        "vsub.f32 s18, s18, s20\n"
        "vsub.f32 s14, s14, s15\n"
        "vdiv.f32 s13, s14, s18\n"
        "vsub.f32 s17, s17, s20\n"
        "vfms.f32 s15, s12, s13\n"
        "vmov.f32 s16, s21\n"
        "vfma.f32 s15, s13, s17\n"
        "vfma.f32 s16, s15, s17\n"
        "vmov.f32 s0, s16\n"
        "vpop {d8, d9, d10, d11}\n"
        "pop {r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif
