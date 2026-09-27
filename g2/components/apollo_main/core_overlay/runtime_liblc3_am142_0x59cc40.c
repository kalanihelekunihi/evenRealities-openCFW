/*
 * Clean-room Thumb source for the AM142 0x0059cc40 mixed loop-tail/prologue
 * span.  External helper calls and the carried trailing 32-bit-instruction
 * halfword stay explicit until adjacent AM142 spans are source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059cc40(void)
{
    __asm__ volatile(
        "lsls r0, r6, #2\n"
        "ldrb.w r0, [r0, #0x224]\n"
        "cmp r0, #0\n"
        "bne 4f\n"
        "uxtb.w r9, r9\n"
        "cmp.w r9, #0\n"
        "beq 1f\n"
        "movs r4, #1\n"
        "b 3f\n"
        "1:\n"
        "movs r4, #0\n"
        "b 3f\n"
        "2:\n"
        "movs r1, r4\n"
        "movs r0, r5\n"
        ".hword 0xf002, 0xf97a\n" /* bl 0x0059ef58 */
        "adds.w r10, r0, r10\n"
        "str.w r10, [sp, #8]\n"
        "adds r1, r4, #1\n"
        "movs r0, r5\n"
        ".hword 0xf002, 0xf972\n" /* bl 0x0059ef58 */
        "adds.w r10, r0, r10\n"
        "str.w r10, [sp, #0xc]\n"
        "movs r0, #0\n"
        "strb.w r0, [sp, #4]\n"
        "movs r0, #0\n"
        "str r0, [sp, #0x10]\n"
        "ldr r0, [sp, #0x10]\n"
        "str r0, [sp, #0x14]\n"
        "add r1, sp, #4\n"
        "movs r0, r6\n"
        ".hword 0xf7fd, 0xfbb4\n" /* bl 0x0059a3fa */
        "adds r4, r4, #2\n"
        "3:\n"
        "cmp r4, r8\n"
        "blo 2b\n"
        "movs r0, r5\n"
        ".hword 0xf002, 0xfa0f\n" /* bl 0x0059f0bc */
        "4:\n"
        "movs r0, #1\n"
        "strb r0, [r7]\n"
        "add sp, #0x1c\n"
        "pop.w {r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "push.w {r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "sub sp, #0x48\n"
        "movs r4, r1\n"
        "movs r5, r2\n"
        "movs r6, r3\n"
        "ldr r7, [sp, #0x70]\n"
        "ldr r1, [r4]\n"
        "str r1, [sp, #0x10]\n"
        "ldr r1, [r5]\n"
        "str r1, [sp, #0x14]\n"
        "movs.w r8, #0\n"
        "ldrb r1, [r7, #9]\n"
        "cmp r1, #0\n"
        "bne 5f\n"
        "movs.w r9, #1\n"
        "b 6f\n"
        "5:\n"
        "movs.w r9, #0\n"
        "6:\n"
        "mov r1, r9\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        ".hword 0xd002\n"        /* beq 0x0059cce0 */
        ".hword 0xf05f\n"        /* first halfword of trailing movs.w */
    );
}
