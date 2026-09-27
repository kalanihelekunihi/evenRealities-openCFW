/*
 * Clean-room Thumb source for the AM142 0x0059b6d0 flag/setter and small
 * initializer/accessor cluster.  The memset-like call targets a shared helper
 * outside this routed section, so its BL halfwords remain explicit with the
 * decoded destination attached.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b6d0(void)
{
    __asm__ volatile(
        "orrs r1, r1, #0x10\n"
        "str r1, [r0]\n"
        "bx lr\n"
        "push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "movs r6, r2\n"
        "movs r7, r3\n"
        "ldr.w r8, [sp, #0x20]\n"
        "movw r1, #0xf1c\n"
        "movs r2, #0\n"
        "mov r9, r4\n"
        "mov r0, r9\n"
        ".hword 0xf668, 0xfd07\n" /* bl 0x00404104 */
        "ldrb.w r0, [r5, #0xb8]\n"
        "strb r0, [r4, #0xd]\n"
        "str.w r8, [r4, #0x10]\n"
        "str r5, [r4]\n"
        "str r6, [r4, #4]\n"
        "str r7, [r4, #8]\n"
        "pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
        "ldrb r0, [r0, #0xc]\n"
        "bx lr\n"
        "bx lr\n"
        "push {r4, r5, r6, lr}\n"
    );
}
