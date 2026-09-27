/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-015 retained island.
 */

#if defined(OPEN_CFW_AM015_4FA5E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fa5e(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r1\n"
        "movs	r5, r2\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fa5e_000e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fa5e_000e:\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4fa5e_001e\n"
        "str	r4, [r0, #0x10]\n"
        "str	r5, [r0, #0x14]\n"
        "ldr.w	r0, [r0, #0x2bc]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_440656\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fa5e_001e:\n"
        "pop	{r0, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FA7E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fa7e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fa7e_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fa7e_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fa7e_0012\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fa7e_0028\n"
        "L_open_cfw_runtime_am015_4fa7e_0012:\n"
        "ldrb.w	r1, [r0, #0x2fc]\n"
        "ands	r1, r1, #7\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am015_4fa7e_0022\n"
        "cmp	r1, #3\n"
        "bne	L_open_cfw_runtime_am015_4fa7e_0026\n"
        "L_open_cfw_runtime_am015_4fa7e_0022:\n"
        "ldr	r0, [r0, #4]\n"
        "b	L_open_cfw_runtime_am015_4fa7e_0028\n"
        "L_open_cfw_runtime_am015_4fa7e_0026:\n"
        "ldr	r0, [r0]\n"
        "L_open_cfw_runtime_am015_4fa7e_0028:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FAA8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4faa8(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4faa8_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4faa8_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4faa8_0012\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4faa8_0028\n"
        "L_open_cfw_runtime_am015_4faa8_0012:\n"
        "ldrb.w	r1, [r0, #0x2fc]\n"
        "ands	r1, r1, #7\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am015_4faa8_0022\n"
        "cmp	r1, #3\n"
        "bne	L_open_cfw_runtime_am015_4faa8_0026\n"
        "L_open_cfw_runtime_am015_4faa8_0022:\n"
        "ldr	r0, [r0]\n"
        "b	L_open_cfw_runtime_am015_4faa8_0028\n"
        "L_open_cfw_runtime_am015_4faa8_0026:\n"
        "ldr	r0, [r0, #4]\n"
        "L_open_cfw_runtime_am015_4faa8_0028:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FAD2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fad2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fad2_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fad2_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fad2_0012\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fad2_003c\n"
        "L_open_cfw_runtime_am015_4fad2_0012:\n"
        "ldrb.w	r1, [r0, #0x2fc]\n"
        "ands	r1, r1, #7\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am015_4fad2_0022\n"
        "cmp	r1, #3\n"
        "bne	L_open_cfw_runtime_am015_4fad2_0030\n"
        "L_open_cfw_runtime_am015_4fad2_0022:\n"
        "ldr	r1, [r0, #0xc]\n"
        "cmp	r1, #1\n"
        "blt	L_open_cfw_runtime_am015_4fad2_002c\n"
        "ldr	r0, [r0, #0xc]\n"
        "b	L_open_cfw_runtime_am015_4fad2_002e\n"
        "L_open_cfw_runtime_am015_4fad2_002c:\n"
        "ldr	r0, [r0, #4]\n"
        "L_open_cfw_runtime_am015_4fad2_002e:\n"
        "b	L_open_cfw_runtime_am015_4fad2_003c\n"
        "L_open_cfw_runtime_am015_4fad2_0030:\n"
        "ldr	r1, [r0, #8]\n"
        "cmp	r1, #1\n"
        "blt	L_open_cfw_runtime_am015_4fad2_003a\n"
        "ldr	r0, [r0, #8]\n"
        "b	L_open_cfw_runtime_am015_4fad2_003c\n"
        "L_open_cfw_runtime_am015_4fad2_003a:\n"
        "ldr	r0, [r0]\n"
        "L_open_cfw_runtime_am015_4fad2_003c:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FB10_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fb10(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fb10_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fb10_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fb10_0012\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fb10_003c\n"
        "L_open_cfw_runtime_am015_4fb10_0012:\n"
        "ldrb.w	r1, [r0, #0x2fc]\n"
        "ands	r1, r1, #7\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am015_4fb10_0022\n"
        "cmp	r1, #3\n"
        "bne	L_open_cfw_runtime_am015_4fb10_0030\n"
        "L_open_cfw_runtime_am015_4fb10_0022:\n"
        "ldr	r1, [r0, #8]\n"
        "cmp	r1, #1\n"
        "blt	L_open_cfw_runtime_am015_4fb10_002c\n"
        "ldr	r0, [r0, #8]\n"
        "b	L_open_cfw_runtime_am015_4fb10_002e\n"
        "L_open_cfw_runtime_am015_4fb10_002c:\n"
        "ldr	r0, [r0]\n"
        "L_open_cfw_runtime_am015_4fb10_002e:\n"
        "b	L_open_cfw_runtime_am015_4fb10_003c\n"
        "L_open_cfw_runtime_am015_4fb10_0030:\n"
        "ldr	r1, [r0, #0xc]\n"
        "cmp	r1, #1\n"
        "blt	L_open_cfw_runtime_am015_4fb10_003a\n"
        "ldr	r0, [r0, #0xc]\n"
        "b	L_open_cfw_runtime_am015_4fb10_003c\n"
        "L_open_cfw_runtime_am015_4fb10_003a:\n"
        "ldr	r0, [r0, #4]\n"
        "L_open_cfw_runtime_am015_4fb10_003c:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FB4E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fb4e(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4fb4e_000e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "movs	r4, r0\n"
        "L_open_cfw_runtime_am015_4fb4e_000e:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4fb4e_0016\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fb4e_004a\n"
        "L_open_cfw_runtime_am015_4fb4e_0016:\n"
        "ldrb.w	r0, [r4, #0x2fc]\n"
        "ands	r0, r0, #7\n"
        "cmp	r0, #1\n"
        "beq	L_open_cfw_runtime_am015_4fb4e_002c\n"
        "blo	L_open_cfw_runtime_am015_4fb4e_0048\n"
        "cmp	r0, #3\n"
        "beq	L_open_cfw_runtime_am015_4fb4e_003c\n"
        "blo	L_open_cfw_runtime_am015_4fb4e_0030\n"
        "b	L_open_cfw_runtime_am015_4fb4e_0048\n"
        "L_open_cfw_runtime_am015_4fb4e_002c:\n"
        "ldr	r0, [r4, #0x14]\n"
        "b	L_open_cfw_runtime_am015_4fb4e_004a\n"
        "L_open_cfw_runtime_am015_4fb4e_0030:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4fad2\n"
        "bl .\n"
        "ldr	r1, [r4, #0x10]\n"
        "subs	r0, r0, r1\n"
        "b	L_open_cfw_runtime_am015_4fb4e_004a\n"
        "L_open_cfw_runtime_am015_4fb4e_003c:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4fad2\n"
        "bl .\n"
        "ldr	r1, [r4, #0x14]\n"
        "subs	r0, r0, r1\n"
        "b	L_open_cfw_runtime_am015_4fb4e_004a\n"
        "L_open_cfw_runtime_am015_4fb4e_0048:\n"
        "ldr	r0, [r4, #0x10]\n"
        "L_open_cfw_runtime_am015_4fb4e_004a:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FB9A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fb9a(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4fb9a_000e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "movs	r4, r0\n"
        "L_open_cfw_runtime_am015_4fb9a_000e:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4fb9a_0016\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fb9a_004a\n"
        "L_open_cfw_runtime_am015_4fb9a_0016:\n"
        "ldrb.w	r0, [r4, #0x2fc]\n"
        "ands	r0, r0, #7\n"
        "cmp	r0, #1\n"
        "beq	L_open_cfw_runtime_am015_4fb9a_002c\n"
        "blo	L_open_cfw_runtime_am015_4fb9a_0048\n"
        "cmp	r0, #3\n"
        "beq	L_open_cfw_runtime_am015_4fb9a_003c\n"
        "blo	L_open_cfw_runtime_am015_4fb9a_0030\n"
        "b	L_open_cfw_runtime_am015_4fb9a_0048\n"
        "L_open_cfw_runtime_am015_4fb9a_002c:\n"
        "ldr	r0, [r4, #0x10]\n"
        "b	L_open_cfw_runtime_am015_4fb9a_004a\n"
        "L_open_cfw_runtime_am015_4fb9a_0030:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4fb10\n"
        "bl .\n"
        "ldr	r1, [r4, #0x14]\n"
        "subs	r0, r0, r1\n"
        "b	L_open_cfw_runtime_am015_4fb9a_004a\n"
        "L_open_cfw_runtime_am015_4fb9a_003c:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4fb10\n"
        "bl .\n"
        "ldr	r1, [r4, #0x10]\n"
        "subs	r0, r0, r1\n"
        "b	L_open_cfw_runtime_am015_4fb9a_004a\n"
        "L_open_cfw_runtime_am015_4fb9a_0048:\n"
        "ldr	r0, [r4, #0x14]\n"
        "L_open_cfw_runtime_am015_4fb9a_004a:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FBE6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fbe6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fbe6_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fbe6_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fbe6_0012\n"
        "movs	r0, #0x82\n"
        "b	L_open_cfw_runtime_am015_4fbe6_0014\n"
        "L_open_cfw_runtime_am015_4fbe6_0012:\n"
        "ldr	r0, [r0, #0x18]\n"
        "L_open_cfw_runtime_am015_4fbe6_0014:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FBFC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fbfc(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r1\n"
        "movs	r5, r2\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fbfc_000e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fbfc_000e:\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4fbfc_001a\n"
        "str	r4, [r0, #0x1c]\n"
        "str	r5, [r0, #0x20]\n"
        "ldr	r1, [r0, #0x1c]\n"
        "str	r1, [r0, #0x24]\n"
        "L_open_cfw_runtime_am015_4fbfc_001a:\n"
        "pop	{r0, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FC18_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fc18(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r1\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fc18_000c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fc18_000c:\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4fc18_0014\n"
        "strb.w	r4, [r0, #0x39]\n"
        "L_open_cfw_runtime_am015_4fc18_0014:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FC2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fc2e(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r1\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fc2e_000c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fc2e_000c:\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4fc2e_0012\n"
        "str	r4, [r0, #0x28]\n"
        "L_open_cfw_runtime_am015_4fc2e_0012:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FC42_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fc42(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #0x34]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4fc42_000a\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am015_4fc42_000c\n"
        "L_open_cfw_runtime_am015_4fc42_000a:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am015_4fc42_000c:\n"
        "uxtb	r0, r0\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FC52_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fc52(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #0x20]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4fc52_000a\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am015_4fc52_000c\n"
        "L_open_cfw_runtime_am015_4fc52_000a:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am015_4fc52_000c:\n"
        "uxtb	r0, r0\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FC62_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fc62(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fc62_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fc62_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fc62_0028\n"
        "ldr.w	r0, [pc, #0x29c]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x29c]\n"
        "movw	r2, #0x245\n"
        "ldr	r1, [pc, #0xb4]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fc62_002c\n"
        "L_open_cfw_runtime_am015_4fc62_0028:\n"
        "ldr.w	r0, [r0, #0x2c4]\n"
        "L_open_cfw_runtime_am015_4fc62_002c:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FC90_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fc90(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fc90_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fc90_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fc90_0028\n"
        "ldr.w	r0, [pc, #0x278]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x274]\n"
        "mov.w	r2, #0x250\n"
        "ldr	r1, [pc, #0x84]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fc90_002c\n"
        "L_open_cfw_runtime_am015_4fc90_0028:\n"
        "ldr.w	r0, [r0, #0x2cc]\n"
        "L_open_cfw_runtime_am015_4fc90_002c:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FCBE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fcbe(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fcbe_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fcbe_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fcbe_0028\n"
        "ldr.w	r0, [pc, #0x250]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x250]\n"
        "movw	r2, #0x25b\n"
        "ldr	r1, [pc, #0x58]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fcbe_002c\n"
        "L_open_cfw_runtime_am015_4fcbe_0028:\n"
        "ldr.w	r0, [r0, #0x2c0]\n"
        "L_open_cfw_runtime_am015_4fcbe_002c:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FCFC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fcfc(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fcfc_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fcfc_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fcfc_0028\n"
        "ldr.w	r0, [pc, #0x21c]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x218]\n"
        "movw	r2, #0x266\n"
        "ldr	r1, [pc, #0x18]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fcfc_002c\n"
        "L_open_cfw_runtime_am015_4fcfc_0028:\n"
        "ldr.w	r0, [r0, #0x2bc]\n"
        "L_open_cfw_runtime_am015_4fcfc_002c:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FD38_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fd38(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fd38_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fd38_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fd38_002a\n"
        "ldr.w	r0, [pc, #0x1e8]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x1e4]\n"
        "movw	r2, #0x271\n"
        "ldr.w	r1, [pc, #0x224]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fd38_002e\n"
        "L_open_cfw_runtime_am015_4fd38_002a:\n"
        "ldr.w	r0, [r0, #0x2c8]\n"
        "L_open_cfw_runtime_am015_4fd38_002e:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FD80_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fd80(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fd80_0034\n"
        "ldr.w	r0, [pc, #0x1f8]\n"
        "str	r0, [sp, #8]\n"
        "ldr.w	r0, [pc, #0x1f4]\n"
        "str	r0, [sp, #4]\n"
        "ldr.w	r0, [pc, #0x1f4]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x1f0]\n"
        "movw	r2, #0x313\n"
        "ldr.w	r1, [pc, #0x1d8]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fd80_002a:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am015_4fd80_002a\n"
        "L_open_cfw_runtime_am015_4fd80_0034:\n"
        "adds.w	r0, r0, #0x2e4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_500e4\n"
        "bl .\n"
        "pop	{r0, r1, r2, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FDBE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fdbe(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, r6, lr}\n"
        "sub	sp, #0x1c\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r6, r2\n"
        "movs	r1, #0x1c\n"
        "mov	r0, sp\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44f7b4\n"
        "bl .\n"
        "str	r5, [sp, #8]\n"
        "str	r4, [sp]\n"
        "str	r4, [sp, #4]\n"
        "str	r6, [sp, #0x10]\n"
        "movs	r2, #1\n"
        "mov	r1, sp\n"
        "adds.w	r0, r4, #0x2e4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4ffe6\n"
        "bl .\n"
        "movs	r1, r0\n"
        "uxtb	r1, r1\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am015_4fdbe_0032\n"
        "uxtb	r0, r0\n"
        "b	L_open_cfw_runtime_am015_4fdbe_004c\n"
        "L_open_cfw_runtime_am015_4fdbe_0032:\n"
        "movs	r2, #0\n"
        "mov	r1, sp\n"
        "adds.w	r0, r4, #0x2e4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4ffe6\n"
        "bl .\n"
        "movs	r1, r0\n"
        "uxtb	r1, r1\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am015_4fdbe_004a\n"
        "uxtb	r0, r0\n"
        "b	L_open_cfw_runtime_am015_4fdbe_004c\n"
        "L_open_cfw_runtime_am015_4fdbe_004a:\n"
        "uxtb	r0, r0\n"
        "L_open_cfw_runtime_am015_4fdbe_004c:\n"
        "add	sp, #0x20\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FE0E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fe0e(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe0e_0010\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "movs	r4, r0\n"
        "L_open_cfw_runtime_am015_4fe0e_0010:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe0e_002e\n"
        "ldr.w	r0, [pc, #0x16c]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x168]\n"
        "movw	r2, #0x371\n"
        "ldr.w	r1, [pc, #0x148]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am015_4fe0e_006e\n"
        "L_open_cfw_runtime_am015_4fe0e_002e:\n"
        "str.w	r5, [r4, #0x300]\n"
        "ldr.w	r0, [r4, #0x2d4]\n"
        "cmp	r0, #4\n"
        "bne	L_open_cfw_runtime_am015_4fe0e_006e\n"
        "ldr.w	r0, [r4, #0x2b8]\n"
        "ldr	r0, [r0]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44ddea\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe0e_006e\n"
        "ldr.w	r0, [r4, #0x2b8]\n"
        "ldr	r0, [r0, #4]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44ddea\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe0e_006e\n"
        "ldr.w	r0, [r4, #0x2b8]\n"
        "ldr	r0, [r0, #8]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44ddea\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe0e_006e\n"
        "ldr.w	r0, [r4, #0x2b8]\n"
        "ldr	r0, [r0]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_482f8a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fe0e_006e:\n"
        "pop	{r0, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FE7E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fe7e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe7e_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fe7e_000a:\n"
        "ldr.w	r0, [r0, #0x300]\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FE8E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fe8e(void)
{
    __asm__ volatile(
        
        "push	{r2, r3, r4, lr}\n"
        "movs	r4, r1\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe8e_000c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fe8e_000c:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fe8e_002a\n"
        "ldr.w	r0, [pc, #0xf0]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0xf0]\n"
        "mov.w	r2, #0x3a4\n"
        "ldr.w	r1, [pc, #0xcc]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am015_4fe8e_0042\n"
        "L_open_cfw_runtime_am015_4fe8e_002a:\n"
        "uxtb	r4, r4\n"
        "cmp	r4, #0\n"
        "beq	L_open_cfw_runtime_am015_4fe8e_0034\n"
        "movs	r1, #1\n"
        "b	L_open_cfw_runtime_am015_4fe8e_0038\n"
        "L_open_cfw_runtime_am015_4fe8e_0034:\n"
        "movs.w	r1, #-1\n"
        "L_open_cfw_runtime_am015_4fe8e_0038:\n"
        "ldr.w	r2, [r0, #0x264]\n"
        "adds	r1, r1, r2\n"
        "str.w	r1, [r0, #0x264]\n"
        "L_open_cfw_runtime_am015_4fe8e_0042:\n"
        "pop	{r0, r1, r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FED2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4fed2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fed2_000a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4fed2_000a:\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4fed2_002a\n"
        "ldr.w	r0, [pc, #0xac]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0xb4]\n"
        "movw	r2, #0x3af\n"
        "ldr.w	r1, [pc, #0x8c]\n"
        "movs	r0, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4fed2_003a\n"
        "L_open_cfw_runtime_am015_4fed2_002a:\n"
        "ldr.w	r0, [r0, #0x264]\n"
        "cmp	r0, #1\n"
        "blt	L_open_cfw_runtime_am015_4fed2_0036\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am015_4fed2_0038\n"
        "L_open_cfw_runtime_am015_4fed2_0036:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am015_4fed2_0038:\n"
        "uxtb	r0, r0\n"
        "L_open_cfw_runtime_am015_4fed2_003a:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FF38_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4ff38(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44fa1a\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_4fc62\n"
        "bl .\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FFCC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4ffcc(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FFD0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4ffd0(void)
{
    __asm__ volatile(
        
        "ldr.w	r1, [pc, #0x2e0]\n"
        "ldr	r2, [r1, #0x6c]\n"
        "str	r2, [r0, #0x14]\n"
        "str	r0, [r1, #0x6c]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FFDC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4ffdc(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #0x14]\n"
        "ldr.w	r1, [pc, #0x2d4]\n"
        "str	r0, [r1, #0x6c]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_4FFE6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_4ffe6(void)
{
    __asm__ volatile(
        
        "push.w	{r4, r5, r6, r7, r8, sb, sl, fp, lr}\n"
        "sub	sp, #0x14\n"
        "movs	r4, r0\n"
        "mov	fp, r1\n"
        "mov	sl, r2\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am015_4ffe6_0014\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am015_4ffe6_00f8\n"
        "L_open_cfw_runtime_am015_4ffe6_0014:\n"
        "ldrb.w	r0, [fp, #0x18]\n"
        "lsls	r0, r0, #0x1f\n"
        "bpl	L_open_cfw_runtime_am015_4ffe6_0020\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am015_4ffe6_00f8\n"
        "L_open_cfw_runtime_am015_4ffe6_0020:\n"
        "mov	r0, sp\n"
        "movs	r1, r4\n"
        "movs	r2, #0x14\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_439c04\n"
        "bl .\n"
        "ldrb	r5, [r4, #0x14]\n"
        "ands	r5, r5, #1\n"
        "ldrb	r0, [r4, #0x14]\n"
        "orrs	r0, r0, #1\n"
        "strb	r0, [r4, #0x14]\n"
        "movs	r6, #1\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_450388\n"
        "bl .\n"
        "movs	r7, r0\n"
        "movs.w	r8, #0\n"
        "b	L_open_cfw_runtime_am015_4ffe6_0056\n"
        "L_open_cfw_runtime_am015_4ffe6_0048:\n"
        "b	L_open_cfw_runtime_am015_4ffe6_0052\n"
        "L_open_cfw_runtime_am015_4ffe6_004a:\n"
        "ldrb.w	r0, [fp, #0x18]\n"
        "lsls	r0, r0, #0x1f\n"
        "bmi	L_open_cfw_runtime_am015_4ffe6_00c8\n"
        "L_open_cfw_runtime_am015_4ffe6_0052:\n"
        "adds.w	r8, r8, #1\n"
        "L_open_cfw_runtime_am015_4ffe6_0056:\n"
        "cmp	r8, r7\n"
        "bhs	L_open_cfw_runtime_am015_4ffe6_00ca\n"
        "ldrb.w	r0, [fp, #0x18]\n"
        "lsls	r0, r0, #0x1f\n"
        "bmi	L_open_cfw_runtime_am015_4ffe6_00ca\n"
        "mov	r1, r8\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_450390\n"
        "bl .\n"
        "ldr.w	sb, [r0]\n"
        "ldr.w	r0, [sb]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4ffe6_0048\n"
        "mov	r0, sb\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_45037e\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_4ffe6_0052\n"
        "ldr.w	r0, [sb, #8]\n"
        "lsrs	r0, r0, #0xf\n"
        "ands	r0, r0, #1\n"
        "mov	r1, sl\n"
        "uxtb	r0, r0\n"
        "uxtb	r1, r1\n"
        "cmp	r0, r1\n"
        "bne	L_open_cfw_runtime_am015_4ffe6_0052\n"
        "ldr.w	r0, [sb, #8]\n"
        "bics	r0, r0, #0x8000\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4ffe6_00a8\n"
        "ldr.w	r1, [fp, #8]\n"
        "cmp	r0, r1\n"
        "bne	L_open_cfw_runtime_am015_4ffe6_0052\n"
        "L_open_cfw_runtime_am015_4ffe6_00a8:\n"
        "ldr.w	r0, [sb, #4]\n"
        "str.w	r0, [fp, #0xc]\n"
        "mov	r0, fp\n"
        "ldr.w	r1, [sb]\n"
        "blx	r1\n"
        "ldrb.w	r0, [fp, #0x18]\n"
        "ubfx	r0, r0, #1, #1\n"
        "uxtb	r0, r0\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_4ffe6_004a\n"
        "b	L_open_cfw_runtime_am015_4ffe6_00ca\n"
        "L_open_cfw_runtime_am015_4ffe6_00c8:\n"
        "movs	r6, #0\n"
        "L_open_cfw_runtime_am015_4ffe6_00ca:\n"
        "uxtb	r5, r5\n"
        "cmp	r5, #0\n"
        "beq	L_open_cfw_runtime_am015_4ffe6_00d6\n"
        "movs	r0, r6\n"
        "uxtb	r0, r0\n"
        "b	L_open_cfw_runtime_am015_4ffe6_00f8\n"
        "L_open_cfw_runtime_am015_4ffe6_00d6:\n"
        "ldrb.w	r0, [fp, #0x18]\n"
        "lsls	r0, r0, #0x1f\n"
        "bpl	L_open_cfw_runtime_am015_4ffe6_00e6\n"
        "mov	r0, sp\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_4502e0\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am015_4ffe6_00f4\n"
        "L_open_cfw_runtime_am015_4ffe6_00e6:\n"
        "ldrb	r0, [r4, #0x14]\n"
        "ands	r0, r0, #0xfe\n"
        "strb	r0, [r4, #0x14]\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_450346\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_4ffe6_00f4:\n"
        "movs	r0, r6\n"
        "uxtb	r0, r0\n"
        "L_open_cfw_runtime_am015_4ffe6_00f8:\n"
        "add	sp, #0x14\n"
        "pop.w	{r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_500E4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_500e4(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, r6, r7, lr}\n"
        "sub	sp, #0x10\n"
        "movs	r4, r0\n"
        "movs	r6, r1\n"
        "movs	r7, r2\n"
        "movs	r5, r3\n"
        "movs	r0, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44f718\n"
        "bl .\n"
        "str	r0, [sp, #0xc]\n"
        "ldr	r0, [sp, #0xc]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_500e4_0046\n"
        "ldr.w	r0, [pc, #0x1b8]\n"
        "str	r0, [sp, #8]\n"
        "ldr.w	r0, [pc, #0x1b4]\n"
        "str	r0, [sp, #4]\n"
        "ldr.w	r0, [pc, #0x1b4]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x1b0]\n"
        "movs	r2, #0x7c\n"
        "ldr.w	r1, [pc, #0x1b0]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_500e4_003c:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am015_500e4_003c\n"
        "L_open_cfw_runtime_am015_500e4_0046:\n"
        "ldr	r0, [sp, #0xc]\n"
        "str	r6, [r0]\n"
        "ldr	r0, [sp, #0xc]\n"
        "str	r7, [r0, #8]\n"
        "ldr	r0, [sp, #0xc]\n"
        "str	r5, [r0, #4]\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_450388\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_500e4_0066\n"
        "movs	r2, #4\n"
        "movs	r1, #1\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_4883fc\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_500e4_0066:\n"
        "add	r1, sp, #0xc\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_488506\n"
        "bl .\n"
        "ldr	r0, [sp, #0xc]\n"
        "add	sp, #0x14\n"
        "pop	{r4, r5, r6, r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_50158_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_50158(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_50158_0032\n"
        "ldr.w	r0, [pc, #0x158]\n"
        "str	r0, [sp, #8]\n"
        "ldr.w	r0, [pc, #0x164]\n"
        "str	r0, [sp, #4]\n"
        "ldr.w	r0, [pc, #0x154]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x15c]\n"
        "movs	r2, #0x9f\n"
        "ldr.w	r1, [pc, #0x150]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_50158_0028:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am015_50158_0028\n"
        "L_open_cfw_runtime_am015_50158_0032:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_450388\n"
        "bl .\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM015_50190_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am015_50190(void)
{
    __asm__ volatile(
        
        "push	{r5, r6, r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am015_50190_0032\n"
        "ldr.w	r0, [pc, #0x120]\n"
        "str	r0, [sp, #8]\n"
        "ldr.w	r0, [pc, #0x12c]\n"
        "str	r0, [sp, #4]\n"
        "ldr.w	r0, [pc, #0x11c]\n"
        "str	r0, [sp]\n"
        "ldr.w	r3, [pc, #0x128]\n"
        "movs	r2, #0xa5\n"
        "ldr.w	r1, [pc, #0x118]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am015_50190_0028:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am015_50190_0028\n"
        "L_open_cfw_runtime_am015_50190_0032:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am015_call_450390\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am015_50190_003e\n"
        "ldr	r0, [r0]\n"
        "b	L_open_cfw_runtime_am015_50190_0040\n"
        "L_open_cfw_runtime_am015_50190_003e:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am015_50190_0040:\n"
        "pop	{r1, r2, r3, pc}\n"
    
    );
}
#endif
