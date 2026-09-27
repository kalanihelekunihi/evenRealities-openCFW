/*
 * Clean-room Thumb source for the AM142 0x0059d8f0 dispatch prefix.  The
 * long outbound dispatch branches and shared helper calls stay explicit until
 * the large downstream AM142 bodies are source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059d8f0(void)
{
    __asm__ volatile(
        "strh r6, [r7, #0x10]\n"
        "cmp r0, #0xc\n"
        ".hword 0xf000, 0x8249\n" /* beq.w 0x0059dd8a */
        "cmp r0, #0xe\n"
        ".hword 0xf000, 0x826c\n" /* beq.w 0x0059ddd6 */
        "cmp r0, #0xf\n"
        ".hword 0xf000, 0x827c\n" /* beq.w 0x0059ddfc */
        "cmp r0, #0x10\n"
        ".hword 0xf000, 0x828b\n" /* beq.w 0x0059de20 */
        "cmp r0, #0x11\n"
        ".hword 0xf000, 0x84c6\n" /* beq.w 0x0059e29c */
        "cmp r0, #0x12\n"
        ".hword 0xf000, 0x84e3\n" /* beq.w 0x0059e2dc */
        "cmp r0, #0x14\n"
        ".hword 0xf000, 0x84e5\n" /* beq.w 0x0059e2e6 */
        "cmp r0, #0x15\n"
        ".hword 0xf000, 0x84f2\n" /* beq.w 0x0059e306 */
        "cmp r0, #0x16\n"
        ".hword 0xf000, 0x84fe\n" /* beq.w 0x0059e324 */
        "cmp r0, #0x17\n"
        ".hword 0xf000, 0x8513\n" /* beq.w 0x0059e354 */
        "cmp r0, #0x18\n"
        ".hword 0xf000, 0x8526\n" /* beq.w 0x0059e380 */
        "cmp r0, #0x1a\n"
        ".hword 0xf000, 0x8533\n" /* beq.w 0x0059e3a0 */
        "cmp r0, #0x1b\n"
        ".hword 0xf000, 0x8551\n" /* beq.w 0x0059e3e2 */
        "cmp r0, #0x1c\n"
        ".hword 0xf000, 0x855c\n" /* beq.w 0x0059e3fe */
        "cmp r0, #0x1d\n"
        ".hword 0xf000, 0x856b\n" /* beq.w 0x0059e422 */
        "cmp r0, #0x1e\n"
        ".hword 0xf000, 0x8586\n" /* beq.w 0x0059e45e */
        "cmp r0, #0x21\n"
        ".hword 0xf000, 0x8591\n" /* beq.w 0x0059e47a */
        ".hword 0xe1e1\n"        /* b 0x0059dd1e */
        ".hword 0xe1e0\n"        /* b 0x0059dd1e */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #8]\n"
        "cmp r0, #0\n"
        ".hword 0xd04f\n"        /* beq 0x0059da0a */
        "uxtb r1, r1\n"
        "cmp r1, #1\n"
        "bne 1f\n"
        "movs r7, #1\n"
        "b 2f\n"
        "1:\n"
        "movs r7, #0\n"
        "2:\n"
        "movs r1, #0\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfaed\n" /* bl 0x0059ef58 */
        "mov r9, r0\n"
        "movs r1, #2\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfae8\n" /* bl 0x0059ef58 */
        "mov r10, r0\n"
        "movs r1, #4\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfae3\n" /* bl 0x0059ef58 */
        "mov r11, r0\n"
        "movs r1, #1\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfade\n" /* bl 0x0059ef58 */
        "subs.w r9, r10, r9\n"
        "subs.w r9, r9, r0\n"
        "mov r2, r9\n"
        "movs r1, #2\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfb08\n" /* bl 0x0059efbe */
        "movs r1, #3\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfad1\n" /* bl 0x0059ef58 */
        "subs.w r10, r11, r10\n"
        "subs.w r10, r10, r0\n"
        "mov r2, r10\n"
        "movs r1, #4\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfafb\n" /* bl 0x0059efbe */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd002\n"        /* beq 0x0059d9d6 */
        "ldr r0, [r6, #0x20]\n"
        "ldr r0, [r0]\n"
    );
}
