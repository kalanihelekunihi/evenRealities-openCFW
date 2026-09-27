/*
 * Clean-room Thumb source for the AM142 0x0059ca2c state-commit and callback
 * prologue span.  Cross-span calls and the carried trailing 32-bit-instruction
 * halfword remain explicit until neighboring AM142 spans are source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059ca2c(void)
{
    __asm__ volatile(
        ".hword 0xf7ff, 0xfc87\n" /* bl 0x0059c33e */
        "movs r0, #1\n"
        "strb.w r0, [r4, r9]\n"
        "movs r0, #4\n"
        "movw r1, #0x2de4\n"
        "str r0, [r4, r1]\n"
        "ldrd r0, r1, [sp, #0x24]\n"
        "movw r2, #0x2de8\n"
        "add r2, r4\n"
        "strd r0, r1, [r2]\n"
        "ldrd r0, r1, [sp, #0x1c]\n"
        "movw r2, #0x2df0\n"
        "add r2, r4\n"
        "strd r0, r1, [r2]\n"
        "ldrd r0, r1, [sp, #0x34]\n"
        "movw r2, #0x2df8\n"
        "add r2, r4\n"
        "strd r0, r1, [r2]\n"
        "ldrd r0, r1, [sp, #0x2c]\n"
        "adds.w r2, r4, #0x2e00\n"
        "strd r0, r1, [r2]\n"
        "movw r9, #0x2d9c\n"
        "ldr.w r0, [r4, r9]\n"
        ".hword 0xf000, 0xf85c\n" /* bl 0x0059cb38 */
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r0, #0\n"
        "str r0, [sp, #4]\n"
        "movw r0, #0x2da0\n"
        "ldr r0, [r4, r0]\n"
        "str r0, [sp]\n"
        "ldr.w r3, [r4, r9]\n"
        "movw r0, #0x2d98\n"
        "ldr r2, [r4, r0]\n"
        "movw r0, #0x2d94\n"
        "ldr r1, [r4, r0]\n"
        "adds.w r0, r4, #8\n"
        ".hword 0xf7ff, 0xf8c1\n" /* bl 0x0059bc2a */
        "1:\n"
        "str r5, [r4, r7]\n"
        "str.w r6, [r4, r8]\n"
        "add sp, #0x44\n"
        "pop.w {r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "push {r1, r2, r3, r4, r5, r6, r7, lr}\n"
        "movs r4, r0\n"
        "movw r5, #0x2d90\n"
        "ldrb r0, [r4, r5]\n"
        "cmp r0, #0\n"
        ".hword 0xd02c\n"        /* beq 0x0059cb1c */
        "movw r6, #0x2d91\n"
        "movs r0, #1\n"
        "strb r0, [r4, r6]\n"
        "movw r0, #0x2ddc\n"
        "ldr r2, [r4, r0]\n"
        "movw r0, #0x2dd8\n"
        "ldr r1, [r4, r0]\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfe8c\n" /* bl 0x0059c7f4 */
        "movw r7, #0x2de0\n"
        "ldrb r0, [r4, r7]\n"
        "cmp r0, #0\n"
        ".hword 0xd010\n"        /* beq 0x0059cb08 */
        "movs r0, #1\n"
        "str r0, [sp, #4]\n"
        "adds.w r2, r4, #0x2dc0\n"
        "ldrd r0, r1, [r2]\n"
        "str r1, [sp]\n"
        "movs r3, r0\n"
        "movw r0, #0x2db8\n"
        ".hword 0xeb04\n"        /* first halfword of trailing add.w */
    );
}
