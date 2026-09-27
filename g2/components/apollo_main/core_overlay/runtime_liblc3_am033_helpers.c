/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-033 retained island.
 */

#if defined(OPEN_CFW_AM033_84380_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84380(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_8438C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_8438c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr.w r0, [pc, #0x614]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d46de\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84398_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84398(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f730\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_84398_0036\n    ldr.w r0, [pc, #0x608]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x604]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x604]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x600]\n    movs r2, #0x54\n    ldr.w r1, [pc, #0x600]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am033_84398_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am033_84398_002c\nL_open_cfw_runtime_am033_84398_0036:\n    ldr.w r1, [pc, #0x5d8]\n    ldr.w r2, [r1, #0x13c]\n    str r2, [r0]\n    str.w r0, [r1, #0x13c]\n    ldr.w r2, [r1, #0x140]\n    adds r2, r2, #1\n    str.w r2, [r1, #0x140]\n    ldr.w r1, [r1, #0x140]\n    str r1, [r0, #8]\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_843EE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_843ee(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r0, #0x5c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f730\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_843ee_003e\n    ldr.w r0, [pc, #0x5a8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x5b8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x5a4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x5b0]\n    movs r2, #0x63\n    ldr.w r1, [pc, #0x5a0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am033_843ee_0034:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am033_843ee_0034\nL_open_cfw_runtime_am033_843ee_003e:\n    adds.w r0, r4, #8\n    movs r1, r6\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00439c04\n    bl .\n    adds.w r0, r4, #0x18\n    movs r1, r6\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00439c04\n    bl .\n    str r5, [r4, #0x48]\n    adds.w r0, r4, #0x38\n    adds.w r1, r5, #0x18\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00439c04\n    bl .\n    movs r0, #1\n    str r0, [r4, #0x50]\n    ldr r0, [r5, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_843ee_0074\n    str r4, [r5, #0x44]\n    b L_open_cfw_runtime_am033_843ee_0082\nL_open_cfw_runtime_am033_843ee_0074:\n    ldr r1, [r5, #0x44]\n    b L_open_cfw_runtime_am033_843ee_007a\nL_open_cfw_runtime_am033_843ee_0078:\n    ldr r1, [r1]\nL_open_cfw_runtime_am033_843ee_007a:\n    ldr r0, [r1]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_843ee_0078\n    str r4, [r1]\nL_open_cfw_runtime_am033_843ee_0082:\n    movs r0, r4\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84476_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84476(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r5, r1\n    ldr r6, [r5, #0x54]\n    str r0, [r6, #0x10]\n    ldr.w r4, [pc, #0x548]\n    ldrb.w r0, [r4, #0x20]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_84476_008c\n    ldr r0, [r6]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84476_003e\n    movs.w r1, #0x80000\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84476_003e\n    movs r0, #1\n    strb.w r0, [r4, #0x20]\n    movs r2, r5\n    movs r1, #0x22\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00451670\n    bl .\n    movs r0, #0\n    strb.w r0, [r4, #0x20]\nL_open_cfw_runtime_am033_84476_003e:\n    movs r0, #0x64\n    strb.w r0, [r5, #0x59]\n    movs r0, #0\n    strb.w r0, [r5, #0x58]\n    ldr r4, [r4]\n    b L_open_cfw_runtime_am033_84476_005e\nL_open_cfw_runtime_am033_84476_004e:\n    ldr r0, [r4, #0x10]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84476_005c\n    movs r1, r5\n    movs r0, r4\n    ldr r2, [r4, #0x10]\n    blx r2\nL_open_cfw_runtime_am033_84476_005c:\n    ldr r4, [r4]\nL_open_cfw_runtime_am033_84476_005e:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_84476_004e\n    ldrb.w r0, [r5, #0x58]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_84476_0086\n    ldr.w r0, [pc, #0x4e8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x4e8]\n    movs r2, #0x9f\n    ldr.w r1, [pc, #0x4cc]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\n    movs r0, #3\n    str r0, [r5, #0x50]\n    b L_open_cfw_runtime_am033_84476_00b0\nL_open_cfw_runtime_am033_84476_0086:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_84548\n    bl .\n    b L_open_cfw_runtime_am033_84476_00b0\nL_open_cfw_runtime_am033_84476_008c:\n    movs r0, #0x64\n    strb.w r0, [r5, #0x59]\n    movs r0, #0\n    strb.w r0, [r5, #0x58]\n    ldr r4, [r4]\n    b L_open_cfw_runtime_am033_84476_00ac\nL_open_cfw_runtime_am033_84476_009c:\n    ldr r0, [r4, #0x10]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84476_00aa\n    movs r1, r5\n    movs r0, r4\n    ldr r2, [r4, #0x10]\n    blx r2\nL_open_cfw_runtime_am033_84476_00aa:\n    ldr r4, [r4]\nL_open_cfw_runtime_am033_84476_00ac:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_84476_009c\nL_open_cfw_runtime_am033_84476_00b0:\n    pop {r0, r1, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84528_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84528(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr.w r0, [pc, #0x47c]\n    ldr.w r4, [r0, #0x13c]\n    b L_open_cfw_runtime_am033_84528_001a\nL_open_cfw_runtime_am033_84528_000c:\n    ldr r0, [r4, #0x14]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84528_0018\n    movs r0, r4\n    ldr r1, [r4, #0x14]\n    blx r1\nL_open_cfw_runtime_am033_84528_0018:\n    ldr r4, [r4]\nL_open_cfw_runtime_am033_84528_001a:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_84528_000c\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84548_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84548(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r6, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044fa22\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am033_84548_003a\nL_open_cfw_runtime_am033_84548_000e:\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_8458e\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84548_001c\n    movs r6, #1\nL_open_cfw_runtime_am033_84548_001c:\n    ldr r4, [r4, #0x4c]\nL_open_cfw_runtime_am033_84548_001e:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_84548_000e\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_84548_0032\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_84528\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_8462e\n    bl .\nL_open_cfw_runtime_am033_84548_0032:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044fa22\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am033_84548_003a:\n    cmp r5, #0\n    beq L_open_cfw_runtime_am033_84548_0044\n    ldr.w r4, [r5, #0x2ac]\n    b L_open_cfw_runtime_am033_84548_001e\nL_open_cfw_runtime_am033_84548_0044:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_8458E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_8458e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r6, r0\n    movs r5, r1\n    movs r4, #0\n    ldr r0, [r5, #0x44]\n    b L_open_cfw_runtime_am033_8458e_0014\nL_open_cfw_runtime_am033_8458e_000c:\n    movs r4, r0\n    b L_open_cfw_runtime_am033_8458e_0012\nL_open_cfw_runtime_am033_8458e_0010:\n    str r7, [r5, #0x44]\nL_open_cfw_runtime_am033_8458e_0012:\n    movs r0, r7\nL_open_cfw_runtime_am033_8458e_0014:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_8458e_002e\n    ldr r7, [r0]\n    ldr r1, [r0, #0x50]\n    cmp r1, #3\n    bne L_open_cfw_runtime_am033_8458e_000c\n    movs r1, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_848e8\n    bl .\n    cmp r4, #0\n    beq L_open_cfw_runtime_am033_8458e_0010\n    str r7, [r4]\n    b L_open_cfw_runtime_am033_8458e_0012\nL_open_cfw_runtime_am033_8458e_002e:\n    movs r6, #0\n    ldr r0, [r5, #0x48]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_8458e_006e\n    ldrb.w r0, [r5, #0x50]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_8458e_006e\n    ldr r0, [r5, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_8458e_006e\n    ldr r0, [r5, #0x48]\n    ldr r1, [r0, #0x44]\n    b L_open_cfw_runtime_am033_8458e_004c\nL_open_cfw_runtime_am033_8458e_004a:\n    ldr r1, [r1]\nL_open_cfw_runtime_am033_8458e_004c:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am033_8458e_008e\n    ldrb r0, [r1, #4]\n    cmp r0, #7\n    bne L_open_cfw_runtime_am033_8458e_004a\n    ldr r0, [r1, #0x50]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_8458e_004a\n    ldr r0, [r1, #0x54]\n    ldr r0, [r0, #0x1c]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am033_8458e_004a\n    movs r0, #1\n    str r0, [r1, #0x50]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_8462e\n    bl .\n    b L_open_cfw_runtime_am033_8458e_008e\nL_open_cfw_runtime_am033_8458e_006e:\n    ldr.w r0, [pc, #0x3a8]\n    ldr.w r4, [r0, #0x13c]\n    b L_open_cfw_runtime_am033_8458e_008a\nL_open_cfw_runtime_am033_8458e_0078:\n    movs r1, r5\n    movs r0, r4\n    ldr r2, [r4, #0xc]\n    blx r2\n    cmn.w r0, #1\n    beq L_open_cfw_runtime_am033_8458e_0088\n    movs r6, #1\nL_open_cfw_runtime_am033_8458e_0088:\n    ldr r4, [r4]\nL_open_cfw_runtime_am033_8458e_008a:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_8458e_0078\nL_open_cfw_runtime_am033_8458e_008e:\n    movs r0, r6\n    uxtb r0, r0\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84622_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84622(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr.w r0, [pc, #0x37c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d46e8\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_8462E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_8462e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr.w r0, [pc, #0x370]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4724\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_8463A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_8463a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr.w r3, [pc, #0x368]\n    ldr.w r3, [r3, #0x140]\n    cmp r3, #1\n    bne L_open_cfw_runtime_am033_8463a_0014\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_849fc\n    bl .\n    b L_open_cfw_runtime_am033_8463a_001a\nL_open_cfw_runtime_am033_8463a_0014:\n    uxtb r2, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_84656\n    bl .\nL_open_cfw_runtime_am033_8463a_001a:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84656_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84656(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r6, r2\n    ldr r0, [r5, #0x44]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84656_0048\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00453604\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044fa7e\n    bl .\n    movs r7, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00453604\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044faa8\n    bl .\n    ldr r1, [r5, #0x44]\n    ldr r2, [r1, #0x50]\n    cmp r2, #1\n    beq L_open_cfw_runtime_am033_84656_0048\n    ldr r2, [r1, #8]\n    cmp r2, #1\n    bge L_open_cfw_runtime_am033_84656_0048\n    ldr r2, [r1, #0x10]\n    subs r7, r7, #1\n    cmp r2, r7\n    blt L_open_cfw_runtime_am033_84656_0048\n    ldr r2, [r1, #0xc]\n    cmp r2, #1\n    bge L_open_cfw_runtime_am033_84656_0048\n    ldr r1, [r1, #0x14]\n    subs r0, r0, #1\n    cmp r1, r0\n    blt L_open_cfw_runtime_am033_84656_0048\n    movs r0, #0\n    b L_open_cfw_runtime_am033_84656_0086\nL_open_cfw_runtime_am033_84656_0048:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am033_84656_0050\n    ldr r4, [r4]\n    b L_open_cfw_runtime_am033_84656_0056\nL_open_cfw_runtime_am033_84656_0050:\n    ldr r4, [r5, #0x44]\n    b L_open_cfw_runtime_am033_84656_0056\nL_open_cfw_runtime_am033_84656_0054:\n    ldr r4, [r4]\nL_open_cfw_runtime_am033_84656_0056:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am033_84656_0084\n    ldr r0, [r4, #0x50]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am033_84656_0054\n    ldrb.w r0, [r4, #0x58]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84656_0074\n    ldrb.w r0, [r4, #0x58]\n    movs r1, r6\n    uxtb r1, r1\n    cmp r0, r1\n    bne L_open_cfw_runtime_am033_84656_0054\nL_open_cfw_runtime_am033_84656_0074:\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_848b2\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84656_0054\n    movs r0, r4\n    b L_open_cfw_runtime_am033_84656_0086\nL_open_cfw_runtime_am033_84656_0084:\n    movs r0, #0\nL_open_cfw_runtime_am033_84656_0086:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_846DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_846de(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_846de_002c\n    ldr r0, [pc, #0x2ec]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x2ec]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x2c4]\n    str r0, [sp]\n    ldr r3, [pc, #0x2e8]\n    mov.w r2, #0x17c\n    ldr r1, [pc, #0x2c0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am033_846de_0022:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am033_846de_0022\nL_open_cfw_runtime_am033_846de_002c:\n    movs r1, #0x58\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_84380\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_8471a\n    bl .\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_8471A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_8471a(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_8471a_002c\n    ldr r0, [pc, #0x2b0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x2b0]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x288]\n    str r0, [sp]\n    ldr r3, [pc, #0x2b0]\n    movw r2, #0x183\n    ldr r1, [pc, #0x284]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am033_8471a_0022:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am033_8471a_0022\nL_open_cfw_runtime_am033_8471a_002c:\n    movs r0, #0xff\n    strb.w r0, [r4, #0x38]\n    movs r3, #0\n    movs r2, #0\n    movs r1, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044107c\n    bl .\n    str.w r0, [r4, #0x39]\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_8475E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_8475e(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r7, r2\n    movs r0, #0x58\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f730\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_8475e_0038\n    ldr r0, [pc, #0x238]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x26c]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x238]\n    str r0, [sp]\n    ldr r3, [pc, #0x268]\n    movw r2, #0x18f\n    ldr r1, [pc, #0x234]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am033_8475e_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am033_8475e_002e\nL_open_cfw_runtime_am033_8475e_0038:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am033_8475e_0040\n    movs r0, #0\n    b L_open_cfw_runtime_am033_8475e_0064\nL_open_cfw_runtime_am033_8475e_0040:\n    movs r3, r7\n    movs r2, r6\n    uxtb r2, r2\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_847c4\n    bl .\n    cmp r5, #0\n    beq L_open_cfw_runtime_am033_8475e_0062\n    ldrb.w r0, [r5, #0x38]\n    strb.w r0, [r4, #0x38]\n    ldr.w r0, [r5, #0x39]\n    str.w r0, [r4, #0x39]\nL_open_cfw_runtime_am033_8475e_0062:\n    movs r0, r4\nL_open_cfw_runtime_am033_8475e_0064:\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_847C4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_847c4(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_846de\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00453604\n    bl .\n    mov r8, r0\n    str r5, [r4, #0x48]\n    adds.w r0, r4, #0x18\n    movs r1, r7\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00439c04\n    bl .\n    adds r0, r4, #4\n    movs r1, r7\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00439c04\n    bl .\n    adds.w r0, r4, #0x28\n    movs r1, r7\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00439c04\n    bl .\n    strb r6, [r4, #0x14]\n    ldr.w r0, [r8, #0x2b0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_847c4_0050\n    movs r1, r4\n    mov r0, r8\n    ldr.w r2, [r8, #0x2b0]\n    blx r2\nL_open_cfw_runtime_am033_847c4_0050:\n    ldr.w r0, [r8, #0x2ac]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_847c4_006a\n    ldr.w r1, [r8, #0x2ac]\n    b L_open_cfw_runtime_am033_847c4_0060\nL_open_cfw_runtime_am033_847c4_005e:\n    ldr r1, [r1, #0x4c]\nL_open_cfw_runtime_am033_847c4_0060:\n    ldr r0, [r1, #0x4c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_847c4_005e\n    str r4, [r1, #0x4c]\n    b L_open_cfw_runtime_am033_847c4_006e\nL_open_cfw_runtime_am033_847c4_006a:\n    str.w r4, [r8, #0x2ac]\nL_open_cfw_runtime_am033_847c4_006e:\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84836_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84836(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84836_0010\n    ldr r0, [r4]\n    ldr r0, [r0, #0x10]\n    b L_open_cfw_runtime_am033_84836_007a\nL_open_cfw_runtime_am033_84836_0010:\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00451598\n    bl .\n    movs r6, r0\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004515a4\n    bl .\n    movs r7, r0\n    ldrb r1, [r4, #0x14]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0048aad8\n    bl .\n    movs r5, r0\n    mul r5, r5, r7\n    movs r3, #0\n    ldrb r2, [r4, #0x14]\n    movs r1, r7\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0048affa\n    bl .\n    str r0, [r4]\n    ldr r0, [r4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am033_84836_0058\n    ldr r0, [pc, #0x170]\n    str r0, [sp]\n    ldr r3, [pc, #0x170]\n    movw r2, #0x1d7\n    ldr r1, [pc, #0x138]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am033_84836_007a\nL_open_cfw_runtime_am033_84836_0058:\n    ldr r0, [pc, #0x118]\n    ldr.w r1, [r0, #0x144]\n    adds r5, r5, r1\n    str.w r5, [r0, #0x144]\n    ldrb r0, [r4, #0x14]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00440fc4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_84836_0076\n    movs r1, #0\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0048ac40\n    bl .\nL_open_cfw_runtime_am033_84836_0076:\n    ldr r0, [r4]\n    ldr r0, [r0, #0x10]\nL_open_cfw_runtime_am033_84836_007a:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_848B2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_848b2(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x10\n    movs r5, r1\n    ldr r4, [r0, #0x44]\n    b L_open_cfw_runtime_am033_848b2_000c\nL_open_cfw_runtime_am033_848b2_000a:\n    ldr r4, [r4]\nL_open_cfw_runtime_am033_848b2_000c:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am033_848b2_0030\n    cmp r4, r5\n    beq L_open_cfw_runtime_am033_848b2_0030\n    ldr r0, [r4, #0x50]\n    cmp r0, #3\n    beq L_open_cfw_runtime_am033_848b2_000a\n    adds.w r2, r5, #0x18\n    adds.w r1, r4, #0x18\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00450bcc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_848b2_000a\n    movs r0, #0\n    b L_open_cfw_runtime_am033_848b2_0032\nL_open_cfw_runtime_am033_848b2_0030:\n    movs r0, #1\nL_open_cfw_runtime_am033_848b2_0032:\n    add sp, #0x14\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_848E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_848e8(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    ldrb r0, [r5, #4]\n    cmp r0, #7\n    bne L_open_cfw_runtime_am033_848e8_0090\n    ldr r0, [r5, #0x54]\n    ldr r6, [r0, #0x1c]\n    ldr r0, [r6]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_848e8_005e\n    adds r0, r6, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004515a4\n    bl .\n    ldr r1, [r6]\n    ldr r1, [r1, #8]\n    uxth r1, r1\n    mul r1, r1, r0\n    ldr r0, [pc, #0x98]\n    ldr.w r2, [r0, #0x144]\n    cmp r2, r1\n    blo L_open_cfw_runtime_am033_848e8_003c\n    ldr.w r2, [r0, #0x144]\n    subs r1, r2, r1\n    str.w r1, [r0, #0x144]\n    b L_open_cfw_runtime_am033_848e8_0054\nL_open_cfw_runtime_am033_848e8_003c:\n    movs r1, #0\n    str.w r1, [r0, #0x144]\n    ldr r0, [pc, #0xc8]\n    str r0, [sp]\n    ldr r3, [pc, #0xc8]\n    mov.w r2, #0x230\n    ldr r1, [pc, #0x84]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am033_848e8_0054:\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0048b216\n    bl .\n    movs r0, #0\n    str r0, [r6]\nL_open_cfw_runtime_am033_848e8_005e:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am033_848e8_0090\n    ldr.w r0, [r4, #0x2ac]\n    b L_open_cfw_runtime_am033_848e8_006a\nL_open_cfw_runtime_am033_848e8_0068:\n    ldr r0, [r0, #0x4c]\nL_open_cfw_runtime_am033_848e8_006a:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_848e8_0078\n    ldr r1, [r0, #0x4c]\n    cmp r1, r6\n    bne L_open_cfw_runtime_am033_848e8_0068\n    ldr r1, [r6, #0x4c]\n    str r1, [r0, #0x4c]\nL_open_cfw_runtime_am033_848e8_0078:\n    ldr.w r0, [r4, #0x2b4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_848e8_008a\n    movs r1, r6\n    movs r0, r4\n    ldr.w r2, [r4, #0x2b4]\n    blx r2\nL_open_cfw_runtime_am033_848e8_008a:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f758\n    bl .\nL_open_cfw_runtime_am033_848e8_0090:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_00489fc8\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am033_848e8_00ae\n    ldrb.w r0, [r4, #0x54]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am033_848e8_00ae\n    ldr r0, [r4, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f758\n    bl .\n    movs r0, #0\n    str r0, [r4, #0x1c]\nL_open_cfw_runtime_am033_848e8_00ae:\n    ldr r0, [r5, #0x54]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f758\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_0044f758\n    bl .\n    pop {r0, r1, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_849FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_849fc(void)
{
    __asm__ volatile(
        "    ldr r0, [r0, #0x44]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am033_849fc_0010\n    ldr r1, [r0, #0x50]\n    cmp r1, #1\n    beq L_open_cfw_runtime_am033_849fc_0010\n    movs r0, #0\n    b L_open_cfw_runtime_am033_849fc_0010\nL_open_cfw_runtime_am033_849fc_0010:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84A10_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84a10(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r2\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d481a\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4826\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84A26_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84a26(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d487a\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4886\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4862\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d486e\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84A4E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84a4e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d487a\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4886\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84A66_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84a66(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4862\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d486e\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM033_84A7E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am033_84a7e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d4892\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am033_addr_004d489e\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif
