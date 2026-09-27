/*
 * Clean-room Thumb source for the AM142 0x0059ce1e mixed boundary/helper span.
 * The first halfword completes the previous span's 32-bit multiply; helper
 * calls and the padding boundary before the next prologue stay explicit until
 * neighboring AM142 spans are collapsed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059ce1e(void)
{
    __asm__ volatile(
        ".hword 0xf207\n"        /* second halfword of previous mul */
        "add.w r1, r1, r2, lsl #2\n"
        "ldr r3, [r1, #0x10]\n"
        "add r1, sp, #0x10\n"
        "mul r2, r0, r7\n"
        "add.w r1, r1, r2, lsl #2\n"
        "ldr r2, [r1, #0xc]\n"
        "add r1, sp, #0x10\n"
        "mul r0, r0, r7\n"
        "add.w r0, r1, r0, lsl #2\n"
        "ldr r1, [r0, #8]\n"
        "movs r0, r6\n"
        ".hword 0xf7ff, 0xfd77\n" /* bl 0x0059c932 */
        "adds r7, r7, #1\n"
        "cmp r7, #2\n"
        ".hword 0xdbd1\n"        /* blt 0x0059cdee */
        "ldr r0, [sp, #0xc]\n"
        ".hword 0xf002, 0xf936\n" /* bl 0x0059f0bc */
        "add r0, sp, #0x10\n"
        "ldr r1, [r0, #0x30]\n"
        "str r1, [r4]\n"
        "ldr r0, [r0, #0x34]\n"
        "str r0, [r5]\n"
        "add sp, #0x4c\n"
        "pop.w {r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "push.w {r0, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "sub sp, #8\n"
        "movs r4, r1\n"
        "movs r5, r2\n"
        "ldr r0, [sp, #8]\n"
        "ldr r0, [r0, #0x14]\n"
        "mul r0, r0, r5\n"
        "str r0, [sp]\n"
        "movs r0, r4\n"
        ".hword 0xf001, 0xfff5\n" /* bl 0x0059ee64 */
        "movs r6, r0\n"
        "ldr r0, [sp]\n"
        "subs r6, r6, r0\n"
        "adds r7, r5, r6\n"
        "movs.w r8, #0\n"
        "b 2f\n"
        "1:\n"
        "movs r1, r7\n"
        "movs r0, r4\n"
        ".hword 0xf002, 0xf864\n" /* bl 0x0059ef58 */
        "adds r7, r7, #1\n"
        "movs r1, r0\n"
        "ldr.w r0, [r10]\n"
        ".hword 0xf74f, 0xfc3e\n" /* bl 0x004ec718 */
        "adds.w r10, r10, #4\n"
        "adds.w r11, r0, r11\n"
        "adds.w r9, r9, #1\n"
        "4:\n"
        "ldr r0, [sp, #8]\n"
        "ldr r0, [r0, #0x14]\n"
        "cmp r9, r0\n"
        "blo 1b\n"
        "mov r2, r11\n"
        "adds.w r1, r6, r8\n"
        "movs r0, r4\n"
        ".hword 0xf002, 0xf881\n" /* bl 0x0059efbe */
        "adds.w r8, r8, #1\n"
        "2:\n"
        "cmp r8, r5\n"
        "bhs 3f\n"
        "ldr r0, [sp, #8]\n"
        "ldr r0, [r0, #0x18]\n"
        "adds.w r10, r0, #4\n"
        "adds.w r1, r6, r8\n"
        "movs r0, r4\n"
        ".hword 0xf002, 0xf841\n" /* bl 0x0059ef58 */
        "mov r11, r0\n"
        "movs.w r9, #1\n"
        "b 4b\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "subs r5, r0, r5\n"
        "movs r1, r5\n"
        "movs r0, r4\n"
        ".hword 0xf002, 0xf881\n" /* bl 0x0059efec */
        "pop.w {r0, r1, r2, r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        ".hword 0x0000\n"
        "push.w {r0, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "sub.w sp, sp, #0x3e00\n"
        "sub sp, #0xb8\n"
        "movs r7, r1\n"
        "movs r4, #0\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldr.w r6, [r0, #0xb0]\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "adds r0, r0, #4\n"
        "str r0, [sp, #0x1c]\n"
        "add.w r0, sp, #0x3c00\n"
    );
}
