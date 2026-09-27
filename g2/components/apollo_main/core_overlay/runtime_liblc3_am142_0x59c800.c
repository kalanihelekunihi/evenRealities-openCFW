/*
 * Clean-room Thumb source for the AM142 0x0059c800 floating-point guard
 * fragment.  PC-relative transfer halfwords are kept explicit because the
 * overlay routes only this leaf span while the original branch/call targets
 * live outside the section.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059c800(void)
{
    __asm__ volatile(
        "movw fp, #0x2d9c\n"
        "ldr.w r0, [r4, fp]\n"
        ".hword 0xf000, 0xf996\n" /* bl 0x0059cb38 */
        "cmp r0, #0\n"
        ".hword 0xd006\n"        /* beq 0x0059c81e */
        "movw r0, #0x2d91\n"
        "ldrb r0, [r4, r0]\n"
        "cmp r0, #0\n"
        ".hword 0xd101\n"        /* bne 0x0059c81e */
        "movs r6, #1\n"
    );
}
