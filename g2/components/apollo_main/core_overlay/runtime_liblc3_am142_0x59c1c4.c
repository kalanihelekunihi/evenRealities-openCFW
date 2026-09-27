/*
 * Clean-room Thumb source for the AM142 0x0059c1c4 accumulator update
 * fragment.  The final branch targets code outside this routed section, so
 * that transfer halfword remains explicit with its decoded destination.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059c1c4(void)
{
    __asm__ volatile(
        "ldr.w r0, [sl]\n"
        "subs r1, r1, r0\n"
        "b 1f\n"
        "ldr.w r1, [sl]\n"
        "ldr r0, [r6]\n"
        "subs r1, r1, r0\n"
        "1:\n"
        "movw r0, #0x2db4\n"
        "ldr r0, [r5, r0]\n"
        "cmp r1, r0\n"
        "bge 2f\n"
        "ldr r0, [r6]\n"
        "str.w r0, [sl]\n"
        "2:\n"
        "ldr r0, [r6, #4]\n"
        "ldr r1, [r7, #4]\n"
        "cmp r0, r1\n"
        ".hword 0xd116\n"        /* bne 0x0059c21a */
        "ldr.w r1, [sl, #4]\n"
        "ldr r0, [r6, #4]\n"
        "subs r1, r1, r0\n"
        "cmp r1, #0\n"
        "bpl 3f\n"
        "ldr r1, [r6, #4]\n"
        "ldr.w r0, [sl, #4]\n"
        "subs r1, r1, r0\n"
        ".hword 0xe003\n"        /* b 0x0059c20a */
        "3:\n"
    );
}
