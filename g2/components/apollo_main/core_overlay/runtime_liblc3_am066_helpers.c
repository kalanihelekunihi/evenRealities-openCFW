/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-066 retained island.
 */

#if defined(OPEN_CFW_AM066_D4354_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4354(void)
{
    __asm__ volatile(
        
        "vmov	d0, r0, r1\n"
        "vmov	d1, r2, r3\n"
        "vmul.f64	d0, d0, d1\n"
        "vmov	r0, r1, d0\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D43A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d43a4(void)
{
    __asm__ volatile(
        
        "ldr	r0, [pc, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D43A8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d43a8(void)
{
    __asm__ volatile(
        
        "ldr	r0, [pc, #4]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D43B4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d43b4(void)
{
    __asm__ volatile(
        
        "dmb	sy\n"
        "orrs	r0, r0, #1\n"
        "ldr	r1, [pc, #0x244]\n"
        "str	r0, [r1]\n"
        "ldr	r0, [pc, #0x244]\n"
        "ldr	r1, [r0]\n"
        "orrs	r1, r1, #0x10000\n"
        "str	r1, [r0]\n"
        "dsb	sy\n"
        "isb	sy\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D43D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d43d4(void)
{
    __asm__ volatile(
        
        "dmb	sy\n"
        "ldr	r0, [pc, #0x22c]\n"
        "ldr	r1, [r0]\n"
        "bics	r1, r1, #0x10000\n"
        "str	r1, [r0]\n"
        "ldr	r0, [pc, #0x220]\n"
        "ldr	r1, [r0]\n"
        "lsrs	r1, r1, #1\n"
        "lsls	r1, r1, #1\n"
        "str	r1, [r0]\n"
        "dsb	sy\n"
        "isb	sy\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D43F6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d43f6(void)
{
    __asm__ volatile(
        
        "push	{r4}\n"
        "movs	r3, r1\n"
        "uxtb	r3, r3\n"
        "lsrs	r3, r3, #2\n"
        "uxtb	r1, r1\n"
        "lsls	r1, r1, #3\n"
        "ands	r1, r1, #0x18\n"
        "movs	r4, #0xff\n"
        "lsls	r4, r1\n"
        "uxtb	r2, r2\n"
        "lsls.w	r1, r2, r1\n"
        "movs	r2, r3\n"
        "uxtb	r2, r2\n"
        "cmp	r2, #2\n"
        "bhs	L_open_cfw_runtime_am066_d43f6_003a\n"
        "movs	r2, r3\n"
        "uxtb	r2, r2\n"
        "add.w	r2, r0, r2, lsl #2\n"
        "ldr	r2, [r2, #0x30]\n"
        "bics	r2, r4\n"
        "ands	r1, r4\n"
        "orrs	r1, r2\n"
        "uxtb	r3, r3\n"
        "add.w	r0, r0, r3, lsl #2\n"
        "str	r1, [r0, #0x30]\n"
        "L_open_cfw_runtime_am066_d43f6_003a:\n"
        "pop	{r4}\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4434_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4434(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, r1\n"
        "uxtb	r2, r2\n"
        "movs	r1, r0\n"
        "uxtb	r1, r1\n"
        "ldr	r0, [pc, #0x1cc]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d43f6\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4446_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4446(void)
{
    __asm__ volatile(
        
        "push	{r4}\n"
        "movs	r3, #0\n"
        "b	L_open_cfw_runtime_am066_d4446_0010\n"
        "L_open_cfw_runtime_am066_d4446_0006:\n"
        "ldr.w	r4, [r1, r3, lsl #2]\n"
        "str.w	r4, [r0, r3, lsl #2]\n"
        "adds	r3, r3, #1\n"
        "L_open_cfw_runtime_am066_d4446_0010:\n"
        "cmp	r3, r2\n"
        "blo	L_open_cfw_runtime_am066_d4446_0006\n"
        "pop	{r4}\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D445E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d445e(void)
{
    __asm__ volatile(
        
        "push.w	{r3, r4, r5, r6, r7, r8, sb, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r1\n"
        "movs	r6, r2\n"
        "movs	r7, r3\n"
        "movs	r5, #2\n"
        "cmp	r7, #1\n"
        "bne	L_open_cfw_runtime_am066_d445e_0022\n"
        "str	r0, [r4, #8]\n"
        "movs	r2, r5\n"
        "movs	r1, r6\n"
        "adds.w	r0, r4, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d4446\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am066_d445e_0070\n"
        "L_open_cfw_runtime_am066_d445e_0022:\n"
        "lsrs.w	r8, r0, #2\n"
        "lsls.w	r8, r8, #2\n"
        "ands	r0, r0, #3\n"
        "str.w	r8, [r4, #8]\n"
        "b	L_open_cfw_runtime_am066_d445e_005a\n"
        "L_open_cfw_runtime_am066_d445e_0034:\n"
        "rsbs.w	sb, r0, #4\n"
        "mul	r2, r5, sb\n"
        "movs	r1, r6\n"
        "add.w	r0, r4, r0, lsl #3\n"
        "adds	r0, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d4446\n"
        "bl .\n"
        "add.w	r6, r6, sb, lsl #3\n"
        "subs.w	r7, r7, sb\n"
        "movs	r0, #0\n"
        "adds.w	r8, r8, #4\n"
        "str.w	r8, [r4, #8]\n"
        "L_open_cfw_runtime_am066_d445e_005a:\n"
        "adds	r1, r7, r0\n"
        "cmp	r1, #5\n"
        "bhs	L_open_cfw_runtime_am066_d445e_0034\n"
        "muls	r7, r5, r7\n"
        "movs	r2, r7\n"
        "movs	r1, r6\n"
        "add.w	r0, r4, r0, lsl #3\n"
        "adds	r0, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d4446\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d445e_0070:\n"
        "pop.w	{r0, r4, r5, r6, r7, r8, sb, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D44D2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d44d2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, r0\n"
        "ldr	r0, [pc, #0x130]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d445e\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D44E2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d44e2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d43d4\n"
        "bl .\n"
        "movs	r0, #0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D44EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d44ec(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "uxtb	r1, r1\n"
        "uxtb	r0, r0\n"
        "lsls	r0, r0, #2\n"
        "orrs.w	r0, r0, r1, lsl #1\n"
        "ldr	r1, [pc, #0x108]\n"
        "ldr	r1, [r1]\n"
        "lsls	r1, r1, #0x1f\n"
        "bpl	L_open_cfw_runtime_am066_d44ec_0018\n"
        "movs	r0, #3\n"
        "b	L_open_cfw_runtime_am066_d44ec_001e\n"
        "L_open_cfw_runtime_am066_d44ec_0018:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d43b4\n"
        "bl .\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am066_d44ec_001e:\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D450C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d450c(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "ldr	r0, [pc, #0xf0]\n"
        "ldr	r0, [r0]\n"
        "lsls	r0, r0, #0x1f\n"
        "bpl	L_open_cfw_runtime_am066_d450c_0012\n"
        "movs	r0, #3\n"
        "b	L_open_cfw_runtime_am066_d450c_0088\n"
        "L_open_cfw_runtime_am066_d450c_0012:\n"
        "movs	r6, #0\n"
        "b	L_open_cfw_runtime_am066_d450c_006c\n"
        "L_open_cfw_runtime_am066_d450c_0016:\n"
        "uxtb	r1, r1\n"
        "lsls	r1, r1, #2\n"
        "ands	r1, r1, #0xc\n"
        "b	L_open_cfw_runtime_am066_d450c_005a\n"
        "L_open_cfw_runtime_am066_d450c_0020:\n"
        "ldrb	r0, [r4, #1]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am066_d450c_007e\n"
        "ldrb	r0, [r4, #2]\n"
        "ldrb	r1, [r4, #3]\n"
        "lsls	r1, r1, #2\n"
        "orrs.w	r1, r1, r0, lsl #3\n"
        "ldrb	r0, [r4, #4]\n"
        "orrs.w	r1, r1, r0, lsl #1\n"
        "ldrb	r0, [r4, #5]\n"
        "orrs	r0, r1\n"
        "ldrb	r1, [r4, #6]\n"
        "ldrb	r3, [r4, #7]\n"
        "lsls	r3, r3, #2\n"
        "orrs.w	r3, r3, r1, lsl #3\n"
        "ldrb	r1, [r4, #8]\n"
        "orrs.w	r3, r3, r1, lsl #1\n"
        "ldrb	r1, [r4, #9]\n"
        "orrs	r1, r3\n"
        "L_open_cfw_runtime_am066_d450c_004e:\n"
        "tst.w	r0, #0xf\n"
        "beq	L_open_cfw_runtime_am066_d450c_0016\n"
        "uxtb	r1, r1\n"
        "ands	r1, r1, #0xf\n"
        "L_open_cfw_runtime_am066_d450c_005a:\n"
        "orrs.w	r1, r1, r0, lsl #4\n"
        "uxtb	r1, r1\n"
        "movs	r0, r2\n"
        "uxtb	r0, r0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d4434\n"
        "bl .\n"
        "adds	r4, #0xb\n"
        "adds	r6, r6, #1\n"
        "L_open_cfw_runtime_am066_d450c_006c:\n"
        "cmp	r6, r5\n"
        "bhs	L_open_cfw_runtime_am066_d450c_0086\n"
        "ldrb	r2, [r4]\n"
        "movs	r0, r2\n"
        "uxtb	r0, r0\n"
        "cmp	r0, #8\n"
        "blt	L_open_cfw_runtime_am066_d450c_0020\n"
        "movs	r0, #5\n"
        "b	L_open_cfw_runtime_am066_d450c_0088\n"
        "L_open_cfw_runtime_am066_d450c_007e:\n"
        "movs	r0, #0\n"
        "ldrb	r1, [r4, #0xa]\n"
        "lsls	r1, r1, #2\n"
        "b	L_open_cfw_runtime_am066_d450c_004e\n"
        "L_open_cfw_runtime_am066_d450c_0086:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am066_d450c_0088:\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4596_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4596(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "sub	sp, #0x80\n"
        "ldr	r3, [r0]\n"
        "ldr	r2, [pc, #0x64]\n"
        "ldr	r2, [r2]\n"
        "lsls	r2, r2, #0x1f\n"
        "bpl	L_open_cfw_runtime_am066_d4596_0012\n"
        "movs	r0, #3\n"
        "b	L_open_cfw_runtime_am066_d4596_0068\n"
        "L_open_cfw_runtime_am066_d4596_0012:\n"
        "adds	r2, r1, r3\n"
        "cmp	r2, #0x11\n"
        "blo	L_open_cfw_runtime_am066_d4596_001c\n"
        "movs	r0, #5\n"
        "b	L_open_cfw_runtime_am066_d4596_0068\n"
        "L_open_cfw_runtime_am066_d4596_001c:\n"
        "movs	r4, #0\n"
        "b	L_open_cfw_runtime_am066_d4596_0058\n"
        "L_open_cfw_runtime_am066_d4596_0020:\n"
        "ldr	r5, [r0, #4]\n"
        "lsrs	r5, r5, #5\n"
        "lsls	r5, r5, #5\n"
        "ldrb	r2, [r0, #8]\n"
        "orrs.w	r5, r5, r2, lsl #3\n"
        "ldrb	r2, [r0, #9]\n"
        "orrs.w	r5, r5, r2, lsl #1\n"
        "ldrb	r2, [r0, #0xa]\n"
        "orrs	r5, r2\n"
        "mov	r2, sp\n"
        "str.w	r5, [r2, r4, lsl #3]\n"
        "ldr	r5, [r0, #0xc]\n"
        "lsrs	r5, r5, #5\n"
        "lsls	r5, r5, #5\n"
        "ldr	r2, [r0, #0x10]\n"
        "orrs.w	r5, r5, r2, lsl #1\n"
        "ldrb	r2, [r0, #0x14]\n"
        "orrs	r5, r2\n"
        "mov	r2, sp\n"
        "add.w	r2, r2, r4, lsl #3\n"
        "str	r5, [r2, #4]\n"
        "adds	r0, #0x18\n"
        "adds	r4, r4, #1\n"
        "L_open_cfw_runtime_am066_d4596_0058:\n"
        "cmp	r4, r1\n"
        "blo	L_open_cfw_runtime_am066_d4596_0020\n"
        "movs	r2, r1\n"
        "mov	r1, sp\n"
        "movs	r0, r3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d44d2\n"
        "bl .\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am066_d4596_0068:\n"
        "add	sp, #0x84\n"
        "pop	{r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4610_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4610(void)
{
    __asm__ volatile(
        
        "push	{r1, r2, r3, r4, r5, lr}\n"
        "ldr	r4, [sp, #0x18]\n"
        "ldr	r5, [sp, #0x1c]\n"
        "str	r5, [r0, #4]\n"
        "str	r3, [r0]\n"
        "adds.w	r3, r0, #8\n"
        "str	r3, [sp, #4]\n"
        "uxtb	r2, r2\n"
        "str	r2, [sp]\n"
        "movs	r3, r0\n"
        "lsrs	r4, r4, #2\n"
        "movs	r2, r4\n"
        "uxth	r2, r2\n"
        "addw	r0, pc, #0x139\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4548ba\n"
        "bl .\n"
        "cmp	r0, #1\n"
        "beq	L_open_cfw_runtime_am066_d4610_003c\n"
        "ldr	r0, [pc, #0x16c]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x16c]\n"
        "movs	r2, #0x67\n"
        "ldr	r1, [pc, #0x16c]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am066_d4610_003e\n"
        "L_open_cfw_runtime_am066_d4610_003c:\n"
        "movs	r0, #1\n"
        "L_open_cfw_runtime_am066_d4610_003e:\n"
        "pop	{r1, r2, r3, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4650_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4650(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "ldr	r0, [r0, #8]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_454aae\n"
        "bl .\n"
        "movs	r0, #1\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D465C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d465c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47cc\n"
        "bl .\n"
        "movs	r0, #1\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4666_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4666(void)
{
    __asm__ volatile(
        
        "push	{r2, r3, r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47cc\n"
        "bl .\n"
        "movs.w	r1, #-1\n"
        "ldr	r0, [r4, #4]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_441750\n"
        "bl .\n"
        "cmp	r0, #1\n"
        "beq	L_open_cfw_runtime_am066_d4666_002c\n"
        "ldr	r0, [pc, #0x134]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x134]\n"
        "movs	r2, #0x84\n"
        "ldr	r1, [pc, #0x128]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am066_d4666_002e\n"
        "L_open_cfw_runtime_am066_d4666_002c:\n"
        "movs	r0, #1\n"
        "L_open_cfw_runtime_am066_d4666_002e:\n"
        "pop	{r1, r2, r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4696_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4696(void)
{
    __asm__ volatile(
        
        "push	{r2, r3, r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47cc\n"
        "bl .\n"
        "ldr	r0, [r4, #4]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_441710\n"
        "bl .\n"
        "cmp	r0, #1\n"
        "beq	L_open_cfw_runtime_am066_d4696_0028\n"
        "ldr	r0, [pc, #0x110]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x110]\n"
        "movs	r2, #0xa8\n"
        "ldr	r1, [pc, #0xfc]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_44d25c\n"
        "bl .\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am066_d4696_002a\n"
        "L_open_cfw_runtime_am066_d4696_0028:\n"
        "movs	r0, #1\n"
        "L_open_cfw_runtime_am066_d4696_002a:\n"
        "pop	{r1, r2, r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D46C2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d46c2(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "ldr	r0, [r4]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am066_d46c2_000e\n"
        "movs	r0, #0\n"
        "b	L_open_cfw_runtime_am066_d46c2_001a\n"
        "L_open_cfw_runtime_am066_d46c2_000e:\n"
        "ldr	r0, [r4, #4]\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_441ea2\n"
        "bl .\n"
        "movs	r0, #0\n"
        "str	r0, [r4]\n"
        "movs	r0, #1\n"
        "L_open_cfw_runtime_am066_d46c2_001a:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D46DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d46de(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47fa\n"
        "bl .\n"
        "movs	r0, #1\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D46E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d46e8(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, r6, r7, lr}\n"
        "movs	r5, r0\n"
        "movs	r6, #1\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47fa\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_45589c\n"
        "bl .\n"
        "movs	r7, r0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420d0\n"
        "bl .\n"
        "ldr	r4, [r5, #4]\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #4]\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am066_d46e8_0022\n"
        "str	r7, [r5, #8]\n"
        "L_open_cfw_runtime_am066_d46e8_0022:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420e8\n"
        "bl .\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am066_d46e8_0036\n"
        "movs.w	r2, #-1\n"
        "movs	r1, #1\n"
        "movs	r0, #0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_455afc\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d46e8_0036:\n"
        "movs	r0, r6\n"
        "uxtb	r0, r0\n"
        "pop	{r1, r4, r5, r6, r7, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4724_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4724(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r5, r0\n"
        "movs	r0, r5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47fa\n"
        "bl .\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420d0\n"
        "bl .\n"
        "ldr	r4, [r5, #8]\n"
        "movs	r0, #0\n"
        "str	r0, [r5, #8]\n"
        "cmp	r4, #0\n"
        "bne	L_open_cfw_runtime_am066_d4724_001c\n"
        "movs	r0, #1\n"
        "str	r0, [r5, #4]\n"
        "L_open_cfw_runtime_am066_d4724_001c:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420e8\n"
        "bl .\n"
        "cmp	r4, #0\n"
        "beq	L_open_cfw_runtime_am066_d4724_0034\n"
        "movs	r0, #0\n"
        "str	r0, [sp]\n"
        "movs	r3, #2\n"
        "movs	r2, #0\n"
        "movs	r1, #0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_455c48\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d4724_0034:\n"
        "movs	r0, #1\n"
        "pop	{r1, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D475C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d475c(void)
{
    __asm__ volatile(
        
        "movs	r1, #0\n"
        "str	r1, [r0, #4]\n"
        "movs	r1, #0\n"
        "str	r1, [r0]\n"
        "movs	r0, #1\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4768_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4768(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r1, r0\n"
        "ldr	r0, [r1, #4]\n"
        "ldr	r1, [r1]\n"
        "blx	r1\n"
        "movs	r0, #0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_454aae\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D477A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d477a(void)
{
    __asm__ volatile(
        
        "push	{r2, r3, r4, lr}\n"
        "movs	r4, r0\n"
        "movs	r0, #4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4416d6\n"
        "bl .\n"
        "str	r0, [r4, #4]\n"
        "ldr	r0, [r4, #4]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am066_d477a_0026\n"
        "ldr	r0, [pc, #0x34]\n"
        "str	r0, [sp]\n"
        "ldr	r3, [pc, #0x34]\n"
        "mov.w	r2, #0x1ba\n"
        "ldr	r1, [pc, #0x18]\n"
        "movs	r0, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_44d25c\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am066_d477a_002a\n"
        "L_open_cfw_runtime_am066_d477a_0026:\n"
        "movs	r0, #1\n"
        "str	r0, [r4]\n"
        "L_open_cfw_runtime_am066_d477a_002a:\n"
        "pop	{r0, r1, r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D47CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d47cc(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "ldr	r0, [r4]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am066_d47cc_001e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420d0\n"
        "bl .\n"
        "ldr	r0, [r4]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am066_d47cc_001a\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d477a\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d47cc_001a:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420e8\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d47cc_001e:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D47EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d47ec(void)
{
    __asm__ volatile(
        
        "movs	r1, #1\n"
        "str	r1, [r0]\n"
        "movs	r1, #0\n"
        "str	r1, [r0, #4]\n"
        "movs	r1, #0\n"
        "str	r1, [r0, #8]\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D47FA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d47fa(void)
{
    __asm__ volatile(
        
        "push	{r4, lr}\n"
        "movs	r4, r0\n"
        "ldr	r0, [r4]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am066_d47fa_001e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420d0\n"
        "bl .\n"
        "ldr	r0, [r4]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am066_d47fa_001a\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_d47ec\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d47fa_001a:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_4420e8\n"
        "bl .\n"
        "L_open_cfw_runtime_am066_d47fa_001e:\n"
        "pop	{r4, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D481A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d481a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, r1\n"
        "movs	r1, #1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_482868\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4826_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4826(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, r1\n"
        "movs	r1, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_482868\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM066_D4832_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am066_d4832(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, r1\n"
        "movs	r1, #7\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am066_call_482868\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif
