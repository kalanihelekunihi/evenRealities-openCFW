/*
 * Clean-room Thumb source for the AM142 0x0059b80c ring-entry arithmetic
 * fragment.  The two BEQ exits target code outside this routed section, so
 * their transfer halfwords remain explicit with decoded destinations.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b80c(void)
{
    __asm__ volatile(
        "mul r0, r8, r7\n"
        "add r0, r6\n"
        "str.w sl, [r0, #0x28]\n"
        "cmp r4, #0\n"
        ".hword 0xd021\n"        /* beq 0x0059b85e */
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x24]\n"
        "mul r1, r8, r4\n"
        "add r1, r6\n"
        "ldr r1, [r1, #0x10]\n"
        "cmp r0, r1\n"
        ".hword 0xd017\n"        /* beq 0x0059b85e */
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r1, [r0, #0x24]\n"
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x10]\n"
        "subs r1, r1, r0\n"
        "mul r0, r8, r4\n"
        "add r0, r6\n"
        "ldr r0, [r0, #0x28]\n"
        "mul r2, r8, r4\n"
        "add r2, r6\n"
        "ldr r2, [r2, #0x14]\n"
        "subs r0, r0, r2\n"
    );
}
