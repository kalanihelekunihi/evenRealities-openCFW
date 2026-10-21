/* Experimental C translation unit for Apollo Main's ARM jump ABI.
 * Instruction sequence follows pinned Newlib ARM setjmp.S at commit
 * 45db03434ac7ae6500c29930f3d691a528584bdf. The native bodies at
 * 0x56777c/0x567790 and this sequence passed 80 finite Cortex-M55 register,
 * stack, and 128-byte buffer comparisons; this does not qualify all callers.
 * FreeType's recovered jmp buffer is 128 bytes, not the upstream 160-byte
 * default typedef. These routines write 104 bytes of that buffer. */

__attribute__((naked, noinline, returns_twice))
int setjmp(void *buffer __attribute__((unused)))
{
    __asm__ volatile(
        "mov ip, sp\n"
        "stmia r0!, {r4-r10, fp, ip, lr}\n"
        "vstm r0, {d8-d15}\n"
        "mov r0, #0\n"
        "bx lr\n");
}

__attribute__((naked, noinline, noreturn))
void longjmp(void *buffer __attribute__((unused)), int value __attribute__((unused)))
{
    __asm__ volatile(
        "ldmia r0!, {r4-r10, fp, ip, lr}\n"
        "mov sp, ip\n"
        "vldm r0, {d8-d15}\n"
        "movs r0, r1\n"
        "it eq\n"
        "moveq r0, #1\n"
        "bx lr\n");
}
