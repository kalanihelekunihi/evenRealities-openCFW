/*
 * Clean-room Thumb source for the AM142 0x0059c820 state comparison leaf.
 * The conditional branches target runtime addresses outside this extracted
 * section, so their already-decoded halfwords are recorded with target notes.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059c820(void)
{
    __asm__ volatile(
        "movw r7, #0x2dc8\n"
        "ldr r0, [r4, r7]\n"
        "cmp r0, sl\n"
        ".hword 0xd108\n"        /* bne 0x0059c83c */
        "movw r0, #0x2dcc\n"
        "ldr r0, [r4, r0]\n"
        "cmp r0, r5\n"
        ".hword 0xd103\n"        /* bne 0x0059c83c */
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd077\n"        /* beq 0x0059c92c */
        ".hword 0xf642\n"        /* leading halfword of next movw */
    );
}
