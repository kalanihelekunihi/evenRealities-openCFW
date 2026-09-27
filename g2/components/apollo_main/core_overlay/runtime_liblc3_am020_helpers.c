/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-020 retained island.
 */

#if defined(OPEN_CFW_AM020_52C66_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52c66(void)
{
    __asm__ volatile(
        
        "b.w	#0x4ba560\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52D42_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52d42(void)
{
    __asm__ volatile(
        
        "push	{r1, r2, r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am020_52d42_002c\n"
        "ldr	r0, [pc, #0x68]\n"
        "str	r0, [sp, #8]\n"
        "ldr	r0, [pc, #0x68]\n"
        "str	r0, [sp, #4]\n"
        "ldr	r0, [pc, #0x68]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x68]\n"
        "movw	r2, #0x165\n"
        "ldr	r1, [pc, #0x64]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44d25c\n"
        "bl .\n"
        "L_open_cfw_runtime_am020_52d42_0022:\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "b	L_open_cfw_runtime_am020_52d42_0022\n"
        "L_open_cfw_runtime_am020_52d42_002c:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_52dc8\n"
        "bl .\n"
        "movs	r5, r0\n"
        "movs	r0, #0\n"
        "str	r0, [sp]\n"
        "mov	r2, sp\n"
        "movs	r1, #0x1b\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_451670\n"
        "bl .\n"
        "ldr	r0, [r4, #8]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_52d42_0050\n"
        "ldr	r0, [sp]\n"
        "ldr	r1, [r4, #8]\n"
        "str	r0, [r1, #0x2c]\n"
        "b	L_open_cfw_runtime_am020_52d42_0062\n"
        "L_open_cfw_runtime_am020_52d42_0050:\n"
        "ldr	r0, [sp]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_52d42_0062\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_43e1fa\n"
        "bl .\n"
        "ldr	r0, [sp]\n"
        "ldr	r1, [r4, #8]\n"
        "str	r0, [r1, #0x2c]\n"
        "L_open_cfw_runtime_am020_52d42_0062:\n"
        "ldr	r0, [sp]\n"
        "cmp	r0, r5\n"
        "beq	L_open_cfw_runtime_am020_52d42_006e\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_440656\n"
        "bl .\n"
        "L_open_cfw_runtime_am020_52d42_006e:\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52DC8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52dc8(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #8]\n"
        "cmp	r0, #0\n"
        "itt	eq\n"
        "moveq	r0, #0\n"
        "bxeq	lr\n"
        "ldr	r0, [r0, #0x2c]\n"
        "nop\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52DD8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52dd8(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #8]\n"
        "cmp	r0, #0\n"
        "itt	eq\n"
        "moveq	r0, #0\n"
        "bxeq	lr\n"
        "ldrh	r0, [r0, #0x32]\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "ubfx	r0, r0, #0xa, #2\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52DF0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52df0(void)
{
    __asm__ volatile(
        
        "ldr	r2, [r2, #0x10]\n"
        "cmp	r2, #0\n"
        "it	eq\n"
        "beq.w	#0x44c47a\n"
        "push	{r4, lr}\n"
        "ldrb.w	r4, [r2, #0x38]\n"
        "cbz	r1, L_open_cfw_runtime_am020_52df0_002e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_7f25b0\n"
        "bl .\n"
        "muls	r0, r4, r0\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "ubfx	r4, r0, #8, #8\n"
        "L_open_cfw_runtime_am020_52df0_002e:\n"
        "mov	r0, r4\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52E22_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52e22(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r7, lr}\n"
        "ldr	r2, [r2, #0x10]\n"
        "mov	r4, r3\n"
        "cbz	r2, L_open_cfw_runtime_am020_52e22_0016\n"
        "ldr.w	r5, [r2, #0x39]\n"
        "cbz	r1, L_open_cfw_runtime_am020_52e22_001c\n"
        "mov	r2, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44c54a\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am020_52e22_001a\n"
        "L_open_cfw_runtime_am020_52e22_0016:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44c582\n"
        "bl .\n"
        "L_open_cfw_runtime_am020_52e22_001a:\n"
        "mov	r5, r0\n"
        "L_open_cfw_runtime_am020_52e22_001c:\n"
        "ubfx	r1, r5, #8, #8\n"
        "ubfx	r2, r5, #0x10, #8\n"
        "uxtb	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_441068\n"
        "bl .\n"
        "lsrs	r2, r5, #0x18\n"
        "mov	r1, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_482dd8\n"
        "bl .\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "pop	{r4, r5, r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52E68_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52e68(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "ldr	r2, [r2, #0x10]\n"
        "mov	r4, r3\n"
        "ldr	r5, [sp, #0x10]\n"
        "cbz	r2, L_open_cfw_runtime_am020_52e68_0018\n"
        "ldr.w	r6, [r2, #0x39]\n"
        "cbz	r1, L_open_cfw_runtime_am020_52e68_001e\n"
        "mov	r2, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44c54a\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am020_52e68_001c\n"
        "L_open_cfw_runtime_am020_52e68_0018:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44c582\n"
        "bl .\n"
        "L_open_cfw_runtime_am020_52e68_001c:\n"
        "mov	r6, r0\n"
        "L_open_cfw_runtime_am020_52e68_001e:\n"
        "lsls	r0, r5, #0x18\n"
        "beq	L_open_cfw_runtime_am020_52e68_0044\n"
        "cmp.w	r6, #0x1000000\n"
        "blo	L_open_cfw_runtime_am020_52e68_0044\n"
        "mov	r0, r4\n"
        "mov	r1, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_440fde\n"
        "bl .\n"
        "mov	r1, r0\n"
        "mov	r0, r6\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "pop.w	{r4, r5, r6, lr}\n"
        "b.w	#0x482ef6\n"
        "L_open_cfw_runtime_am020_52e68_0044:\n"
        "cmp.w	r6, #0x1000000\n"
        "blo	L_open_cfw_runtime_am020_52e68_0056\n"
        "mov	r0, r6\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "pop	{r4, r5, r6, pc}\n"
        "L_open_cfw_runtime_am020_52e68_0056:\n"
        "mov	r0, r4\n"
        "mov	r1, r5\n"
        "nop\n"
        "nop\n"
        "nop\n"
        "pop.w	{r4, r5, r6, lr}\n"
        "b.w	#0x440fde\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52ED0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52ed0(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "mov	r2, r1\n"
        "movs	r1, #0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_454746\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52EDC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52edc(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52edc_0010\n"
        "ldr.w	r0, [pc, #0x170]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_482cd8\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am020_52edc_001a\n"
        "L_open_cfw_runtime_am020_52edc_0010:\n"
        "movs	r1, r0\n"
        "ldr.w	r0, [pc, #0x164]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_482cf0\n"
        "bl .\n"
        "L_open_cfw_runtime_am020_52edc_001a:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52EF8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52ef8(void)
{
    __asm__ volatile(
        
        "ldr.w	r0, [pc, #0x15c]\n"
        "ldr	r0, [r0, #0x50]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52F00_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52f00(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52f00_0008\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52f00_000a\n"
        "L_open_cfw_runtime_am020_52f00_0008:\n"
        "ldrb	r0, [r0]\n"
        "L_open_cfw_runtime_am020_52f00_000a:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52F0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52f0c(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52f0c_0008\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52f0c_000a\n"
        "L_open_cfw_runtime_am020_52f0c_0008:\n"
        "ldrb	r0, [r0, #8]\n"
        "L_open_cfw_runtime_am020_52f0c_000a:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52F18_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52f18(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52f18_0008\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52f18_000c\n"
        "L_open_cfw_runtime_am020_52f18_0008:\n"
        "ldr.w	r0, [r0, #0xb8]\n"
        "L_open_cfw_runtime_am020_52f18_000c:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52F26_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52f26(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r5, r1\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_52f26_0010\n"
        "movs	r1, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_5305c\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am020_52f26_0036\n"
        "L_open_cfw_runtime_am020_52f26_0010:\n"
        "movs	r0, #0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_52edc\n"
        "bl .\n"
        "movs	r4, r0\n"
        "b	L_open_cfw_runtime_am020_52f26_002a\n"
        "L_open_cfw_runtime_am020_52f26_001a:\n"
        "movs	r1, r5\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_5305c\n"
        "bl .\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_52edc\n"
        "bl .\n"
        "movs	r4, r0\n"
        "L_open_cfw_runtime_am020_52f26_002a:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am020_52f26_001a\n"
        "movs	r0, #0\n"
        "ldr.w	r1, [pc, #0x100]\n"
        "str	r0, [r1, #0x54]\n"
        "L_open_cfw_runtime_am020_52f26_0036:\n"
        "pop	{r0, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52F5E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52f5e(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52f5e_000e\n"
        "movs	r0, #0\n"
        "str	r0, [r1]\n"
        "movs	r0, #0\n"
        "str	r0, [r1, #4]\n"
        "b	L_open_cfw_runtime_am020_52f5e_002c\n"
        "L_open_cfw_runtime_am020_52f5e_000e:\n"
        "ldrb	r2, [r0]\n"
        "cmp	r2, #1\n"
        "beq	L_open_cfw_runtime_am020_52f5e_0024\n"
        "ldrb	r2, [r0]\n"
        "cmp	r2, #3\n"
        "beq	L_open_cfw_runtime_am020_52f5e_0024\n"
        "movs.w	r0, #-1\n"
        "str	r0, [r1]\n"
        "str	r0, [r1, #4]\n"
        "b	L_open_cfw_runtime_am020_52f5e_002c\n"
        "L_open_cfw_runtime_am020_52f5e_0024:\n"
        "ldr	r2, [r0, #0x30]\n"
        "str	r2, [r1]\n"
        "ldr	r0, [r0, #0x34]\n"
        "str	r0, [r1, #4]\n"
        "L_open_cfw_runtime_am020_52f5e_002c:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52F8C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52f8c(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52f8c_0008\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52f8c_0020\n"
        "L_open_cfw_runtime_am020_52f8c_0008:\n"
        "ldrb	r1, [r0]\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am020_52f8c_0018\n"
        "ldrb	r1, [r0]\n"
        "cmp	r1, #3\n"
        "beq	L_open_cfw_runtime_am020_52f8c_0018\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52f8c_0020\n"
        "L_open_cfw_runtime_am020_52f8c_0018:\n"
        "ldrb.w	r0, [r0, #0xa8]\n"
        "ands	r0, r0, #0xf\n"
        "L_open_cfw_runtime_am020_52f8c_0020:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52FAE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52fae(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am020_52fae_0008\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52fae_001a\n"
        "L_open_cfw_runtime_am020_52fae_0008:\n"
        "ldrb	r1, [r0]\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am020_52fae_0018\n"
        "ldrb	r1, [r0]\n"
        "cmp	r1, #3\n"
        "beq	L_open_cfw_runtime_am020_52fae_0018\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am020_52fae_001a\n"
        "L_open_cfw_runtime_am020_52fae_0018:\n"
        "ldr	r0, [r0, #0x70]\n"
        "L_open_cfw_runtime_am020_52fae_001a:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52FCA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52fca(void)
{
    __asm__ volatile(
        
        "movs	r2, #0\n"
        "str	r2, [r1]\n"
        "movs	r2, #0\n"
        "str	r2, [r1, #4]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_52fca_0020\n"
        "ldrb	r2, [r0]\n"
        "cmp	r2, #1\n"
        "beq	L_open_cfw_runtime_am020_52fca_0018\n"
        "ldrb	r2, [r0]\n"
        "cmp	r2, #3\n"
        "bne	L_open_cfw_runtime_am020_52fca_0020\n"
        "L_open_cfw_runtime_am020_52fca_0018:\n"
        "ldr	r2, [r0, #0x48]\n"
        "str	r2, [r1]\n"
        "ldr	r0, [r0, #0x4c]\n"
        "str	r0, [r1, #4]\n"
        "L_open_cfw_runtime_am020_52fca_0020:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52FEC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52fec(void)
{
    __asm__ volatile(
        
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_52fec_000c\n"
        "ldrb	r1, [r0, #0xb]\n"
        "orrs	r1, r1, #8\n"
        "strb	r1, [r0, #0xb]\n"
        "L_open_cfw_runtime_am020_52fec_000c:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_52FFA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_52ffa(void)
{
    __asm__ volatile(
        
        "ldr.w	r0, [pc, #0x5c]\n"
        "ldr	r0, [r0, #0x54]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_53002_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_53002(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, r6, lr}\n"
        "sub	sp, #0x1c\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r6, r2\n"
        "movs	r1, #0x1c\n"
        "mov	r0, sp\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_52ed0\n"
        "bl .\n"
        "str	r5, [sp, #8]\n"
        "str	r4, [sp]\n"
        "str	r4, [sp, #4]\n"
        "str	r6, [sp, #0x10]\n"
        "movs	r2, #1\n"
        "mov	r1, sp\n"
        "adds.w	r0, r4, #0xc0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44ffe6\n"
        "bl .\n"
        "movs	r1, r0\n"
        "uxtb	r1, r1\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am020_53002_0032\n"
        "uxtb	r0, r0\n"
        "b	L_open_cfw_runtime_am020_53002_004c\n"
        "L_open_cfw_runtime_am020_53002_0032:\n"
        "movs	r2, #0\n"
        "mov	r1, sp\n"
        "adds.w	r0, r4, #0xc0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44ffe6\n"
        "bl .\n"
        "movs	r1, r0\n"
        "uxtb	r1, r1\n"
        "cmp	r1, #1\n"
        "beq	L_open_cfw_runtime_am020_53002_004a\n"
        "uxtb	r0, r0\n"
        "b	L_open_cfw_runtime_am020_53002_004c\n"
        "L_open_cfw_runtime_am020_53002_004a:\n"
        "uxtb	r0, r0\n"
        "L_open_cfw_runtime_am020_53002_004c:\n"
        "add	sp, #0x20\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_5305C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_5305c(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "movs	r5, r0\n"
        "movs	r4, r1\n"
        "movs	r0, #0\n"
        "movs	r0, #0\n"
        "ldrb	r0, [r5, #0xb]\n"
        "orrs	r0, r0, #2\n"
        "strb	r0, [r5, #0xb]\n"
        "ldr	r0, [pc, #0x88]\n"
        "ldr	r1, [r0, #0x50]\n"
        "cmp	r1, r5\n"
        "bne	L_open_cfw_runtime_am020_5305c_001e\n"
        "movs	r1, #0\n"
        "str	r1, [r0, #0x54]\n"
        "L_open_cfw_runtime_am020_5305c_001e:\n"
        "ldrb	r0, [r5]\n"
        "cmp	r0, #1\n"
        "beq	L_open_cfw_runtime_am020_5305c_002a\n"
        "ldrb	r0, [r5]\n"
        "cmp	r0, #2\n"
        "bne	L_open_cfw_runtime_am020_5305c_0098\n"
        "L_open_cfw_runtime_am020_5305c_002a:\n"
        "cmp	r4, #0\n"
        "beq	L_open_cfw_runtime_am020_5305c_0034\n"
        "ldr	r0, [r5, #0x74]\n"
        "cmp	r0, r4\n"
        "bne	L_open_cfw_runtime_am020_5305c_0038\n"
        "L_open_cfw_runtime_am020_5305c_0034:\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #0x74]\n"
        "L_open_cfw_runtime_am020_5305c_0038:\n"
        "ldr	r0, [r5, #0x68]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_5305c_005a\n"
        "ldr	r6, [r5, #0x68]\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #0x68]\n"
        "movs	r2, r5\n"
        "movs	r1, #0x17\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_451670\n"
        "bl .\n"
        "movs	r2, r6\n"
        "movs	r1, #0x17\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_53002\n"
        "bl .\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am020_5305c_005a:\n"
        "cmp	r4, #0\n"
        "beq	L_open_cfw_runtime_am020_5305c_0064\n"
        "ldr	r0, [r5, #0x6c]\n"
        "cmp	r0, r4\n"
        "bne	L_open_cfw_runtime_am020_5305c_0068\n"
        "L_open_cfw_runtime_am020_5305c_0064:\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #0x6c]\n"
        "L_open_cfw_runtime_am020_5305c_0068:\n"
        "ldr	r0, [r5, #0x70]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am020_5305c_008a\n"
        "ldr	r6, [r5, #0x70]\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #0x70]\n"
        "movs	r2, r5\n"
        "movs	r1, #0x17\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_451670\n"
        "bl .\n"
        "movs	r2, r6\n"
        "movs	r1, #0x17\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_53002\n"
        "bl .\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am020_5305c_008a:\n"
        "cmp	r4, #0\n"
        "beq	L_open_cfw_runtime_am020_5305c_0094\n"
        "ldr	r0, [r5, #0x78]\n"
        "cmp	r0, r4\n"
        "bne	L_open_cfw_runtime_am020_5305c_0098\n"
        "L_open_cfw_runtime_am020_5305c_0094:\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #0x78]\n"
        "L_open_cfw_runtime_am020_5305c_0098:\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_530FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_530fc(void)
{
    __asm__ volatile(
        
        "ldr	r2, [r1]\n"
        "str	r2, [r0]\n"
        "ldr	r2, [r1, #4]\n"
        "str	r2, [r0, #4]\n"
        "ldr	r2, [r1, #8]\n"
        "str	r2, [r0, #8]\n"
        "ldr	r1, [r1, #0xc]\n"
        "str	r1, [r0, #0xc]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_5310E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_5310e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "mov	r2, r1\n"
        "movs	r1, #0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_454746\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_5311A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_5311a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x6e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_53124_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_53124(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x6f\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_5312E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_5312e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x70\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_53138_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_53138(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x71\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_53142_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_53142(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x72\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_5314C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_5314c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x73\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_53156_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_53156(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0x74\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM020_53160_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am020_53160(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am020_call_44bdea\n"
        "bl .\n"
        "pop	{r7, pc}\n"
    
    );
}
#endif
