/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-007 retained island.
 */

#if defined(OPEN_CFW_AM007_41004_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41004(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "uxtb	r0, r0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_440f44\n"
        "bl .\n"
        "adds	r0, r0, #7\n"
        "uxth	r0, r0\n"
        "lsrs	r0, r0, #3\n"
        "uxtb	r0, r0\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41016_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41016(void)
{
    __asm__ volatile(
        
        "push	{r0}\n"
        "mov	r1, sp\n"
        "ldrb	r0, [r1]\n"
        "ldrb	r2, [r1, #1]\n"
        "lsls	r2, r2, #8\n"
        "uxtab	r0, r2, r0\n"
        "ldrb	r1, [r1, #2]\n"
        "adds.w	r0, r0, r1, lsl #16\n"
        "add	sp, #4\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4102E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4102e(void)
{
    __asm__ volatile(
        
        "push	{r3, r4, r5, lr}\n"
        "movs	r4, r1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_41016\n"
        "bl .\n"
        "movs	r5, r0\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_41016\n"
        "bl .\n"
        "cmp	r5, r0\n"
        "bne	L_open_cfw_runtime_am007_4102e_0018\n"
        "movs	r0, #1\n"
        "b	L_open_cfw_runtime_am007_4102e_001a\n"
        "L_open_cfw_runtime_am007_4102e_0018:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am007_4102e_001a:\n"
        "uxtb	r0, r0\n"
        "pop	{r1, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4104C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4104c(void)
{
    __asm__ volatile(
        
        "sub	sp, #4\n"
        "movs	r1, r0\n"
        "lsrs	r1, r1, #0x10\n"
        "strb.w	r1, [sp, #2]\n"
        "movs	r1, r0\n"
        "lsrs	r1, r1, #8\n"
        "strb.w	r1, [sp, #1]\n"
        "strb.w	r0, [sp]\n"
        "ldr	r0, [sp]\n"
        "add	sp, #4\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41068_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41068(void)
{
    __asm__ volatile(
        
        "sub	sp, #4\n"
        "strb.w	r0, [sp, #2]\n"
        "strb.w	r1, [sp, #1]\n"
        "strb.w	r2, [sp]\n"
        "ldr	r0, [sp]\n"
        "add	sp, #4\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4107C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4107c(void)
{
    __asm__ volatile(
        
        "sub	sp, #4\n"
        "strb.w	r0, [sp, #2]\n"
        "strb.w	r1, [sp, #1]\n"
        "strb.w	r2, [sp]\n"
        "strb.w	r3, [sp, #3]\n"
        "ldr	r0, [sp]\n"
        "add	sp, #4\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41094_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41094(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0xff\n"
        "movs	r1, #0xff\n"
        "movs	r0, #0xff\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_41068\n"
        "bl .\n"
        "str	r0, [sp]\n"
        "ldr	r0, [sp]\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_410A6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_410a6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, #0\n"
        "movs	r1, #0\n"
        "movs	r0, #0\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_41068\n"
        "bl .\n"
        "str	r0, [sp]\n"
        "ldr	r0, [sp]\n"
        "pop	{r1, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_410B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_410b8(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "ldrb	r1, [r0, #3]\n"
        "cmp	r1, #0xff\n"
        "beq	L_open_cfw_runtime_am007_410b8_0034\n"
        "ldrb	r1, [r0, #3]\n"
        "cmp	r1, #0\n"
        "bne	L_open_cfw_runtime_am007_410b8_0016\n"
        "movs	r1, #4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_440f38\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am007_410b8_0034\n"
        "L_open_cfw_runtime_am007_410b8_0016:\n"
        "ldrb	r2, [r0, #2]\n"
        "ldrb	r1, [r0, #3]\n"
        "muls	r2, r1, r2\n"
        "asrs	r2, r2, #8\n"
        "strb	r2, [r0, #2]\n"
        "ldrb	r2, [r0, #1]\n"
        "ldrb	r1, [r0, #3]\n"
        "muls	r2, r1, r2\n"
        "asrs	r2, r2, #8\n"
        "strb	r2, [r0, #1]\n"
        "ldrb	r2, [r0]\n"
        "ldrb	r1, [r0, #3]\n"
        "muls	r2, r1, r2\n"
        "asrs	r2, r2, #8\n"
        "strb	r2, [r0]\n"
        "L_open_cfw_runtime_am007_410b8_0034:\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_410EE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_410ee(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r2, r1\n"
        "uxtb	r2, r2\n"
        "cmp	r2, #0xff\n"
        "beq	L_open_cfw_runtime_am007_410ee_0074\n"
        "movs	r2, r1\n"
        "uxtb	r2, r2\n"
        "cmp	r2, #0\n"
        "bne	L_open_cfw_runtime_am007_410ee_001a\n"
        "movs	r1, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_440f38\n"
        "bl .\n"
        "b	L_open_cfw_runtime_am007_410ee_0074\n"
        "L_open_cfw_runtime_am007_410ee_001a:\n"
        "ldrh	r3, [r0]\n"
        "uxth	r3, r3\n"
        "lsrs	r3, r3, #0xb\n"
        "uxth	r3, r3\n"
        "movs	r2, r1\n"
        "uxtb	r2, r2\n"
        "mul	r2, r2, r3\n"
        "asrs	r2, r2, #8\n"
        "ands	r2, r2, #0x1f\n"
        "ldrh	r3, [r0]\n"
        "bfi	r3, r2, #0xb, #5\n"
        "strh	r3, [r0]\n"
        "ldrh	r2, [r0]\n"
        "ubfx	r3, r2, #5, #6\n"
        "uxth	r3, r3\n"
        "movs	r2, r1\n"
        "uxtb	r2, r2\n"
        "mul	r2, r2, r3\n"
        "asrs	r2, r2, #8\n"
        "ands	r2, r2, #0x3f\n"
        "ldrh	r3, [r0]\n"
        "bfi	r3, r2, #5, #6\n"
        "strh	r3, [r0]\n"
        "ldrb	r2, [r0]\n"
        "ands	r2, r2, #0x1f\n"
        "uxtb	r1, r1\n"
        "mul	r1, r1, r2\n"
        "asrs	r1, r1, #8\n"
        "ands	r1, r1, #0x1f\n"
        "ldrh	r3, [r0]\n"
        "movw	r2, #0xffe0\n"
        "ands	r3, r2\n"
        "orrs	r1, r3\n"
        "strh	r1, [r0]\n"
        "L_open_cfw_runtime_am007_410ee_0074:\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41164_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41164(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #1\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41180_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41180(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #5\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4118E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4118e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4119C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4119c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #6\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_411AA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_411aa(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #7\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_411B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_411b8(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #8\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_411C6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_411c6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #9\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_411D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_411d4(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0xa\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_411E4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_411e4(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x6d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_411F2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_411f2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x6e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41200_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41200(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x6f\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4120E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4120e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x10\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4121C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4121c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x11\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4122A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4122a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x12\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41238_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41238(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x13\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41246_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41246(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x14\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41254_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41254(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x15\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41262_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41262(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x19\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41270_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41270(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x1a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4127E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4127e(void)
{
    __asm__ volatile(
        
        "push	{r0, r1, r4, r5, lr}\n"
        "sub	sp, #4\n"
        "movs	r4, r0\n"
        "movs	r5, r2\n"
        "mov	r0, sp\n"
        "add	r1, sp, #8\n"
        "movs	r2, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_439be4\n"
        "bl .\n"
        "movs	r3, r5\n"
        "ldr	r2, [sp]\n"
        "movs	r1, #0x1c\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4129E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4129e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x1d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_412AE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_412ae(void)
{
    __asm__ volatile(
        
        "push	{r0, r1, r4, r5, lr}\n"
        "sub	sp, #4\n"
        "movs	r4, r0\n"
        "movs	r5, r2\n"
        "mov	r0, sp\n"
        "add	r1, sp, #8\n"
        "movs	r2, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_439be4\n"
        "bl .\n"
        "movs	r3, r5\n"
        "ldr	r2, [sp]\n"
        "movs	r1, #0x23\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_412CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_412ce(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x20\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_412EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_412ec(void)
{
    __asm__ volatile(
        
        "push	{r0, r1, r4, r5, lr}\n"
        "sub	sp, #4\n"
        "movs	r4, r0\n"
        "movs	r5, r2\n"
        "mov	r0, sp\n"
        "add	r1, sp, #8\n"
        "movs	r2, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_439be4\n"
        "bl .\n"
        "movs	r3, r5\n"
        "ldr	r2, [sp]\n"
        "movs	r1, #0x31\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4130C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4130c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x32\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4131C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4131c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x30\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4132A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4132a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x34\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4133A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4133a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x38\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41378_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41378(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x3b\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41386_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41386(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x3c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41394_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41394(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x40\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_413A2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_413a2(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x41\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_413B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_413b0(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x42\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_413BE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_413be(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x3e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_413CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_413ce(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x44\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_413DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_413de(void)
{
    __asm__ volatile(
        
        "push	{r0, r1, r4, r5, lr}\n"
        "sub	sp, #4\n"
        "movs	r4, r0\n"
        "movs	r5, r2\n"
        "mov	r0, sp\n"
        "add	r1, sp, #8\n"
        "movs	r2, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_439be4\n"
        "bl .\n"
        "movs	r3, r5\n"
        "ldr	r2, [sp]\n"
        "movs	r1, #0x45\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_413FE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_413fe(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x46\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4140E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4140e(void)
{
    __asm__ volatile(
        
        "push	{r0, r1, r4, r5, lr}\n"
        "sub	sp, #4\n"
        "movs	r4, r0\n"
        "movs	r5, r2\n"
        "mov	r0, sp\n"
        "add	r1, sp, #8\n"
        "movs	r2, #3\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_439be4\n"
        "bl .\n"
        "movs	r3, r5\n"
        "ldr	r2, [sp]\n"
        "movs	r1, #0x58\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, r1, r2, r4, r5, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4142E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4142e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x59\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4143E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4143e(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x5a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4144C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4144c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0x5c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4145A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4145a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x5e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4146A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4146a(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "movs	r2, r1\n"
        "movs	r1, #0xc\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41478_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41478(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x2d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41488_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41488(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x62\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_414A6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_414a6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxth	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x16\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_414C6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_414c6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x7a\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_414D6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_414d6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x7b\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_414E6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_414e6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x7c\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_414F6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_414f6(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x7d\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41506_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41506(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r3, r2\n"
        "uxtb	r1, r1\n"
        "movs	r2, r1\n"
        "movs	r1, #0x7e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_44be4c\n"
        "bl .\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_41EC4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_41ec4(void)
{
    __asm__ volatile(
        
        "ldr	r1, [r0, #0x24]\n"
        "cmp	r1, #0\n"
        "beq	L_open_cfw_runtime_am007_41ec4_0010\n"
        "ldr	r0, [r0, #0x30]\n"
        "ldr	r0, [r0]\n"
        "rsbs.w	r0, r0, #0x38\n"
        "b	L_open_cfw_runtime_am007_41ec4_0012\n"
        "L_open_cfw_runtime_am007_41ec4_0010:\n"
        "movs	r0, #0\n"
        "L_open_cfw_runtime_am007_41ec4_0012:\n"
        "bx	lr\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_42030_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_42030(void)
{
    __asm__ volatile(
        
        "push	{r4, r5, r6, lr}\n"
        "movs	r4, r0\n"
        "movs	r5, r1\n"
        "movs	r6, r2\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_4420d0\n"
        "bl .\n"
        "ldrsb.w	r0, [r4, #0x44]\n"
        "cmn.w	r0, #1\n"
        "bne	L_open_cfw_runtime_am007_42030_001c\n"
        "movs	r0, #0\n"
        "strb.w	r0, [r4, #0x44]\n"
        "L_open_cfw_runtime_am007_42030_001c:\n"
        "ldrsb.w	r0, [r4, #0x45]\n"
        "cmn.w	r0, #1\n"
        "bne	L_open_cfw_runtime_am007_42030_002c\n"
        "movs	r0, #0\n"
        "strb.w	r0, [r4, #0x45]\n"
        "L_open_cfw_runtime_am007_42030_002c:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_4420e8\n"
        "bl .\n"
        "ldr	r0, [r4, #0x38]\n"
        "cmp	r0, #0\n"
        "bne	L_open_cfw_runtime_am007_42030_0042\n"
        "movs	r2, r6\n"
        "movs	r1, r5\n"
        "adds.w	r0, r4, #0x24\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_455320\n"
        "bl .\n"
        "L_open_cfw_runtime_am007_42030_0042:\n"
        "movs	r0, r4\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_441f88\n"
        "bl .\n"
        "pop	{r4, r5, r6, pc}\n"
    
    );
}
#endif

#if defined(OPEN_CFW_AM007_4207C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am007_4207c(void)
{
    __asm__ volatile(
        
        "push	{r7, lr}\n"
        "movs	r0, #0\n"
        "str	r0, [sp]\n"
        "ldr	r0, [pc, #0x18c]\n"
        "ldr	r0, [r0]\n"
        "cmn.w	r0, #1\n"
        "beq	L_open_cfw_runtime_am007_4207c_001e\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_5fa0a4\n"
        "bl .\n"
        "movs	r0, #0\n"
        "movs.w	r1, #-1\n"
        "str	r0, [r1]\n"
        "L_open_cfw_runtime_am007_4207c_001c:\n"
        "b	L_open_cfw_runtime_am007_4207c_001c\n"
        "L_open_cfw_runtime_am007_4207c_001e:\n"
        ".reloc ., R_ARM_THM_CALL, open_cfw_runtime_am007_call_5fa0a4\n"
        "bl .\n"
        "L_open_cfw_runtime_am007_4207c_0022:\n"
        "ldr	r0, [sp]\n"
        "cmp	r0, #0\n"
        "beq	L_open_cfw_runtime_am007_4207c_0022\n"
        "pop	{r0, pc}\n"
    
    );
}
#endif
