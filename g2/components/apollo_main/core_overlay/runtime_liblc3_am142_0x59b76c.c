/*
 * Clean-room Thumb source for the AM142 0x0059b76c mixed tail/head span.
 * The fragment includes a prior routine return plus the next routine prologue;
 * outbound calls and the branch into the following span stay explicit until
 * those AM142 neighbors are source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b76c(void)
{
    __asm__ volatile(
        "subs r0, r0, r2\n"
        ".hword 0xf750, 0xffd3\n" /* bl 0x004ec718 */
        "ldr r1, [r5, #0x28]\n"
        "adds r0, r1, r0\n"
        "b 1f\n"
        "movs r6, #0x14\n"
        "mul r1, r6, r4\n"
        "add r1, r5\n"
        "ldr r1, [r1, #0x2c]\n"
        "mul r2, r6, r4\n"
        "add r2, r5\n"
        "ldr r2, [r2, #0x24]\n"
        "subs r0, r0, r2\n"
        ".hword 0xf750, 0xffc4\n" /* bl 0x004ec718 */
        "muls r4, r6, r4\n"
        "add.w r1, r5, r4\n"
        "ldr r1, [r1, #0x28]\n"
        "adds r0, r1, r0\n"
        "1:\n"
        "pop {r4, r5, r6, pc}\n"
        "push.w {r2, r3, r4, r5, r6, r7, r8, r9, r10, lr}\n"
        "movs r6, r0\n"
        "ldr r0, [r6, #8]\n"
        ".hword 0xf7fe, 0xfe12\n" /* bl 0x0059a3cc */
        "movs r4, #0\n"
        ".hword 0xe082\n"        /* b 0x0059b8b2 */
        "movs.w r10, #0\n"
        "movs r0, #1\n"
        "b 2f\n"
        "movs r0, #0\n"
        "2:\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldr r0, [r6, #0x14]\n"
        "subs r0, r0, #1\n"
        "cmp r7, r0\n"
        "bhs 3f\n"
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "adds r0, #0x30\n"
        ".hword 0xf7ff, 0xff73\n" /* bl 0x0059b6b6 */
        "cmp r0, #0\n"
        "bne 3f\n"
        "str r7, [sp]\n"
        "subs.w r5, r5, r10\n"
        "str r5, [sp, #4]\n"
        "mov r1, sp\n"
        "ldr r0, [r6, #8]\n"
        ".hword 0xf7fe, 0xfe0b\n" /* bl 0x0059a3fa */
        "3:\n"
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x28]\n"
        "adds.w r0, r10, r0\n"
        "mul r1, r8, r4\n"
        "add r1, r6\n"
        "str r0, [r1, #0x28]\n"
        "mov r0, r9\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd00a\n"        /* beq 0x0059b816 */
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x28]\n"
    );
}
