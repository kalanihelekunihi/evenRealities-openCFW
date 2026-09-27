/*
 * Clean-room Thumb source for the AM142 0x0059b714 ring-position search
 * fragment.  The fallback call and final fall-through branch leave this route,
 * so their transfer halfwords remain explicit with decoded destinations.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b714(void)
{
    __asm__ volatile(
        "movs r0, r1\n"
        "ldr r1, [r5, #0x14]\n"
        "cmp r1, #0\n"
        "beq 1f\n"
        "ldrb r1, [r5, #0xd]\n"
        "cmp r1, #0\n"
        "bne 2f\n"
        "1:\n"
        "ldr r1, [r5, #0x10]\n"
        ".hword 0xf750, 0xfff8\n" /* bl 0x004ec718 */
        ".hword 0xe037\n"        /* b 0x0059b79a */
        "2:\n"
        "ldr r4, [r5, #0x18]\n"
        "b 4f\n"
        "3:\n"
        "adds r4, r4, #1\n"
        "4:\n"
        "ldr r1, [r5, #0x14]\n"
        "subs r1, r1, #1\n"
        "cmp r4, r1\n"
        "bhs 5f\n"
        "movs r1, #0x14\n"
        "mul r1, r1, r4\n"
        "add r1, r5\n"
        "ldr r1, [r1, #0x38]\n"
        "cmp r0, r1\n"
        "bge 3b\n"
        "5:\n"
        "cmp r4, #0\n"
        "beq 6f\n"
        "movs r1, #0x14\n"
        "mul r1, r1, r4\n"
        "add r1, r5\n"
        "ldr r1, [r1, #0x24]\n"
        "cmp r0, r1\n"
        "bge 6f\n"
        "subs r4, r4, #1\n"
        "b 5b\n"
        "6:\n"
        "str r4, [r5, #0x18]\n"
        "cmp r4, #0\n"
        ".hword 0xd10a\n"        /* bne 0x0059b778 */
        "ldr r1, [r5, #0x24]\n"
        "cmp r0, r1\n"
        ".hword 0xda07\n"        /* bge 0x0059b778 */
        "ldr r1, [r5, #0x10]\n"
    );
}
