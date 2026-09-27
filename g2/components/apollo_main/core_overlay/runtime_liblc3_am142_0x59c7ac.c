/*
 * Clean-room Thumb source for the AM142 0x0059c7ac arithmetic setup tail and
 * following prologue prefix.  Branch/call transfers whose targets are outside
 * this routed span remain explicit with decoded destinations attached.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059c7ac(void)
{
    __asm__ volatile(
        ".hword 0xd006\n"        /* beq 0x0059c7bc */
        "movw r0, #0x2d9c\n"
        "ldr r0, [r4, r0]\n"
        ".hword 0xf000, 0xf9c0\n" /* bl 0x0059cb38 */
        "cmp r0, #0\n"
        ".hword 0xd012\n"        /* beq 0x0059c7e2 */
        "movs r0, #0\n"
        "str r0, [sp, #4]\n"
        "movw r0, #0x2da0\n"
        "ldr r0, [r4, r0]\n"
        "str r0, [sp]\n"
        "movw r0, #0x2d9c\n"
        "ldr r3, [r4, r0]\n"
        "movw r0, #0x2d98\n"
        "ldr r2, [r4, r0]\n"
        "movw r0, #0x2d94\n"
        "ldr r1, [r4, r0]\n"
        "adds.w r0, r4, #8\n"
        ".hword 0xf7ff, 0xfa24\n" /* bl 0x0059bc2a */
        "addw r0, r4, #0xf24\n"
        "adds.w r1, r4, #8\n"
        "movw r2, #0xf1c\n"
        ".hword 0xf665, 0xfa19\n" /* bl 0x00401c24 */
        "pop {r0, r1, r4, r5, r6, pc}\n"
        "push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}\n"
        "sub sp, #0x24\n"
        "movs r4, r0\n"
        "mov sl, r1\n"
        "movs r5, r2\n"
    );
}
