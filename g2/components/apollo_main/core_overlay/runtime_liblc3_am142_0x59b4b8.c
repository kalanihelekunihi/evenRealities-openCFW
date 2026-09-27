/*
 * Clean-room Thumb source for the AM142 0x0059b4b8 mixed TNS/MDCT helper span.
 * Cross-island calls stay as reviewed halfwords until their callees are pulled
 * through as source-owned symbols.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b4b8(void)
{
    __asm__ volatile(
        "movs r0, r6\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "ldr.w r0, [r5, #0x260]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r4, #4]\n"
        "ldr.w r1, [r5, #0x260]\n"
        "ldr.w r1, [r1, r6, lsl #2]\n"
        "add r0, r1\n"
        "str r0, [r4, #8]\n"
        "b 3f\n"
        "1:\n"
        "ldr.w r0, [r5, #0x25c]\n"
        "cmp r0, #0\n"
        "bmi 4f\n"
        "ldr.w r0, [r5, #0x25c]\n"
        "b 5f\n"
        "4:\n"
        "movs r0, #0\n"
        "5:\n"
        "ldr r1, [r4, #4]\n"
        "add r0, r1\n"
        "str r0, [r4, #4]\n"
        "ldr.w r0, [r5, #0x23c]\n"
        "add.w r0, r0, r6, lsl #2\n"
        "ldr r0, [r0, #4]\n"
        "str r0, [r4, #8]\n"
        "3:\n"
        "ldr r0, [r4, #4]\n"
        "cmp r0, #0\n"
        "bne 6f\n"
        "b 6f\n"
        "2:\n"
        "ldr.w r0, [r5, #0x23c]\n"
        "add.w r0, r0, r6, lsl #2\n"
        "ldr r0, [r0, #4]\n"
        "str r0, [r4, #8]\n"
        "6:\n"
        "ldr r0, [r4, #4]\n"
        "str r0, [r4, #0xc]\n"
        "movs r0, #0\n"
        "pop {r1, r4, r5, r6, r7, pc}\n"

        "ldr.w r0, [r0, #0x218]\n"
        "ldr.w r0, [r0, #0x21c]\n"
        "lsls r0, r0, #0x10\n"
        "bx lr\n"

        "ldr.w r0, [r0, #0x218]\n"
        "ldr.w r0, [r0, #0x220]\n"
        "lsls r0, r0, #0x10\n"
        "bx lr\n"

        "push {r7, lr}\n"
        "ldr r1, [r0, #0x1c]\n"
        "movs r2, #0\n"
        "str r2, [r0, #0x10]\n"
        "ldr r0, [r1, #0xc]\n"
        ".hword 0xf751, 0xfb47\n" /* bl 0x004ecbc8 */
        "pop {r0, pc}\n"

        "push {r4, lr}\n"
        "ldr r4, [r0, #0x1c]\n"
        "movs r0, r4\n"
        ".hword 0xf7fe, 0xfa30\n" /* bl 0x005999a6 */
        "ldr r0, [r4, #0xc]\n"
        ".hword 0xf751, 0xfca7\n" /* bl 0x004ece9a */
        "pop {r4, pc}\n"

        "push {r4}\n"
        "movs r4, r0\n"
        "subs r3, r3, r1\n"
        "smultt r0, r4, r3\n"
        "subs r4, r2, r4\n"
        "smultt r1, r1, r4\n"
        "subs r0, r0, r1\n"
        "pop {r4}\n"
        "bx lr\n"

        "push.w {r3, r4, r5, r6, r7, r8, r9, lr}\n"
        "movs r5, r0\n"
        "movs r7, r1\n"
        "movs r6, r2\n"
        "mov r8, r3\n"
        "ldr r4, [sp, #0x28]\n"
        "movs r1, #0x14\n"
        "movs r2, #0\n"
        "mov r9, r5\n"
        "mov r0, r9\n"
        ".hword 0xf668, 0xfdc3\n" /* bl 0x00404104 */
        "movs r1, r6\n"
        "movs r0, r7\n"
        ".hword 0xf7fe, 0xff2a\n" /* bl 0x0059a3da */
        "movs r7, r0\n"
        "ldr r1, [r7, #8]\n"
        "ldr r0, [r7, #4]\n"
        "subs r1, r1, r0\n"
        "cmn.w r1, #0x150000\n"
        "bne 7f\n"
        "uxtb r4, r4\n"
        "cmp r4, #0\n"
        "beq 8f\n"
        "ldr r0, [r7, #8]\n"
        "str r0, [r5, #8]\n"
        "movs r0, #1\n"
        "str r0, [r5]\n"
        ".hword 0xe02b\n"        /* b 0x0059b5fc */
        "8:\n"
        "movs r0, #0\n"
        "str r0, [r5]\n"
        ".hword 0xe028\n"        /* b 0x0059b5fc */
        "7:\n"
        "cmn.w r1, #0x140000\n"
        ".hword 0xd10a\n"        /* bne 0x0059b5c6 */
        "uxtb r4, r4\n"
        "cmp r4, #0\n"
        ".hword 0xd002\n"        /* beq 0x0059b5bc */
        "movs r0, #0\n"
        "str r0, [r5]\n"
    );
}
