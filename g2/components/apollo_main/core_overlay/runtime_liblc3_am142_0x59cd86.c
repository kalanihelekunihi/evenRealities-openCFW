/*
 * Clean-room Thumb source for the AM142 0x0059cd86 stack-window update
 * fragment.  Calls to the shared interpolation helper, the outbound loop
 * branch, and the carried 32-bit-instruction boundary are kept explicit until
 * their neighboring AM142 spans are source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059cd86(void)
{
    __asm__ volatile(
        "uxtb.w r9, r9\n"
        "cmp.w r9, #0\n"
        "beq 1f\n"
        "ldr r1, [r7, #0x28]\n"
        "adds r0, r0, r1\n"
        "str r0, [r7, #0x30]\n"
        "ldr r0, [r5]\n"
        "str r0, [r7, #0x34]\n"
        "b 2f\n"
        "1:\n"
        "ldr r1, [r4]\n"
        "str r1, [r7, #0x30]\n"
        "ldr r1, [r7, #0x2c]\n"
        "adds r0, r0, r1\n"
        "str r0, [r7, #0x34]\n"
        "b 2f\n"
        "ldrb r0, [r7, #0xa]\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "mov r1, r8\n"
        "ldr r0, [sp, #0xc]\n"
        ".hword 0xf002, 0xf8d1\n" /* bl 0x0059ef58 */
        "adds.w r8, r8, #1\n"
        "add r1, sp, #0x10\n"
        "ldr r2, [r1, #0x28]\n"
        "adds r0, r0, r2\n"
        "str r0, [r1, #0x30]\n"
        "b 4f\n"
        "3:\n"
        "ldr r0, [r4]\n"
        "str r0, [sp, #0x40]\n"
        "4:\n"
        "ldrb r0, [r7, #0xb]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "add r7, sp, #0x10\n"
        "ldr.w r9, [r7, #0x2c]\n"
        "mov r1, r8\n"
        "ldr r0, [sp, #0xc]\n"
        ".hword 0xf002, 0xf8be\n" /* bl 0x0059ef58 */
        "adds.w r9, r0, r9\n"
        "str.w r9, [r7, #0x34]\n"
        "b 2f\n"
        "5:\n"
        "ldr r0, [r5]\n"
        "str r0, [sp, #0x44]\n"
        "2:\n"
        "movs r7, #0\n"
        ".hword 0xe02b\n"        /* b 0x0059ce46 */
        "movs r0, #6\n"
        "add r1, sp, #0x10\n"
        "mul r2, r0, r7\n"
        "add.w r1, r1, r2, lsl #2\n"
        "ldr r1, [r1, #0x1c]\n"
        "str r1, [sp, #8]\n"
        "add r1, sp, #0x10\n"
        "mul r2, r0, r7\n"
        "add.w r1, r1, r2, lsl #2\n"
        "ldr r1, [r1, #0x18]\n"
        "str r1, [sp, #4]\n"
        "add r1, sp, #0x10\n"
        "mul r2, r0, r7\n"
        "add.w r1, r1, r2, lsl #2\n"
        "ldr r1, [r1, #0x14]\n"
        "str r1, [sp]\n"
        "add r1, sp, #0x10\n"
        ".hword 0xfb00\n"        /* first halfword of trailing 32-bit mul */
    );
}
