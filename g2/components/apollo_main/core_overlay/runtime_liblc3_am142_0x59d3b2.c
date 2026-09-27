/*
 * Clean-room Thumb source for the AM142 0x0059d3b2 stack/setup control
 * fragment.  Calls and branches leave this routed span, so those transfer
 * halfwords remain explicit with decoded destinations.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059d3b2(void)
{
    __asm__ volatile(
        "ldr r0, [r0, #4]\n"
        ".hword 0xe000\n"        /* b 0x0059d3b8 */
        "movs r0, #0\n"
        "str r0, [sp, #4]\n"
        "add r0, sp, #0x18\n"
        "str r0, [sp]\n"
        "add.w r3, sp, #0x3c00\n"
        "ldr.w r3, [r3, #0x2f4]\n"
        "add r2, sp, #0x90\n"
        "movs r1, r5\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        ".hword 0xf7ff, 0xfc02\n" /* bl 0x0059cbda */
        "ldrb.w r0, [r6, #0x224]\n"
        "cmp r0, #0\n"
        ".hword 0xd101\n"        /* bne 0x0059d3e2 */
        ".hword 0xf001, 0xba78\n" /* b.w 0x0059e8d2 */
        ".hword 0xe637\n"        /* b 0x0059d054 */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #8]\n"
        "cmp r0, #0\n"
        ".hword 0xd105\n"        /* bne 0x0059d3fe */
        "add r0, sp, #0x54\n"
        ".hword 0xf7ff, 0xfb9e\n" /* bl 0x0059cb34 */
        "cmp r0, #0\n"
        ".hword 0xf041, 0x826a\n" /* bne.w 0x0059e8d2 */
        ".hword 0xf50d\n"        /* leading halfword of next add.w */
    );
}
