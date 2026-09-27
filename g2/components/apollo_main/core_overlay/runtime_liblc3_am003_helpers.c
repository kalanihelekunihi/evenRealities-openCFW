/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-003 retained island.
 */

#if defined(OPEN_CFW_AM003_DD7C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dd7c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x6b\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DD86_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dd86(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x10\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DD90_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dd90(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x12\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DD9A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dd9a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x1c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "str	r0, [sp]\n"
        "ldr	r0, [sp]\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDA8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dda8(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x1d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDB4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ddb4(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x20\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDC0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ddc0(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x24\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDCC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ddcc(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x25\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDD8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ddd8(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x26\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDE2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dde2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x31\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "str	r0, [sp]\n"
        "ldr	r0, [sp]\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDF0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ddf0(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x32\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DDFC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ddfc(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x30\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE06_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de06(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x35\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am003_de06_0010\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am003_de06_0012\n"
        "L_open_cfw_runtime_am003_de06_0010:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am003_de06_0012:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE1C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de1c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x3c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE26_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de26(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x42\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE30_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de30(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x3d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "str	r0, [sp]\n"
        "ldr	r0, [sp]\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE3E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de3e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x3e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE4A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de4a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE54_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de54(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x2d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am003_de54_0010\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am003_de54_0012\n"
        "L_open_cfw_runtime_am003_de54_0010:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am003_de54_0012:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE6A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de6a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x62\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE76_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de76(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x16\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44bdea\n"
        "bl .\n"
        "uxth	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DE82_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_de82(void)
{
    __asm__ volatile(
        
        "push	{r0, r1, r2, r3, r4, lr}\n"
        "movs	r1, r0\n"
        "ldr.w	r0, [pc, #0x3fc]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44cf98\n"
        "bl .\n"
        "movs	r4, r0\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am003_de82_003e\n"
        "ldr.w	r0, [pc, #0x3f0]\n"
        "str	r0, [sp, #8]\n"
        "ldr.w	r0, [pc, #0x3f0]\n"
        "str	r0, [sp, #4]\n"
        "ldr.w	r0, [pc, #0x3ec]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x3ec]\n"
        "movs	r2, #0xd9\n"
        "ldr.w	r1, [pc, #0x3e8]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_de82_0034:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_de82_0034\n"
        "L_open_cfw_runtime_am003_de82_003e:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am003_de82_0046\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am003_de82_004e\n"
        "L_open_cfw_runtime_am003_de82_0046:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d0f0\n"
        "bl .\n"
        "movs	r0, r4\n"
        "L_open_cfw_runtime_am003_de82_004e:\n"
        "add	sp, #0x10\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DED4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_ded4(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, r6, r7, lr}\n"
        "sub	sp, #0x20\n"
        "movs	r4, r0\n"
        "movs	r6, r1\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am003_ded4_0038\n"
        "ldr.w	r0, [pc, #0x3a4]\n"
        "str	r0, [sp, #8]\n"
        "ldr.w	r0, [pc, #0x3a4]\n"
        "str	r0, [sp, #4]\n"
        "ldr.w	r0, [pc, #0x3a0]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x3a8]\n"
        "movs	r2, #0xe9\n"
        "ldr.w	r1, [pc, #0x39c]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_ded4_002e:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_ded4_002e\n"
        "L_open_cfw_runtime_am003_ded4_0038:\n"
        "movs	r1, r6\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_e0e0\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_ded4_00cc\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f612\n"
        "bl .\n"
        "movs	r7, r0\n"
        "lsls	r0, r6, #0x1f\n"
        "bpl	L_open_cfw_runtime_am003_ded4_0056\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_440656\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_ded4_0056:\n"
        "ldr	r0, [r4, #0x24]\n"
        "orrs	r0, r6\n"
        "str	r0, [r4, #0x24]\n"
        "lsls	r0, r6, #0x1f\n"
        "bpl	L_open_cfw_runtime_am003_ded4_008c\n"
        "movs	r1, #2\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_e184\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am003_ded4_008c\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_e1be\n"
        "bl .\n"
        "movs	r5, r0\n"
        "cmp	r5, #0\n"
        "beq	L_open_cfw_runtime_am003_ded4_008c\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d45c\n"
        "bl .\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d58c\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am003_ded4_008c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_440656\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_ded4_008c:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f612\n"
        "bl .\n"
        "uxtb	r7, r7\n"
        "cmp	r7, r0\n"
        "bne	L_open_cfw_runtime_am003_ded4_009e\n"
        "tst.w	r6, #0x1800000\n"
        "beq	L_open_cfw_runtime_am003_ded4_00ae\n"
        "L_open_cfw_runtime_am003_ded4_009e:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44dca2\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f648\n"
        "bl .\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f648\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_ded4_00ae:\n"
        "lsls	r0, r6, #0x1b\n"
        "bpl	L_open_cfw_runtime_am003_ded4_00cc\n"
        "mov	r2, sp\n"
        "add	r1, sp, #0x10\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44eb28\n"
        "bl .\n"
        "add	r1, sp, #0x10\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_4405d4\n"
        "bl .\n"
        "mov	r1, sp\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_4405d4\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_ded4_00cc:\n"
        "add	sp, #0x24\n"
        "pop	{r4, r5, r6, r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_DFA4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_dfa4(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "sub	sp, #0x20\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am003_dfa4_0030\n"
        "ldr	r0, [pc, #0x2d4]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x2d4]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x2d4]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x2e0]\n"
        "mov.w	r2, #0x110\n"
        "ldr	r1, [pc, #0x2d4]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_dfa4_0026:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_dfa4_0026\n"
        "L_open_cfw_runtime_am003_dfa4_0030:\n"
        "movs	r1, r5\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_e11c\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am003_dfa4_009e\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f612\n"
        "bl .\n"
        "movs	r6, r0\n"
        "lsls	r0, r5, #0x1b\n"
        "bpl	L_open_cfw_runtime_am003_dfa4_0062\n"
        "mov	r2, sp\n"
        "add	r1, sp, #0x10\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44eb28\n"
        "bl .\n"
        "add	r1, sp, #0x10\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_4405d4\n"
        "bl .\n"
        "mov	r1, sp\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_4405d4\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_dfa4_0062:\n"
        "ldr	r0, [r4, #0x24]\n"
        "bics	r0, r5\n"
        "str	r0, [r4, #0x24]\n"
        "lsls	r0, r5, #0x1f\n"
        "bpl	L_open_cfw_runtime_am003_dfa4_0082\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_440656\n"
        "bl .\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44dca2\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f648\n"
        "bl .\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f648\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_dfa4_0082:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f612\n"
        "bl .\n"
        "uxtb	r6, r6\n"
        "cmp	r6, r0\n"
        "bne	L_open_cfw_runtime_am003_dfa4_0094\n"
        "tst.w	r5, #0x1800000\n"
        "beq	L_open_cfw_runtime_am003_dfa4_009e\n"
        "L_open_cfw_runtime_am003_dfa4_0094:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44dca2\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43f648\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_dfa4_009e:\n"
        "add	sp, #0x20\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E046_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e046(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e046_002a\n"
        "ldr	r0, [pc, #0x238]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x238]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x238]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x248]\n"
        "mov.w	r2, #0x132\n"
        "ldr	r1, [pc, #0x238]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e046_0020:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e046_0020\n"
        "L_open_cfw_runtime_am003_e046_002a:\n"
        "ldrh	r2, [r0, #0x28]\n"
        "orrs	r1, r2\n"
        "ldrh	r2, [r0, #0x28]\n"
        "movs	r3, r1\n"
        "uxth	r3, r3\n"
        "cmp	r2, r3\n"
        "beq	L_open_cfw_runtime_am003_e046_003e\n"
        "uxth	r1, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43ebec\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e046_003e:\n"
        "pop	{r0, r1, r2, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E086_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e086(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e086_002a\n"
        "ldr	r0, [pc, #0x1f8]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x1f8]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x1f8]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x20c]\n"
        "mov.w	r2, #0x13c\n"
        "ldr	r1, [pc, #0x1f8]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e086_0020:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e086_0020\n"
        "L_open_cfw_runtime_am003_e086_002a:\n"
        "ldrh	r2, [r0, #0x28]\n"
        "bics.w	r1, r2, r1\n"
        "ldrh	r2, [r0, #0x28]\n"
        "movs	r3, r1\n"
        "uxth	r3, r3\n"
        "cmp	r2, r3\n"
        "beq	L_open_cfw_runtime_am003_e086_0040\n"
        "uxth	r1, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_43ebec\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e086_0040:\n"
        "pop	{r0, r1, r2, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E0C8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e0c8(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "uxtb	r2, r2\n"
        "cmp	r2, #0\n"
        "beq	L_open_cfw_runtime_am003_e0c8_0010\n"
        "uxth	r1, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_e046\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am003_e0c8_0016\n"
        "L_open_cfw_runtime_am003_e0c8_0010:\n"
        "uxth	r1, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_e086\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e0c8_0016:\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E0E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e0e0(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e0e0_002a\n"
        "ldr	r0, [pc, #0x1a0]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x1a0]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x1a0]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x1b8]\n"
        "mov.w	r2, #0x150\n"
        "ldr	r1, [pc, #0x19c]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e0e0_0020:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e0e0_0020\n"
        "L_open_cfw_runtime_am003_e0e0_002a:\n"
        "ldr	r0, [r0, #0x24]\n"
        "ands	r0, r1\n"
        "cmp	r0, r1\n"
        "bne	L_open_cfw_runtime_am003_e0e0_0036\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am003_e0e0_0038\n"
        "L_open_cfw_runtime_am003_e0e0_0036:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am003_e0e0_0038:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E11C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e11c(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e11c_002a\n"
        "ldr	r0, [pc, #0x164]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x164]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x164]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x180]\n"
        "movw	r2, #0x157\n"
        "ldr	r1, [pc, #0x160]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e11c_0020:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e11c_0020\n"
        "L_open_cfw_runtime_am003_e11c_002a:\n"
        "ldr	r0, [r0, #0x24]\n"
        "tst	r0, r1\n"
        "beq	L_open_cfw_runtime_am003_e11c_0034\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am003_e11c_0036\n"
        "L_open_cfw_runtime_am003_e11c_0034:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am003_e11c_0036:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E156_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e156(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e156_002a\n"
        "ldr	r0, [pc, #0x128]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x128]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x128]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x148]\n"
        "mov.w	r2, #0x15e\n"
        "ldr	r1, [pc, #0x128]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e156_0020:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e156_0020\n"
        "L_open_cfw_runtime_am003_e156_002a:\n"
        "ldrh	r0, [r0, #0x28]\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E184_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e184(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e184_002a\n"
        "ldr	r0, [pc, #0xfc]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0xfc]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0xfc]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x120]\n"
        "movw	r2, #0x165\n"
        "ldr	r1, [pc, #0xf8]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e184_0020:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e184_0020\n"
        "L_open_cfw_runtime_am003_e184_002a:\n"
        "ldrh	r0, [r0, #0x28]\n"
        "tst	r0, r1\n"
        "beq	L_open_cfw_runtime_am003_e184_0034\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am003_e184_0036\n"
        "L_open_cfw_runtime_am003_e184_0034:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am003_e184_0036:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM003_E1BE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am003_e1be(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am003_e1be_002c\n"
        "ldr	r0, [pc, #0xc0]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0xc0]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0xc0]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0xc5c]\n"
        "mov.w	r2, #0x16c\n"
        "ldr	r1, [pc, #0xbc]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am003_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am003_e1be_0022:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am003_e1be_0022\n"
        "L_open_cfw_runtime_am003_e1be_002c:\n"
        "ldr	r1, [r0, #8]\n"
        "cmp	r1, #0\n"
        "beq	L_open_cfw_runtime_am003_e1be_0038\n"
        "ldr	r0, [r0, #8]\n"
        "ldr	r0, [r0, #4]\n"
        "b	L_open_cfw_runtime_am003_e1be_003a\n"
        "L_open_cfw_runtime_am003_e1be_0038:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am003_e1be_003a:\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif
