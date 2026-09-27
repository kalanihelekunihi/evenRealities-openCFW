/*
 * Clean-room Thumb source for the AM142 0x0059b852 mixed candidate-search span.
 * Branches and cross-span calls remain explicit reviewed halfwords until the
 * surrounding AM142 control-flow graph is fully source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b852(void)
{
    __asm__ volatile(
        ".hword 0xf750, 0xff8f\n" /* bl #0x4ec774 */
        "mul r1, r8, r4\n"
        "add r1, r6\n"
        "str r0, [r1, #0x18]\n"
        "uxtb.w r9, r9\n"
        "cmp.w r9, #0\n"
        ".hword 0xd023\n" /* beq #0x59b8b0 */
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x24]\n"
        "mul r1, r8, r7\n"
        "add r1, r6\n"
        "ldr r1, [r1, #0x10]\n"
        "cmp r0, r1\n"
        ".hword 0xd018\n" /* beq #0x59b8ae */
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "ldr r1, [r0, #0x24]\n"
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x10]\n"
        "subs r1, r1, r0\n"
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x28]\n"
        "mul r2, r8, r7\n"
        "add r2, r6\n"
        "ldr r2, [r2, #0x14]\n"
        "subs r0, r0, r2\n"
        ".hword 0xf750, 0xff68\n" /* bl #0x4ec774 */
        "mul r7, r8, r7\n"
        "add.w r1, r6, r7\n"
        "str r0, [r1, #0x18]\n"
        "adds r4, r4, #1\n"
        "adds r4, r4, #1\n"
        "ldr r0, [r6, #0x14]\n"
        "cmp r4, r0\n"
        ".hword 0xf080, 0x8089\n" /* bhs.w #0x59b9cc */
        "movs.w r8, #0x14\n"
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "adds r0, #0x1c\n"
        ".hword 0xf7ff, 0xfed5\n" /* bl #0x59b674 */
        "mov r9, r0\n"
        "mov r0, r9\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd001\n" /* beq #0x59b8d8 */
        "adds r7, r4, #1\n"
        ".hword 0xe000\n" /* b #0x59b8da */
        "movs r7, r4\n"
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "adds r0, #0x1c\n"
        ".hword 0xf7ff, 0xfee8\n" /* bl #0x59b6b6 */
        "cmp r0, #0\n"
        ".hword 0xd195\n" /* bne #0x59b816 */
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x28]\n"
        "mul r1, r8, r4\n"
        "add r1, r6\n"
        "ldr r1, [r1, #0x28]\n"
        ".hword 0xf36f, 0x010f\n" /* bfc r1, #0, #0x10 */
        "subs r0, r0, r1\n"
        "mul r1, r8, r7\n"
        "add r1, r6\n"
        "ldr r5, [r1, #0x28]\n"
        "mul r1, r8, r7\n"
        "add r1, r6\n"
        "ldr r1, [r1, #0x28]\n"
        ".hword 0xf36f, 0x010f\n" /* bfc r1, #0, #0x10 */
        "subs r5, r5, r1\n"
        "rsbs r1, r0, #0\n"
        "rsbs r2, r5, #0\n"
        "cmp r0, #0\n"
        ".hword 0xd101\n" /* bne #0x59b922 */
        "movs r0, #0\n"
        ".hword 0xe001\n" /* b #0x59b926 */
        "rsbs.w r0, r0, #0x10000\n"
        "cmp r5, #0\n"
        ".hword 0xd101\n" /* bne #0x59b92e */
        "movs r5, #0\n"
        ".hword 0xe001\n" /* b #0x59b932 */
        "rsbs.w r5, r5, #0x10000\n"
        "cmp r0, r5\n"
        ".hword 0xda01\n" /* bge #0x59b93a */
        "movs r5, r0\n"
        ".hword 0xe7ff\n" /* b #0x59b93a */
        "cmp r2, r1\n"
        ".hword 0xdb00\n" /* blt #0x59b940 */
        "movs r1, r2\n"
        "mov.w r3, #0x8000\n"
        "movs r2, r3\n"
        "movs r0, #0\n"
        "ldr.w ip, [r6, #0x14]\n"
        "subs.w ip, ip, #1\n"
        "cmp r7, ip\n"
        ".hword 0xd20f\n" /* bhs #0x59b974 */
        "mul ip, r8, r7\n"
        "add ip, r6\n"
        "ldr.w ip, [ip, #0x3c]\n"
        "mul lr, r8, r7\n"
        "add lr, r6\n"
        "ldr.w lr, [lr, #0x28]\n"
        "adds.w lr, r5, lr\n"
        "adds.w r3, r3, lr\n"
        "cmp ip, r3\n"
        ".hword 0xdb16\n" /* blt #0x59b9a2 */
        "cmp r4, #0\n"
        ".hword 0xd00b\n" /* beq #0x59b990 */
        "mul r3, r8, r4\n"
        "add r3, r6\n"
        "ldr r3, [r3, #0x28]\n"
        "adds r3, r1, r3\n"
        "subs r2, r3, r2\n"
        "mul r3, r8, r4\n"
        "add r3, r6\n"
        "ldr r3, [r3, #0x14]\n"
        "cmp r2, r3\n"
        ".hword 0xdb06\n" /* blt #0x59b99e */
        "rsbs r2, r1, #0\n"
        "cmp r2, r5\n"
        ".hword 0xda01\n" /* bge #0x59b99a */
        "mov r10, r1\n"
        ".hword 0xe70d\n" /* b #0x59b7b6 */
        "mov r10, r5\n"
        ".hword 0xe70b\n" /* b #0x59b7b6 */
        "mov r10, r5\n"
        ".hword 0xe709\n" /* b #0x59b7b6 */
        "cmp r4, #0\n"
        ".hword 0xd00c\n" /* beq #0x59b9c0 */
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x28]\n"
        "adds r0, r1, r0\n"
        "subs r2, r0, r2\n"
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x14]\n"
        "cmp r2, r0\n"
        ".hword 0xf6ff, 0xaef6\n" /* blt.w #0x59b7ac */
        "mov r10, r1\n"
        "cmn r5, r1\n"
        ".hword 0xf6bf, 0xaef6\n" /* bge.w #0x59b7b4 */
        "movs r0, #1\n"
        ".hword 0xe6f4\n" /* b #0x59b7b6 */
        "ldr r0, [r6, #8]\n"
        ".hword 0xf7fe, 0xfd00\n" /* bl #0x59a3d2 */
        "movs r4, r0\n"
        ".hword 0xe035\n" /* b #0x59ba42 */
        "subs r1, r4, #1\n"
        "ldr r0, [r6, #8]\n"
        ".hword 0xf7fe, 0xfcfe\n" /* bl #0x59a3da */
        "mov r8, r0\n"
        "ldr.w r5, [r8]\n"
        "movs r7, #0x14\n"
        "mul r0, r7, r5\n"
        "add r0, r6\n"
        "ldr r1, [r0, #0x3c]\n"
        "mul r0, r7, r5\n"
        "add r0, r6\n"
        "ldr r2, [r0, #0x28]\n"
        "ldr.w r0, [r8, #4]\n"
        "adds r2, r0, r2\n"
        "adds.w r2, r2, #0x8000\n"
        "cmp r1, r2\n"
        ".hword 0xdb1d\n" /* blt #0x59ba40 */
        "mul r0, r7, r5\n"
        "add r0, r6\n"
        "ldr r1, [r0, #0x28]\n"
        "ldr.w r0, [r8, #4]\n"
        "adds r1, r0, r1\n"
        "mul r0, r7, r5\n"
        "add r0, r6\n"
        "str r1, [r0, #0x28]\n"
        "mul r0, r7, r5\n"
        "add r0, r6\n"
        "adds r0, #0x1c\n"
        ".hword 0xf7ff, 0xfe27\n" /* bl #0x59b674 */
        "cmp r0, #0\n"
        ".hword 0xd00a\n" /* beq #0x59ba40 */
        "mul r0, r7, r5\n"
        "add r0, r6\n"
        "ldr r1, [r0, #0x14]\n"
        "ldr.w r0, [r8, #4]\n"
        "adds r1, r0, r1\n"
        "muls r5, r7, r5\n"
        "add.w r0, r6, r5\n"
        "str r1, [r0, #0x14]\n"
        "subs r4, r4, #1\n"
        "cmp r4, #0\n"
        ".hword 0xd1c7\n" /* bne #0x59b9d6 */
        "pop.w {r0, r1, r4, r5, r6, r7, r8, r9, r10, pc}\n"
        "push.w {r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "movs r5, r0\n"
        "movs r4, r1\n"
        "mov r9, r2\n"
        "movs r6, #1\n"
        "movs r7, r4\n"
        "mov r8, r9\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfe02\n" /* bl #0x59b664 */
        "cmp r0, #0\n"
        ".hword 0xd102\n" /* bne #0x59ba6a */
        "mov r7, r9\n"
        "movs r6, #0\n"
        ".hword 0xe005\n" /* b #0x59ba76 */
        "mov r0, r9\n"
        ".hword 0xf7ff, 0xfdfa\n" /* bl #0x59b664 */
        "cmp r0, #0\n"
        ".hword 0xd100\n" /* bne #0x59ba76 */
        "movs r6, #0\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd005\n" /* beq #0x59ba8a */
        "ldr.w r0, [r9, #8]\n"
        "ldr r1, [r4, #8]\n"
        "cmp r0, r1\n"
        ".hword 0xf2c0, 0x80ce\n" /* blt.w #0x59bc26 */
        "movs r4, #0\n"
        ".hword 0xe000\n" /* b #0x59ba90 */
        "adds r4, r4, #1\n"
        "ldr r0, [r5, #0x14]\n"
        "cmp r4, r0\n"
        ".hword 0xd207\n" /* bhs #0x59baa6 */
    );
}
