/*
 * Clean-room Thumb source for the AM142 0x0059cf1a encoder finalization span.
 * Branches and cross-span helper calls remain explicit halfwords until adjacent
 * AM142 control-flow boundaries are source-routed.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059cf1a(void)
{
    __asm__ volatile(
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldr r5, [r0]\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldr r0, [r0, #0x34]\n"
        "str r0, [sp, #0x40]\n"
        "movs r0, r6\n"
        ".hword 0xf7fe, 0xfaf7\n" /* bl #0x59b520 */
        "str r0, [sp, #0x34]\n"
        "movs.w r8, #0\n"
        "movs r0, #0\n"
        "strb.w r0, [sp, #0x1a]\n"
        "movs r0, #0\n"
        "strb.w r0, [sp, #0x19]\n"
        "movs r0, #0\n"
        "str r0, [sp, #0x20]\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2f0]\n"
        "str r0, [sp, #0x24]\n"
        "movs r0, #0\n"
        "ldr.w r0, [pc, #0xc50]\n"
        "str r0, [sp, #0x38]\n"
        "movs r0, #0\n"
        "movs.w r0, #-1\n"
        "movs r1, #0x80\n"
        "movs r2, #0\n"
        "movw r9, #0x3e34\n"
        "add r9, sp, r9\n"
        "mov r0, r9\n"
        ".hword 0xf667, 0xf8ca\n" /* bl #0x404104 */
        "movs r1, #0xc\n"
        "movs r2, #0\n"
        "add.w r9, sp, #0xe8\n"
        "mov r0, r9\n"
        ".hword 0xf667, 0xf8c3\n" /* bl #0x404104 */
        "movs r1, #0x18\n"
        "movs r2, #0\n"
        "add.w r9, sp, #0xd0\n"
        "mov r0, r9\n"
        ".hword 0xf667, 0xf8bc\n" /* bl #0x404104 */
        "movs r3, #0x10\n"
        "ldr r2, [sp, #0x1c]\n"
        "movs r1, r5\n"
        "add r0, sp, #0xb0\n"
        ".hword 0xf7fd, 0xf9bd\n" /* bl #0x59a312 */
        "movs r3, #0x14\n"
        "ldr r2, [sp, #0x1c]\n"
        "movs r1, r5\n"
        "add r0, sp, #0x90\n"
        ".hword 0xf7fd, 0xf9b7\n" /* bl #0x59a312 */
        "movs r3, #0x14\n"
        "ldr r2, [sp, #0x1c]\n"
        "movs r1, r5\n"
        "add r0, sp, #0x70\n"
        ".hword 0xf7fd, 0xf9b1\n" /* bl #0x59a312 */
        "ldr r1, [sp, #0x1c]\n"
        "add r0, sp, #0x54\n"
        ".hword 0xf7ff, 0xfdb3\n" /* bl #0x59cb1e */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2c0]\n"
        "str r0, [sp, #0x14]\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "adds r0, #0xf0\n"
        "str r0, [sp, #0x10]\n"
        "ldr r0, [sp, #0x24]\n"
        "str r0, [sp, #0xc]\n"
        "add r0, sp, #0x54\n"
        "str r0, [sp, #8]\n"
        "add r0, sp, #0x70\n"
        "str r0, [sp, #4]\n"
        "add r0, sp, #0x90\n"
        "str r0, [sp]\n"
        "ldr r3, [sp, #0x40]\n"
        "add.w r2, sp, #0x3c00\n"
        "ldr.w r2, [r2, #0x2bc]\n"
        "add.w r1, sp, #0x3c00\n"
        "ldr.w r1, [r1, #0x2b8]\n"
        "movw r0, #0x102c\n"
        "add r0, sp, r0\n"
        ".hword 0xf7fe, 0xff7b\n" /* bl #0x59bef0 */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #9]\n"
        "cmp r0, #0\n"
        ".hword 0xd003\n"        /* beq #0x59d010 */
        "movs r0, #1\n"
        "strb.w r0, [sp, #0x18]\n"
        ".hword 0xe002\n"        /* b #0x59d016 */
        "movs r0, #0\n"
        "strb.w r0, [sp, #0x18]\n"
        "movs r0, r6\n"
        ".hword 0xf7fe, 0xfa7c\n" /* bl #0x59b514 */
        "add.w r1, sp, #0x3c00\n"
        "ldr.w r1, [r1, #0x2f4]\n"
        "str r0, [r1]\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #9]\n"
        "cmp r0, #0\n"
        ".hword 0xd004\n"        /* beq #0x59d03e */
        "movs r0, r6\n"
        ".hword 0xf7fe, 0xf917\n" /* bl #0x59b268 */
        "str r0, [sp, #0x3c]\n"
        ".hword 0xe001\n"        /* b #0x59d042 */
        "movs r0, #0x30\n"
        "str r0, [sp, #0x3c]\n"
        "ldr r2, [sp, #0x3c]\n"
        "ldr r1, [sp, #0x1c]\n"
        "movs r0, r5\n"
        ".hword 0xf001, 0xfecf\n" /* bl #0x59edea */
        "movs r5, r0\n"
        "cmp r5, #0\n"
        ".hword 0xd11d\n"        /* bne #0x59d08e */
        "movs r4, #0x40\n"
        "movs r1, r4\n"
        "ldr r0, [sp, #0x1c]\n"
        ".hword 0xf7fd, 0xfce7\n" /* bl #0x59aa2a */
        "ldr r0, [sp, #0x1c]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        "movw r0, #0x102c\n"
        "add r0, sp, r0\n"
        ".hword 0xf7fe, 0xfff3\n" /* bl #0x59c052 */
        "add r0, sp, #0x70\n"
        ".hword 0xf7fd, 0xf95e\n" /* bl #0x59a32e */
        "add r0, sp, #0x90\n"
        ".hword 0xf7fd, 0xf95b\n" /* bl #0x59a32e */
        "add r0, sp, #0xb0\n"
        ".hword 0xf7fd, 0xf958\n" /* bl #0x59a32e */
        "movs r0, r5\n"
        ".hword 0xf001, 0xfedf\n" /* bl #0x59ee42 */
        "add.w sp, sp, #0x3e00\n"
        "add sp, #0xc4\n"
        "pop.w {r4, r5, r6, r7, r8, r9, r10, r11, pc}\n"
        "movs r1, #0x11\n"
        "add r0, sp, #0xb0\n"
        ".hword 0xf7fd, 0xf98d\n" /* bl #0x59a3b0 */
        "add r0, sp, #0xb0\n"
        ".hword 0xf7fd, 0xf99d\n" /* bl #0x59a3d6 */
        "str r0, [sp, #0xc]\n"
        "ldr r0, [sp, #0xc]\n"
        "movs r1, r7\n"
        "movs r2, #0x10\n"
        ".hword 0xf664, 0xfdbe\n" /* bl #0x401c24 */
        "movs r0, #0\n"
        "str r0, [sp, #0x14]\n"
        "ldr r0, [sp, #0x1c]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        ".hword 0xd003\n"        /* beq #0x59d0bc */
        ".hword 0xe7ce\n"        /* b #0x59d054 */
        "movs r0, r5\n"
        ".hword 0xf002, 0xf800\n" /* bl #0x59f0bc */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #8]\n"
        "cmp r0, #0\n"
        "ldr r0, [sp, #0xc]\n"
        ".hword 0xf001, 0xfe85\n" /* bl #0x59edd8 */
        "cmp r0, #0\n"
        ".hword 0xd006\n"        /* beq #0x59d0e0 */
        "ldr r0, [sp, #0x14]\n"
        "cmp r0, #0\n"
        ".hword 0xd001\n"        /* beq #0x59d0dc */
        "movs r7, #0xb\n"
        ".hword 0xe015\n"        /* b #0x59d108 */
        "movs r7, #0xe\n"
        ".hword 0xe013\n"        /* b #0x59d108 */
        "ldr r0, [sp, #0xc]\n"
        ".hword 0xf001, 0xfe69\n" /* bl #0x59edb8 */
        "movs r7, r0\n"
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xb\n"
        ".hword 0xd003\n"        /* beq #0x59d0f8 */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xe\n"
        ".hword 0xd107\n"        /* bne #0x59d108 */
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #9]\n"
        "cmp r0, #0\n"
        ".hword 0xd000\n"        /* beq #0x59d108 */
        "movs r7, #0\n"
        "add.w r0, sp, #0x3c00\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "ldrb r0, [r0, #8]\n"
        "cmp r0, #0\n"
        ".hword 0xd047\n"        /* beq #0x59d1a6 */
        "ldrb.w r0, [sp, #0x19]\n"
        "cmp r0, #0\n"
        ".hword 0xd11f\n"        /* bne #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #1\n"
        ".hword 0xd01b\n"        /* beq #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #3\n"
        ".hword 0xd017\n"        /* beq #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xd\n"
        ".hword 0xd013\n"        /* beq #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xa\n"
        ".hword 0xd00f\n"        /* beq #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xb\n"
        ".hword 0xd00b\n"        /* beq #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xc\n"
        ".hword 0xd007\n"        /* beq #0x59d15e */
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0xe\n"
        ".hword 0xd003\n"        /* beq #0x59d15e */
    );
}
