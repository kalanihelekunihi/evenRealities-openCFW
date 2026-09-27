/*
 * Clean-room Thumb source for the AM142 0x0059d380 late-control fragment.
 * Control-flow transfers leave this routed span, so those branch/call
 * halfwords remain explicit with decoded destinations.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059d380(void)
{
    __asm__ volatile(
        "asrs r0, r7, #0xa\n"
        "strb.w r0, [r1, #0x5d]\n"
        ".hword 0xe699\n"        /* b 0x0059d0bc */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #8]\n"
        "cmp r0, #0\n"
        ".hword 0xd105\n"        /* bne 0x0059d3a2 */
        "add r0, sp, #0x54\n"
        ".hword 0xf7ff, 0xfbcc\n" /* bl 0x0059cb34 */
        "cmp r0, #0\n"
        ".hword 0xf041, 0x8298\n" /* bne.w 0x0059e8d2 */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #8]\n"
        "cmp r0, #0\n"
        ".hword 0xd002\n"        /* beq 0x0059d3b6 */
        "ldr r0, [r6, #0x20]\n"
    );
}
