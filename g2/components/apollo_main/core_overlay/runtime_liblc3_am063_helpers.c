/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-063 retained island.
 */

#if defined(OPEN_CFW_AM063_CFD84_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfd84(void)
{
    __asm__ volatile(
        
        "push	{r4}\n"
        "ldr	r3, [r0, #4]\n"
        "ldr.w	r2, [pc, #0x878]\n"
        "ldr	r4, [r2]\n"
        "ldr.w	r2, [pc, #0x948]\n"
        "ldr	r2, [r2]\n"
        "orrs	r4, r2\n"
        "ands	r3, r4\n"
        "orrs	r1, r3\n"
        "str	r1, [r0, #4]\n"
        "pop	{r4}\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDA0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfda0(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am063_cfda0_000e\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am063_cfda0_0010\n"
        "L_open_cfw_runtime_am063_cfda0_000e:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am063_cfda0_0010:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDB4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfdb4(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #4]\n"
        "ldr.w	r1, [pc, #0x84c]\n"
        "ldr	r1, [r1]\n"
        "ands	r0, r1\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDC0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfdc0(void)
{
    __asm__ volatile(
        
        "ldr	r2, [r0, #4]\n"
        "ldr.w	r1, [pc, #0x840]\n"
        "ldr	r1, [r1]\n"
        "orrs	r2, r1\n"
        "str	r2, [r0, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDCE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfdce(void)
{
    __asm__ volatile(
        
        "ldr	r2, [r0, #4]\n"
        "ldr.w	r1, [pc, #0x830]\n"
        "ldr	r1, [r1]\n"
        "bics	r2, r1\n"
        "str	r2, [r0, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDDC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfddc(void)
{
    __asm__ volatile(
        
        "ldr	r0, [r0, #4]\n"
        "ldr.w	r1, [pc, #0x8f8]\n"
        "ldr	r1, [r1]\n"
        "ands	r0, r1\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDE8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfde8(void)
{
    __asm__ volatile(
        
        "ldr	r2, [r0, #4]\n"
        "ldr.w	r1, [pc, #0x8ec]\n"
        "ldr	r1, [r1]\n"
        "orrs	r2, r1\n"
        "str	r2, [r0, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFDF6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfdf6(void)
{
    __asm__ volatile(
        
        "ldr	r2, [r0, #4]\n"
        "ldr.w	r1, [pc, #0x8dc]\n"
        "ldr	r1, [r1]\n"
        "bics	r2, r1\n"
        "str	r2, [r0, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE04_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe04(void)
{
    __asm__ volatile(
        
        "ldr.w	r1, [pc, #0x8d4]\n"
        "ldr	r1, [r1]\n"
        "rsbs	r1, r1, #0\n"
        "add	r0, r1\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE10_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe10(void)
{
    __asm__ volatile(
        
        "ldr.w	r1, [pc, #0x8c8]\n"
        "ldr	r1, [r1]\n"
        "add	r0, r1\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE1A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe1a(void)
{
    __asm__ volatile(
        
        "adds	r0, r1, r0\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE1E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe1e(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfddc\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am063_cfe1e_0022\n"
        "movw	r2, #0x1b1\n"
        "ldr.w	r1, [pc, #0x878]\n"
        "ldr.w	r0, [pc, #0x8a8]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_cfe1e_0022:\n"
        "ldr	r0, [r4]\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE44_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe44(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "movs	r5, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe10\n"
        "bl .\n"
        "ldr.w	r1, [pc, #0x858]\n"
        "ldr	r1, [r1]\n"
        "subs	r5, r5, r1\n"
        "movs	r1, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe1a\n"
        "bl .\n"
        "movs	r5, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfda0\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am063_cfe44_0040\n"
        "mov.w	r2, #0x1ba\n"
        "ldr.w	r1, [pc, #0x834]\n"
        "ldr.w	r0, [pc, #0x868]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_cfe44_0040:\n"
        "movs	r0, r5\n"
        "pop	{r1, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE88_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe88(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe44\n"
        "bl .\n"
        "str	r4, [r0]\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFE96_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfe96(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe88\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfde8\n"
        "bl .\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfdc0\n"
        "bl .\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFEAC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfeac(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe44\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfdf6\n"
        "bl .\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfdce\n"
        "bl .\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFEC2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfec2(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "subs	r0, r5, #1\n"
        "tst	r5, r0\n"
        "beq	L_open_cfw_runtime_am063_cfec2_0020\n"
        "movw	r2, #0x1d7\n"
        "ldr.w	r1, [pc, #0x7d8]\n"
        "ldr.w	r0, [pc, #0x92c]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_cfec2_0020:\n"
        "adds	r4, r5, r4\n"
        "subs	r4, r4, #1\n"
        "subs	r5, r5, #1\n"
        "bics	r4, r5\n"
        "movs	r0, r4\n"
        "pop	{r1, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFEEE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cfeee(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "subs	r0, r5, #1\n"
        "tst	r5, r0\n"
        "beq	L_open_cfw_runtime_am063_cfeee_0020\n"
        "movw	r2, #0x1dd\n"
        "ldr.w	r1, [pc, #0x7ac]\n"
        "ldr.w	r0, [pc, #0x900]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_cfeee_0020:\n"
        "subs	r5, r5, #1\n"
        "ands	r5, r4\n"
        "subs	r4, r4, r5\n"
        "movs	r0, r4\n"
        "pop	{r1, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFF18_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cff18(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "adds	r4, r1, r4\n"
        "subs	r4, r4, #1\n"
        "subs	r0, r1, #1\n"
        "bics	r4, r0\n"
        "subs	r0, r1, #1\n"
        "tst	r1, r0\n"
        "beq	L_open_cfw_runtime_am063_cff18_0026\n"
        "movw	r2, #0x1e5\n"
        "ldr.w	r1, [pc, #0x77c]\n"
        "ldr.w	r0, [pc, #0x8d0]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_cff18_0026:\n"
        "movs	r0, r4\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFF42_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cff42(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, #0\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am063_cff42_0026\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfec2\n"
        "bl .\n"
        "ldr.w	r1, [pc, #0x798]\n"
        "ldr	r1, [r1]\n"
        "cmp	r0, r1\n"
        "bhs	L_open_cfw_runtime_am063_cff42_0026\n"
        "ldr.w	r1, [pc, #0x8f8]\n"
        "ldr	r2, [r1]\n"
        "cmp	r2, r0\n"
        "bhs	L_open_cfw_runtime_am063_cff42_0024\n"
        "movs	r4, r0\n"
        "b	L_open_cfw_runtime_am063_cff42_0026\n"
        "L_open_cfw_runtime_am063_cff42_0024:\n"
        "ldr	r4, [r1]\n"
        "L_open_cfw_runtime_am063_cff42_0026:\n"
        "movs	r0, r4\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFF6C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cff6c(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r6, r2\n"
        "cmp	r4, #0x80\n"
        "bhs	L_open_cfw_runtime_am063_cff6c_0016\n"
        "movs	r0, #0\n"
        "movs	r1, #4\n"
        "sdiv	r4, r4, r1\n"
        "b	L_open_cfw_runtime_am063_cff6c_0028\n"
        "L_open_cfw_runtime_am063_cff6c_0016:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd66\n"
        "bl .\n"
        "adds.w	r1, r0, #0xfb\n"
        "lsrs	r4, r1\n"
        "eors	r4, r4, #0x20\n"
        "subs	r0, r0, #6\n"
        "L_open_cfw_runtime_am063_cff6c_0028:\n"
        "str	r0, [r5]\n"
        "str	r4, [r6]\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFF9A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cff9a(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, r6, r7, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r6, r2\n"
        "cmp	r4, #0x80\n"
        "blo	L_open_cfw_runtime_am063_cff9a_001c\n"
        "movs	r7, #1\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd66\n"
        "bl .\n"
        "subs	r0, r0, #5\n"
        "lsls	r7, r0\n"
        "subs	r7, r7, #1\n"
        "adds	r4, r7, r4\n"
        "L_open_cfw_runtime_am063_cff9a_001c:\n"
        "movs	r2, r6\n"
        "movs	r1, r5\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cff6c\n"
        "bl .\n"
        "pop	{r0, r4, r5, r6, r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_CFFC2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_cffc2(void)
{
    __asm__ volatile(
        
        "push.w	{r4, r5, r6, r7, r8, lr}\n"
        "movs	r6, r0\n"
        "mov	r8, r1\n"
        "movs	r7, r2\n"
        "ldr.w	r5, [r8]\n"
        "ldr	r4, [r7]\n"
        "movs.w	r0, #-1\n"
        "add.w	r1, r6, r5, lsl #2\n"
        "ldr	r1, [r1, #0x14]\n"
        "lsls.w	r4, r0, r4\n"
        "ands	r4, r1\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am063_cffc2_0048\n"
        "ldr	r1, [r6, #0x10]\n"
        "adds	r5, r5, #1\n"
        "lsls.w	r5, r0, r5\n"
        "ands	r5, r1\n"
        "cmp	r5, #0\n"
        "bne	L_open_cfw_runtime_am063_cffc2_0036\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am063_cffc2_0074\n"
        "L_open_cfw_runtime_am063_cffc2_0036:\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd56\n"
        "bl .\n"
        "movs	r5, r0\n"
        "str.w	r5, [r8]\n"
        "add.w	r0, r6, r5, lsl #2\n"
        "ldr	r4, [r0, #0x14]\n"
        "L_open_cfw_runtime_am063_cffc2_0048:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am063_cffc2_0060\n"
        "mov.w	r2, #0x238\n"
        "ldr.w	r1, [pc, #0x698]\n"
        "ldr.w	r0, [pc, #0x840]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_cffc2_0060:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd56\n"
        "bl .\n"
        "str	r0, [r7]\n"
        "lsls	r5, r5, #7\n"
        "add.w	r1, r6, r5\n"
        "add.w	r0, r1, r0, lsl #2\n"
        "ldr	r0, [r0, #0x74]\n"
        "L_open_cfw_runtime_am063_cffc2_0074:\n"
        "pop.w	{r4, r5, r6, r7, r8, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D003A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d003a(void)
{
    __asm__ volatile(
        
        "push.w	{r3, r4, r5, r6, r7, r8, sb, lr}\n"
        "movs	r6, r0\n"
        "mov	sb, r1\n"
        "movs	r7, r2\n"
        "mov	r8, r3\n"
        "ldr.w	r5, [sb, #0xc]\n"
        "ldr.w	r4, [sb, #8]\n"
        "cmp	r5, #0\n"
        "bne	L_open_cfw_runtime_am063_d003a_002c\n"
        "movw	r2, #0x245\n"
        "ldr.w	r1, [pc, #0x654]\n"
        "ldr.w	r0, [pc, #0x800]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d003a_002c:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am063_d003a_0044\n"
        "movw	r2, #0x246\n"
        "ldr.w	r1, [pc, #0x63c]\n"
        "ldr.w	r0, [pc, #0x8d8]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d003a_0044:\n"
        "str	r5, [r4, #0xc]\n"
        "str	r4, [r5, #8]\n"
        "lsls	r0, r7, #7\n"
        "add	r0, r6\n"
        "add.w	r0, r0, r8, lsl #2\n"
        "ldr	r0, [r0, #0x74]\n"
        "cmp	r0, sb\n"
        "bne	L_open_cfw_runtime_am063_d003a_0092\n"
        "lsls	r0, r7, #7\n"
        "add	r0, r6\n"
        "add.w	r0, r0, r8, lsl #2\n"
        "str	r4, [r0, #0x74]\n"
        "cmp	r4, r6\n"
        "bne	L_open_cfw_runtime_am063_d003a_0092\n"
        "movs	r1, #1\n"
        "add.w	r0, r6, r7, lsl #2\n"
        "ldr	r0, [r0, #0x14]\n"
        "lsls.w	r8, r1, r8\n"
        "bics.w	r8, r0, r8\n"
        "add.w	r0, r6, r7, lsl #2\n"
        "str.w	r8, [r0, #0x14]\n"
        "add.w	r0, r6, r7, lsl #2\n"
        "ldr	r0, [r0, #0x14]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am063_d003a_0092\n"
        "ldr	r0, [r6, #0x10]\n"
        "lsls.w	r7, r1, r7\n"
        "bics.w	r7, r0, r7\n"
        "str	r7, [r6, #0x10]\n"
        "L_open_cfw_runtime_am063_d003a_0092:\n"
        "pop.w	{r0, r4, r5, r6, r7, r8, sb, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D00D0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d00d0(void)
{
    __asm__ volatile(
        
        "push.w	{r4, r5, r6, r7, r8, lr}\n"
        "movs	r6, r0\n"
        "movs	r4, r1\n"
        "movs	r7, r2\n"
        "mov	r8, r3\n"
        "lsls	r0, r7, #7\n"
        "add	r0, r6\n"
        "add.w	r0, r0, r8, lsl #2\n"
        "ldr	r5, [r0, #0x74]\n"
        "cmp	r5, #0\n"
        "bne	L_open_cfw_runtime_am063_d00d0_002e\n"
        "movw	r2, #0x261\n"
        "ldr.w	r1, [pc, #0x5bc]\n"
        "ldr.w	r0, [pc, #0x76c]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d00d0_002e:\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am063_d00d0_0046\n"
        "movw	r2, #0x262\n"
        "ldr.w	r1, [pc, #0x5a4]\n"
        "ldr.w	r0, [pc, #0x758]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d00d0_0046:\n"
        "str	r5, [r4, #8]\n"
        "str	r6, [r4, #0xc]\n"
        "str	r4, [r5, #0xc]\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe10\n"
        "bl .\n"
        "movs	r5, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe10\n"
        "bl .\n"
        "movs	r1, #4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cff18\n"
        "bl .\n"
        "cmp	r5, r0\n"
        "beq	L_open_cfw_runtime_am063_d00d0_0078\n"
        "mov.w	r2, #0x268\n"
        "ldr.w	r1, [pc, #0x570]\n"
        "ldr.w	r0, [pc, #0x810]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d00d0_0078:\n"
        "lsls	r0, r7, #7\n"
        "add	r0, r6\n"
        "add.w	r0, r0, r8, lsl #2\n"
        "str	r4, [r0, #0x74]\n"
        "movs	r1, #1\n"
        "ldr	r2, [r6, #0x10]\n"
        "lsls.w	r0, r1, r7\n"
        "orrs	r2, r0\n"
        "str	r2, [r6, #0x10]\n"
        "add.w	r0, r6, r7, lsl #2\n"
        "ldr	r0, [r0, #0x14]\n"
        "lsls.w	r8, r1, r8\n"
        "orrs.w	r8, r8, r0\n"
        "add.w	r0, r6, r7, lsl #2\n"
        "str.w	r8, [r0, #0x14]\n"
        "pop.w	{r4, r5, r6, r7, r8, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D0178_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d0178(void)
{
    __asm__ volatile(
        
        "push	{r1, r2, r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "mov	r2, sp\n"
        "add	r1, sp, #4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cff6c\n"
        "bl .\n"
        "ldr	r3, [sp]\n"
        "ldr	r2, [sp, #4]\n"
        "movs	r1, r5\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_d003a\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D019A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d019a(void)
{
    __asm__ volatile(
        
        "push	{r1, r2, r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "mov	r2, sp\n"
        "add	r1, sp, #4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cff6c\n"
        "bl .\n"
        "ldr	r3, [sp]\n"
        "ldr	r2, [sp, #4]\n"
        "movs	r1, r5\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_d00d0\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D01BC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d01bc(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "adds	r4, #0x10\n"
        "cmp	r0, r4\n"
        "blo	L_open_cfw_runtime_am063_d01bc_0012\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am063_d01bc_0014\n"
        "L_open_cfw_runtime_am063_d01bc_0012:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am063_d01bc_0014:\n"
        "uxtb	r0, r0\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D01D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d01d4(void)
{
    __asm__ volatile(
        
        "push.w	{r3, r4, r5, r6, r7, r8, sb, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe10\n"
        "bl .\n"
        "ldr.w	r7, [pc, #0x4cc]\n"
        "ldr	r1, [r7]\n"
        "subs	r1, r5, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe1a\n"
        "bl .\n"
        "movs	r6, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "mov	r8, r0\n"
        "subs.w	r8, r8, r5\n"
        "ldr	r0, [r7]\n"
        "subs.w	r8, r8, r0\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe10\n"
        "bl .\n"
        "mov	sb, r0\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe10\n"
        "bl .\n"
        "movs	r1, #4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cff18\n"
        "bl .\n"
        "cmp	sb, r0\n"
        "beq	L_open_cfw_runtime_am063_d01d4_005a\n"
        "movw	r2, #0x291\n"
        "ldr.w	r1, [pc, #0x48c]\n"
        "ldr.w	r0, [pc, #0x730]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d01d4_005a:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "adds.w	r2, r5, r8\n"
        "ldr	r1, [r7]\n"
        "adds	r2, r1, r2\n"
        "cmp	r0, r2\n"
        "beq	L_open_cfw_runtime_am063_d01d4_0080\n"
        "movw	r2, #0x293\n"
        "ldr.w	r1, [pc, #0x464]\n"
        "ldr.w	r0, [pc, #0x70c]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d01d4_0080:\n"
        "mov	r1, r8\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfd84\n"
        "bl .\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "ldr.w	r1, [pc, #0x5f0]\n"
        "ldr	r1, [r1]\n"
        "cmp	r0, r1\n"
        "bhs	L_open_cfw_runtime_am063_d01d4_00ac\n"
        "movw	r2, #0x295\n"
        "ldr.w	r1, [pc, #0x438]\n"
        "ldr.w	r0, [pc, #0x6e4]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d01d4_00ac:\n"
        "movs	r1, r5\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfd84\n"
        "bl .\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe96\n"
        "bl .\n"
        "movs	r0, r6\n"
        "pop.w	{r1, r4, r5, r6, r7, r8, sb, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D0294_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d0294(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfda0\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am063_d0294_0024\n"
        "mov.w	r2, #0x2a0\n"
        "ldr.w	r1, [pc, #0x400]\n"
        "ldr.w	r0, [pc, #0x6b0]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d0294_0024:\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4cfd70\n"
        "bl .\n"
        "ldr	r1, [r4, #4]\n"
        "adds	r0, r0, r1\n"
        "ldr.w	r1, [pc, #0x6a0]\n"
        "ldr	r1, [r1]\n"
        "adds	r0, r1, r0\n"
        "str	r0, [r4, #4]\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe88\n"
        "bl .\n"
        "movs	r0, r4\n"
        "pop	{r1, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D02D6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d02d6(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "movs	r5, r0\n"
        "movs	r6, r1\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfddc\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am063_d02d6_0060\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe1e\n"
        "bl .\n"
        "movs	r4, r0\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am063_d02d6_0030\n"
        "movw	r2, #0x2ad\n"
        "ldr.w	r1, [pc, #0x3b4]\n"
        "ldr.w	r0, [pc, #0x66c]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d02d6_0030:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfdb4\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am063_d02d6_004e\n"
        "movw	r2, #0x2ae\n"
        "ldr.w	r1, [pc, #0x394]\n"
        "ldr.w	r0, [pc, #0x650]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d02d6_004e:\n"
        "movs	r1, r4\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_d0178\n"
        "bl .\n"
        "movs	r1, r6\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_d0294\n"
        "bl .\n"
        "movs	r6, r0\n"
        "L_open_cfw_runtime_am063_d02d6_0060:\n"
        "movs	r0, r6\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM063_D033A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am063_d033a(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "movs	r5, r0\n"
        "movs	r6, r1\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfe44\n"
        "bl .\n"
        "movs	r4, r0\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am063_d033a_0026\n"
        "movw	r2, #0x2ba\n"
        "ldr.w	r1, [pc, #0x358]\n"
        "ldr.w	r0, [pc, #0x618]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d033a_0026:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfdb4\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am063_d033a_0060\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_cfda0\n"
        "bl .\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am063_d033a_004e\n"
        "movw	r2, #0x2be\n"
        "ldr.w	r1, [pc, #0x330]\n"
        "ldr.w	r0, [pc, #0x5f4]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_call_4d09b4\n"
        "bl .\n"
        "nop.w\n"
        "L_open_cfw_runtime_am063_d033a_004e:\n"
        "movs	r1, r4\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_d0178\n"
        "bl .\n"
        "movs	r1, r4\n"
        "movs	r0, r6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am063_d0294\n"
        "bl .\n"
        "movs	r6, r0\n"
        "L_open_cfw_runtime_am063_d033a_0060:\n"
        "movs	r0, r6\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif
