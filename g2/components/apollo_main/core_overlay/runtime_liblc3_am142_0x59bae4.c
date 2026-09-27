/*
 * Clean-room Thumb source for the AM142 0x0059bae4 mixed search/encoder span.
 * Branches, vector instructions, indirect transfers, and cross-span calls remain
 * explicit reviewed halfwords until adjacent AM142 control-flow is source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059bae4(void)
{
    __asm__ volatile(
        "adds r0, #0x1c\n"
        ".hword 0xf7ff, 0xfdce\n" /* bl #0x59b686 */
        "cmp r0, #0\n"
        ".hword 0xf040, 0x809b\n" /* bne.w #0x59bc26 */
        "ldr r0, [r5, #4]\n"
        ".hword 0xf7ff, 0xfe0a\n" /* bl #0x59b70a */
        "cmp r0, #0\n"
        ".hword 0xd02a\n" /* beq #0x59bb50 */
        "movs r0, r7\n"
        ".hword 0xf7ff, 0xfddb\n" /* bl #0x59b6b6 */
        "cmp r0, #0\n"
        ".hword 0xd125\n" /* bne #0x59bb50 */
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd01c\n" /* beq #0x59bb46 */
        "ldr.w r1, [r8, #8]\n"
        "ldr r0, [r7, #8]\n"
        "adds r1, r0, r1\n"
        "movs r0, #2\n"
        "sdiv r1, r1, r0\n"
        "ldr r0, [r5, #4]\n"
        ".hword 0xf7ff, 0xfdf8\n" /* bl #0x59b710 */
        "mov r9, r0\n"
        "ldr r1, [r5, #0x10]\n"
        "ldr.w r2, [r8, #8]\n"
        "ldr r0, [r7, #8]\n"
        "subs r2, r2, r0\n"
        "movs r0, #2\n"
        "sdiv r0, r2, r0\n"
        ".hword 0xf750, 0xfdf1\n" /* bl #0x4ec718 */
        "subs.w r1, r9, r0\n"
        "str r1, [r7, #0xc]\n"
        "adds.w r9, r0, r9\n"
        "str.w r9, [r8, #0xc]\n"
        ".hword 0xe004\n" /* b #0x59bb50 */
        "ldr r1, [r7, #8]\n"
        "ldr r0, [r5, #4]\n"
        ".hword 0xf7ff, 0xfde1\n" /* bl #0x59b710 */
        "str r0, [r7, #0xc]\n"
        "cmp r4, #0\n"
        ".hword 0xd007\n" /* beq #0x59bb64 */
        "ldr r0, [r7, #0xc]\n"
        "movs r1, #0x14\n"
        "mul r1, r1, r4\n"
        "add r1, r5\n"
        "ldr r1, [r1, #0x14]\n"
        "cmp r0, r1\n"
        ".hword 0xdb60\n" /* blt #0x59bc26 */
        "ldr r0, [r5, #0x14]\n"
        "cmp r4, r0\n"
        ".hword 0xd215\n" /* bhs #0x59bb96 */
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd009\n" /* beq #0x59bb86 */
        "movs r0, #0x14\n"
        "mul r0, r0, r4\n"
        "add r0, r5\n"
        "ldr r0, [r0, #0x28]\n"
        "ldr.w r1, [r8, #0xc]\n"
        "cmp r0, r1\n"
        ".hword 0xda08\n" /* bge #0x59bb96 */
        ".hword 0xe04f\n" /* b #0x59bc26 */
        "movs r0, #0x14\n"
        "mul r0, r0, r4\n"
        "add r0, r5\n"
        "ldr r0, [r0, #0x28]\n"
        "ldr r1, [r7, #0xc]\n"
        "cmp r0, r1\n"
        ".hword 0xdb47\n" /* blt #0x59bc26 */
        "ldr.w r9, [r5, #0x14]\n"
        "subs.w r9, r9, #1\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd004\n" /* beq #0x59bbb0 */
        "ldr.w r10, [r5, #0x14]\n"
        "adds.w r10, r10, #1\n"
        ".hword 0xe001\n" /* b #0x59bbb4 */
        "ldr.w r10, [r5, #0x14]\n"
        "ldr.w r11, [r5, #0x14]\n"
        "subs.w r11, r11, r4\n"
        "cmp.w r10, #0xc0\n"
        ".hword 0xd310\n" /* blo #0x59bbe4 */
        ".hword 0xe030\n" /* b #0x59bc26 */
        "movs r1, #0x14\n"
        "mul r0, r1, r10\n"
        "add r0, r5\n"
        "adds r0, #0x1c\n"
        "mul r1, r1, r9\n"
        "add r1, r5\n"
        "adds r1, #0x1c\n"
        "movs r2, #0x14\n"
        ".hword 0xf666, 0xf824\n" /* bl #0x401c24 */
        "subs.w r9, r9, #1\n"
        "subs.w r10, r10, #1\n"
        "mov r0, r11\n"
        "subs.w r11, r0, #1\n"
        "cmp r0, #0\n"
        ".hword 0xd1ea\n" /* bne #0x59bbc4 */
        "movs.w r9, #0x14\n"
        "mul r0, r9, r4\n"
        "add r0, r5\n"
        "adds r0, #0x1c\n"
        "movs r1, r7\n"
        "movs r2, #0x14\n"
        ".hword 0xf666, 0xf811\n" /* bl #0x401c24 */
        "ldr r0, [r5, #0x14]\n"
        "adds r0, r0, #1\n"
        "str r0, [r5, #0x14]\n"
        "uxtb r6, r6\n"
        "cmp r6, #0\n"
        ".hword 0xd00b\n" /* beq #0x59bc26 */
        "mul r4, r9, r4\n"
        "add.w r0, r5, r4\n"
        "adds r0, #0x30\n"
        "mov r1, r8\n"
        "movs r2, #0x14\n"
        ".hword 0xf666, 0xf802\n" /* bl #0x401c24 */
        "ldr r0, [r5, #0x14]\n"
        "adds r0, r0, #1\n"
        "str r0, [r5, #0x14]\n"
        "pop.w {r0, r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "push.w {r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "sub sp, #0xa8\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "mov r8, r2\n"
        "movs r6, r3\n"
        "ldr.w r11, [sp, #0xd4]\n"
        "ldr r7, [r4]\n"
        "mov r0, r11\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd112\n" /* bne #0x59bc6c */
        "ldr r0, [r4, #4]\n"
        ".hword 0xf7ff, 0xfd5f\n" /* bl #0x59b70a */
        "cmp r0, #0\n"
        ".hword 0xd10d\n" /* bne #0x59bc6c */
        "ldr r1, [r6]\n"
        "add r0, sp, #0x8c\n"
        ".hword 0xf000, 0xff63\n" /* bl #0x59cb1e */
        "movs r0, #1\n"
        "str r0, [sp, #4]\n"
        "ldr r0, [sp, #0xd0]\n"
        "str r0, [sp]\n"
        "add r3, sp, #0x8c\n"
        "mov r2, r8\n"
        "movs r1, r5\n"
        "ldr r0, [r4, #4]\n"
        ".hword 0xf7ff, 0xffdf\n" /* bl #0x59bc2a */
        "movs r0, r6\n"
        ".hword 0xf000, 0xff61\n" /* bl #0x59cb34 */
        "cmp r0, #0\n"
        ".hword 0xd11a\n" /* bne #0x59bcac */
        "movs r0, r5\n"
        ".hword 0xf7fe, 0xfbab\n" /* bl #0x59a3d2 */
        "mov r9, r0\n"
        "mov r0, r8\n"
        ".hword 0xf7fe, 0xfba7\n" /* bl #0x59a3d2 */
        "adds.w r9, r0, r9\n"
        "mov r1, r9\n"
        "movs r0, r6\n"
        ".hword 0xf000, 0xff84\n" /* bl #0x59cb98 */
        "movs r0, r6\n"
        ".hword 0xf000, 0xff4f\n" /* bl #0x59cb34 */
        "cmp r0, #0\n"
        ".hword 0xd108\n" /* bne #0x59bcac */
        "ldrb r0, [r7, #8]\n"
        "cmp r0, #0\n"
        ".hword 0xd004\n" /* beq #0x59bcaa */
        "movs r0, #0\n"
        "ldr r1, [r6]\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "strb r0, [r4, #0xd]\n"
        ".hword 0xe11e\n" /* b #0x59beea */
        "movs r0, #0\n"
        "str r0, [r4, #0x14]\n"
        "movs r0, #0\n"
        "str r0, [r4, #0x18]\n"
        "add r0, sp, #0x8c\n"
        "movs r1, r6\n"
        "movs r2, #0x1c\n"
        ".hword 0xf665, 0xffb3\n" /* bl #0x401c24 */
        "add r0, sp, #0x8c\n"
        ".hword 0xf000, 0xff3e\n" /* bl #0x59cb40 */
        "mov r8, r0\n"
        "movs r0, r5\n"
        ".hword 0xf7fe, 0xfb83\n" /* bl #0x59a3d2 */
        "str r0, [sp, #0xc]\n"
        "ldr r0, [r6, #8]\n"
        "ldr r1, [sp, #0xc]\n"
        "cmp r0, r1\n"
        ".hword 0xf0c0, 0x8109\n" /* blo.w #0x59beea */
        "ldrb.w r0, [r7, #0xf9]\n"
        "cmp r0, #0\n"
        ".hword 0xd00e\n" /* beq #0x59bcfe */
        "add r0, sp, #0x78\n"
        ".hword 0xf7ff, 0xfcb7\n" /* bl #0x59b654 */
        "add r2, sp, #0x78\n"
        "adds.w r1, r7, #0x120\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfeac\n" /* bl #0x59ba4a */
        "adds.w r2, r7, #0x10c\n"
        "add r1, sp, #0x78\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfea6\n" /* bl #0x59ba4a */
        "movs.w r9, #0\n"
        "movs.w r10, #0x80\n"
        ".hword 0xe048\n" /* b #0x59bd9a */
        "uxtb.w r10, r10\n"
        "lsrs.w r10, r10, #1\n"
        ".hword 0xe041\n" /* b #0x59bd96 */
        "ldrb.w r1, [r8]\n"
        "tst.w r10, r1\n"
        ".hword 0xd034\n" /* beq #0x59bd86 */
        "movs r0, #1\n"
        "str r0, [sp, #8]\n"
        "ldr r0, [r4, #0x10]\n"
        "str r0, [sp, #4]\n"
        "ldr r0, [sp, #0xd0]\n"
        "str r0, [sp]\n"
        "movs r3, r7\n"
        "mov r2, r9\n"
        "movs r1, r5\n"
        "add r0, sp, #0x28\n"
        ".hword 0xf7ff, 0xfc18\n" /* bl #0x59b564 */
        "movs r0, #0\n"
        "str r0, [sp, #8]\n"
        "ldr r0, [r4, #0x10]\n"
        "str r0, [sp, #4]\n"
        "ldr r0, [sp, #0xd0]\n"
        "str r0, [sp]\n"
        "movs r3, r7\n"
        "mov r2, r9\n"
        "movs r1, r5\n"
        "add r0, sp, #0x14\n"
        ".hword 0xf7ff, 0xfc0c\n" /* bl #0x59b564 */
        "add r0, sp, #0x28\n"
        ".hword 0xf7ff, 0xfcb2\n" /* bl #0x59b6b6 */
        "cmp r0, #0\n"
        ".hword 0xd10c\n" /* bne #0x59bd70 */
        "add r0, sp, #0x14\n"
        ".hword 0xf7ff, 0xfcad\n" /* bl #0x59b6b6 */
        "cmp r0, #0\n"
        ".hword 0xd107\n" /* bne #0x59bd70 */
        "add r2, sp, #0x14\n"
        "add r1, sp, #0x28\n"
        "adds.w r0, r7, #0xf0\n"
        ".hword 0xf7fe, 0xfd6e\n" /* bl #0x59a848 */
        "cmp r0, #0\n"
        ".hword 0xd00a\n" /* beq #0x59bd86 */
        "add r2, sp, #0x14\n"
        "add r1, sp, #0x28\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfe68\n" /* bl #0x59ba4a */
        "ldrb.w r0, [r8]\n"
        ".hword 0xea30, 0x000a\n" /* bics.w r0, r0, sl */
        "strb.w r0, [r8]\n"
        "ands r0, r9, #7\n"
        "cmp r0, #7\n"
        ".hword 0xd1bc\n" /* bne #0x59bd08 */
        "adds.w r8, r8, #1\n"
        "movs.w r10, #0x80\n"
        "adds.w r9, r9, #1\n"
        "ldr r0, [sp, #0xc]\n"
        "cmp r9, r0\n"
        ".hword 0xd3b8\n" /* blo #0x59bd12 */
        "mov r0, r11\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        ".hword 0xd02c\n" /* beq #0x59be02 */
        "ldr r0, [r4, #0x14]\n"
        "cmp r0, #0\n"
        ".hword 0xd00a\n" /* beq #0x59bdc4 */
        "ldr r0, [r4, #0x24]\n"
        "cmp r0, #1\n"
        ".hword 0xda07\n" /* bge #0x59bdc4 */
        "ldr r1, [r4, #0x14]\n"
        "movs r0, #0x14\n"
        "muls r1, r0, r1\n"
        "add.w r0, r4, r1\n"
        "ldr r0, [r0, #0x10]\n"
        "cmp r0, #0\n"
        ".hword 0xd50e\n" /* bpl #0x59bde2 */
        "mov r0, sp\n"
        ".hword 0xf7ff, 0xfc45\n" /* bl #0x59b654 */
        "movs r0, #0x31\n"
        "str r0, [sp]\n"
        "ldr r0, [r4, #0x10]\n"
        "str r0, [sp, #0x10]\n"
        "add r0, sp, #0x64\n"
        ".hword 0xf7ff, 0xfc3e\n" /* bl #0x59b654 */
        "add r2, sp, #0x64\n"
        "mov r1, sp\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfe34\n" /* bl #0x59ba4a */
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfc93\n" /* bl #0x59b70e */
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfcd7\n" /* bl #0x59b79c */
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfc8d\n" /* bl #0x59b70e */
        "uxtb.w r11, r11\n"
        "cmp.w r11, #0\n"
        ".hword 0xd16f\n" /* bne #0x59bede */
        "movs r7, #0\n"
        ".hword 0xe06a\n" /* b #0x59bed8 */
        "add r0, sp, #0x8c\n"
        ".hword 0xf000, 0xfe9c\n" /* bl #0x59cb40 */
        "mov r8, r0\n"
        "movs.w r9, #0\n"
        "movs.w r10, #0x80\n"
        ".hword 0xe004\n" /* b #0x59be1e */
        "uxtb.w r10, r10\n"
        "lsrs.w r10, r10, #1\n"
        ".hword 0xe02c\n" /* b #0x59be78 */
        "ldr r0, [sp, #0xc]\n"
        "cmp r9, r0\n"
        ".hword 0xd2de\n" /* bhs #0x59bde2 */
        "ldrb.w r1, [r8]\n"
        "tst.w r10, r1\n"
        ".hword 0xd01c\n" /* beq #0x59be68 */
        "movs r0, #1\n"
        "str r0, [sp, #8]\n"
        "ldr r0, [r4, #0x10]\n"
        "str r0, [sp, #4]\n"
        "ldr r0, [sp, #0xd0]\n"
        "str r0, [sp]\n"
        "movs r3, r7\n"
        "mov r2, r9\n"
        "movs r1, r5\n"
        "add r0, sp, #0x50\n"
        ".hword 0xf7ff, 0xfb8f\n" /* bl #0x59b564 */
        "movs r0, #0\n"
        "str r0, [sp, #8]\n"
        "ldr r0, [r4, #0x10]\n"
        "str r0, [sp, #4]\n"
        "ldr r0, [sp, #0xd0]\n"
        "str r0, [sp]\n"
        "movs r3, r7\n"
        "mov r2, r9\n"
        "movs r1, r5\n"
        "add r0, sp, #0x3c\n"
        ".hword 0xf7ff, 0xfb83\n" /* bl #0x59b564 */
        "add r2, sp, #0x3c\n"
        "add r1, sp, #0x50\n"
        "movs r0, r4\n"
        ".hword 0xf7ff, 0xfdf1\n" /* bl #0x59ba4a */
        "ands r0, r9, #7\n"
        "cmp r0, #7\n"
        ".hword 0xd1d1\n" /* bne #0x59be14 */
        "adds.w r8, r8, #1\n"
        "movs.w r10, #0x80\n"
        "adds.w r9, r9, #1\n"
        ".hword 0xe7cf\n" /* b #0x59be1e */
        "mul r8, r8, r7\n"
        "add.w r0, r4, r8\n"
        "ldr r0, [r0, #0x28]\n"
        "str.w r0, [r9, #0xc]\n"
        ".hword 0xe020\n" /* b #0x59bed0 */
        "movs.w r8, #0x14\n"
        "mul r0, r8, r7\n"
        "add r0, r4\n"
        "adds r0, #0x1c\n"
        ".hword 0xf7ff, 0xfc12\n" /* bl #0x59b6c2 */
        "cmp r0, #0\n"
        ".hword 0xd119\n" /* bne #0x59bed6 */
        "mul r0, r8, r7\n"
        "add r0, r4\n"
        "ldr r1, [r0, #0x20]\n"
        "movs r0, r5\n"
        ".hword 0xf7fe, 0xfa95\n" /* bl #0x59a3da */
        "mov r9, r0\n"
        "mul r0, r8, r7\n"
        "add r0, r4\n"
        "adds r0, #0x1c\n"
        ".hword 0xf7ff, 0xfbea\n" /* bl #0x59b692 */
        "cmp r0, #0\n"
        ".hword 0xd0dd\n" /* beq #0x59be7e */
        "mul r8, r8, r7\n"
        "add.w r0, r4, r8\n"
        "ldr r0, [r0, #0x28]\n"
        "str.w r0, [r9, #0x10]\n"
        "movs r0, #1\n"
        "strb.w r0, [r9]\n"
        "adds r7, r7, #1\n"
        "ldr r0, [r4, #0x14]\n"
        "cmp r7, r0\n"
        ".hword 0xd3d7\n" /* blo #0x59be8e */
        "movs r0, #1\n"
        "strb r0, [r4, #0xc]\n"
        "movs r1, #0\n"
        "movs r0, r6\n"
        ".hword 0xf000, 0xfe29\n" /* bl #0x59cb3c */
        "add sp, #0xac\n"
        "pop.w {r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "push.w {r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "mov r11, r2\n"
        "ldr.w r10, [sp, #0x30]\n"
        "ldr r6, [sp, #0x34]\n"
        "ldr r7, [sp, #0x38]\n"
        "ldr.w r8, [sp, #0x3c]\n"
        "ldr.w r9, [sp, #0x40]\n"
        "movw r1, #0x2e08\n"
        "movs r2, #0\n"
        "str r4, [sp]\n"
        "ldr r0, [sp]\n"
        ".hword 0xf668, 0xf8f6\n" /* bl #0x404104 */
        "ldr r0, [sp]\n"
        "str r5, [r4]\n"
        "str.w r11, [r4, #4]\n"
        "movw r11, #0x2d5c\n"
        "movs r3, #8\n"
        "adds r2, r5, #4\n"
        "ldr r1, [r5]\n"
        "add.w r0, r4, r11\n"
        ".hword 0xf7fe, 0xf9f0\n" /* bl #0x59a312 */
        "ldr r0, [sp, #8]\n"
        "str r0, [sp]\n"
        "add.w r3, r4, r11\n"
        "adds.w r2, r4, #0x1e40\n"
        "movs r1, r5\n"
        "adds.w r0, r4, #0x1e40\n"
        ".hword 0xf7ff, 0xfbc8\n" /* bl #0x59b6d8 */
        "ldr r0, [sp, #8]\n"
        "str r0, [sp]\n"
        "add.w r3, r4, r11\n"
        "adds.w r2, r4, #0x1e40\n"
        "movs r1, r5\n"
        "addw r0, r4, #0xf24\n"
        ".hword 0xf7ff, 0xfbbd\n" /* bl #0x59b6d8 */
        "ldr r0, [sp, #8]\n"
        "str r0, [sp]\n"
        "add.w r3, r4, r11\n"
        "adds.w r2, r4, #0x1e40\n"
        "movs r1, r5\n"
        "adds.w r0, r4, #8\n"
        ".hword 0xf7ff, 0xfbb2\n" /* bl #0x59b6d8 */
        "ldr r0, [r5, #0x28]\n"
        "movw r1, #0x2d7c\n"
        "str r0, [r4, r1]\n"
        "ldr r0, [r5, #0x30]\n"
        "adds.w r1, r4, #0x2d80\n"
        "str r0, [r1]\n"
        "ldr r0, [r5, #0x34]\n"
        "movw r1, #0x2d84\n"
        "str r0, [r4, r1]\n"
        "ldr r2, [sp, #0x44]\n"
        "ldrd r0, r1, [r2]\n"
        "movw r2, #0x2d88\n"
        "add r2, r4\n"
        "strd r0, r1, [r2]\n"
        "movw r0, #0x2d94\n"
        "str.w r10, [r4, r0]\n"
        "movw r0, #0x2d98\n"
        "str r6, [r4, r0]\n"
        "movw r0, #0x2d9c\n"
        "str r7, [r4, r0]\n"
        "movw r0, #0x2da0\n"
        "str.w r8, [r4, r0]\n"
        "movw r0, #0x2da4\n"
        "str.w r9, [r4, r0]\n"
        "ldrb.w r0, [r5, #0xb9]\n"
        "movw r1, #0x2d92\n"
        "strb r0, [r4, r1]\n"
        "movw r0, #0x2da8\n"
        "ldr.w r1, [r5, #0xe4]\n"
        "str r1, [r4, r0]\n"
        "movw r1, #0x2dac\n"
        "ldr.w r2, [r5, #0xe8]\n"
        "str r2, [r4, r1]\n"
        "ldr r2, [r4, r1]\n"
        "cmp r2, #0\n"
        ".hword 0xd502\n" /* bpl #0x59bfea */
        "ldr r2, [r4, r1]\n"
        "rsbs r2, r2, #0\n"
        ".hword 0xe000\n" /* b #0x59bfec */
        "ldr r2, [r4, r1]\n"
        "ldr r3, [r4, r0]\n"
        "cmp r3, #0\n"
        ".hword 0xd502\n" /* bpl #0x59bff8 */
        "ldr r3, [r4, r0]\n"
        "rsbs r3, r3, #0\n"
        ".hword 0xe000\n" /* b #0x59bffa */
        "ldr r3, [r4, r0]\n"
        "cmp r2, r3\n"
        ".hword 0xda07\n" /* bge #0x59c00e */
        "ldr r1, [r4, r0]\n"
        "cmp r1, #0\n"
        ".hword 0xd502\n" /* bpl #0x59c00a */
        "ldr r0, [r4, r0]\n"
        "rsbs r0, r0, #0\n"
        ".hword 0xe008\n" /* b #0x59c01c */
        "ldr r0, [r4, r0]\n"
        ".hword 0xe006\n" /* b #0x59c01c */
        "ldr r0, [r4, r1]\n"
        "cmp r0, #0\n"
        ".hword 0xd502\n" /* bpl #0x59c01a */
        "ldr r0, [r4, r1]\n"
        "rsbs r0, r0, #0\n"
        ".hword 0xe000\n" /* b #0x59c01c */
        "ldr r0, [r4, r1]\n"
        "lsls r0, r0, #1\n"
        "movw r1, #0x2db0\n"
        "str r0, [r4, r1]\n"
        "movw r0, #0x199a\n"
        "movw r1, #0x2db4\n"
        "str r0, [r4, r1]\n"
        "movs r0, #1\n"
        "movw r1, #0x2d93\n"
        "strb r0, [r4, r1]\n"
        "movs r0, #0\n"
        "movw r1, #0x2d90\n"
        "strb r0, [r4, r1]\n"
        "movs r0, #0\n"
        "movw r1, #0x2d91\n"
        "strb r0, [r4, r1]\n"
        "movs r0, #0\n"
        "movw r1, #0x2de0\n"
        "strb r0, [r4, r1]\n"
        "pop.w {r0, r1, r2, r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "push {r7, lr}\n"
        "movw r1, #0x2d5c\n"
        "add r0, r1\n"
        ".hword 0xf7fe, 0xf968\n" /* bl #0x59a32e */
        "pop {r0, pc}\n"
        "push.w {r2, r3, r4, r5, r6, r7, r8, lr}\n"
        "movs r5, r0\n"
        "movs r6, r1\n"
        "movs r4, r2\n"
        "ldr r7, [sp, #0x20]\n"
        "movs r1, r3\n"
        "movw r0, #0x2d7c\n"
        "ldr r0, [r5, r0]\n"
        ".hword 0xf750, 0xfb50\n" /* bl #0x4ec718 */
        "mov r8, r0\n"
        "movs r1, r7\n"
        "adds.w r0, r5, #0x2d80\n"
        "ldr r0, [r0]\n"
        ".hword 0xf750, 0xfb49\n" /* bl #0x4ec718 */
        "adds.w r8, r0, r8\n"
        "str.w r8, [sp]\n"
        "movs r1, r7\n"
        "movs r0, r6\n"
        ".hword 0xf7ff, 0xfb3d\n" /* bl #0x59b710 */
        "str r0, [sp, #4]\n"
        "ldr r1, [sp]\n"
        "ldr r0, [r5]\n"
        "ldr r0, [r0, #0x40]\n"
        ".hword 0xf750, 0xfb3b\n" /* bl #0x4ec718 */
        "movs r6, r0\n"
        "ldr r1, [sp, #4]\n"
        "ldr r0, [r5]\n"
        "ldr r0, [r0, #0x48]\n"
        ".hword 0xf750, 0xfb35\n" /* bl #0x4ec718 */
        "adds r6, r0, r6\n"
        "movw r0, #0x2d88\n"
        "ldr r0, [r5, r0]\n"
        "adds r6, r0, r6\n"
        "str r6, [r4]\n"
        "ldr r1, [sp]\n"
        "ldr r0, [r5]\n"
        "ldr r0, [r0, #0x44]\n"
        ".hword 0xf750, 0xfb2a\n" /* bl #0x4ec718 */
        "movs r6, r0\n"
        "ldr r1, [sp, #4]\n"
        "ldr r0, [r5]\n"
        "ldr r0, [r0, #0x4c]\n"
        ".hword 0xf750, 0xfb24\n" /* bl #0x4ec718 */
        "adds r6, r0, r6\n"
        "movw r0, #0x2d8c\n"
        "ldr r0, [r5, r0]\n"
        "adds r6, r0, r6\n"
        "str r6, [r4, #4]\n"
        "pop.w {r0, r1, r4, r5, r6, r7, r8, pc}\n"
        "push.w {r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "sub sp, #0x18\n"
        "movs r5, r0\n"
        "movs r6, r1\n"
        "movs r7, r2\n"
        "mov r8, r3\n"
        "ldr.w r9, [sp, #0x40]\n"
        "ldr r1, [r7]\n"
        "ldr r0, [r6]\n"
        "subs r1, r1, r0\n"
        "adds r1, #0x10\n"
        "asrs r1, r1, #5\n"
        "str r1, [sp, #8]\n"
        "ldr r1, [r7, #4]\n"
        "ldr r0, [r6, #4]\n"
        "subs r1, r1, r0\n"
        "adds r1, #0x10\n"
        "asrs r1, r1, #5\n"
        "str r1, [sp, #0xc]\n"
        "ldr.w r1, [r9]\n"
        "ldr.w r0, [r8]\n"
        "subs r1, r1, r0\n"
        "adds r1, #0x10\n"
        "asrs r1, r1, #5\n"
        "str r1, [sp]\n"
        "ldr.w r1, [r9, #4]\n"
        "ldr.w r0, [r8, #4]\n"
        "subs r1, r1, r0\n"
        "adds r1, #0x10\n"
        "asrs r1, r1, #5\n"
        "str r1, [sp, #4]\n"
        "ldr.w r1, [r8]\n"
        "ldr r0, [r6]\n"
        "subs r1, r1, r0\n"
        "adds r1, #0x10\n"
        "asrs r1, r1, #5\n"
        "str r1, [sp, #0x10]\n"
        "ldr.w r1, [r8, #4]\n"
        "ldr r0, [r6, #4]\n"
        "subs r1, r1, r0\n"
        "adds r1, #0x10\n"
        "asrs r1, r1, #5\n"
        "str r1, [sp, #0x14]\n"
        "ldr r1, [sp, #4]\n"
        "ldr r0, [sp, #8]\n"
        ".hword 0xf750, 0xfae5\n" /* bl #0x4ec718 */
        "movs r4, r0\n"
        "ldr r1, [sp]\n"
        "ldr r0, [sp, #0xc]\n"
        ".hword 0xf750, 0xfae0\n" /* bl #0x4ec718 */
        "subs r4, r4, r0\n"
        "cmp r4, #0\n"
        ".hword 0xd101\n" /* bne #0x59c162 */
        "movs r0, #0\n"
        ".hword 0xe0ea\n" /* b #0x59c338 */
        "ldr.w r10, [sp, #0x44]\n"
    );
}
