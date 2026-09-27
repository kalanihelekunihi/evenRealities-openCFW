/*
 * Clean-room Thumb source for the AM142 0x0059c83e stack/accumulator leaf.
 * The call target is outside this routed section, so the BL halfwords remain
 * explicit with the decoded destination attached.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059c83e(void)
{
    __asm__ volatile(
        "ldr r4, [r1, r3]\n"
        "add r0, sp, #0xc\n"
        "str r0, [sp, #8]\n"
        "add r0, sp, #0x10\n"
        "str r0, [sp, #4]\n"
        "str r5, [sp]\n"
        "mov r3, sl\n"
        "ldr.w r2, [r4, r8]\n"
        "ldr r1, [r4, r7]\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfea5\n" /* bl 0x0059c5a2 */
        "ldr r1, [r4, r7]\n"
        "ldr r0, [sp, #0x10]\n"
        "adds r1, r0, r1\n"
        "str r1, [sp, #0x1c]\n"
        "ldr.w r1, [r4, r8]\n"
        "ldr r0, [sp, #0xc]\n"
    );
}
