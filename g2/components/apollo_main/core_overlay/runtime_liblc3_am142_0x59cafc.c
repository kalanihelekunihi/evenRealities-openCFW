/*
 * Clean-room Thumb source for the AM142 0x0059cafc local setup and byte
 * accessor cluster.  Calls target helpers outside this routed section, so the
 * BL halfwords remain explicit with their decoded destinations attached.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059cafc(void)
{
    __asm__ volatile(
        "lsls r0, r0, #8\n"
        "adds.w r1, r4, #8\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfc1b\n" /* bl 0x0059c33e */
        "movs r0, #1\n"
        "movw r1, #0x2d93\n"
        "strb r0, [r4, r1]\n"
        "movs r0, #0\n"
        "strb r0, [r4, r5]\n"
        "movs r0, #0\n"
        "strb r0, [r4, r6]\n"
        "movs r0, #0\n"
        "strb r0, [r4, r7]\n"
        "pop {r0, r1, r2, r4, r5, r6, r7, pc}\n"
        "push {r4, r5, r6, lr}\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "movs r1, #0x1c\n"
        "movs r2, #0\n"
        "movs r6, r4\n"
        "movs r0, r6\n"
        ".hword 0xf667, 0xfaea\n" /* bl 0x00404104 */
        "str r5, [r4]\n"
        "pop {r4, r5, r6, pc}\n"
        "ldrb r0, [r0, #4]\n"
        "bx lr\n"
        "ldrb r0, [r0, #5]\n"
        "bx lr\n"
        "strb r1, [r0, #5]\n"
        "bx lr\n"
        "adds r0, #0x10\n"
    );
}
