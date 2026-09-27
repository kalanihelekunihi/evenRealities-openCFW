/*
 * Clean-room Thumb source for the AM142 0x0059ba96 ring search fragment.
 * Several branch exits target neighboring AM142 spans outside this route, so
 * those transfer halfwords remain explicit with decoded destinations.
 */
__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059ba96(void)
{
    __asm__ volatile(
        "movs r0, #0x14\n"
        "mul r0, r0, r4\n"
        "add r0, r5\n"
        "ldr r0, [r0, #0x24]\n"
        "ldr r1, [r7, #8]\n"
        "cmp r0, r1\n"
        ".hword 0xdbf3\n"        /* blt 0x0059ba8e */
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "ldr r0, [r5, #0x14]\n"
        "cmp r4, r0\n"
        ".hword 0xd21e\n"        /* bhs 0x0059baf0 */
        "movs r0, #0x14\n"
        "mul r1, r0, r4\n"
        "add r1, r5\n"
        "ldr r1, [r1, #0x24]\n"
        "ldr r2, [r7, #8]\n"
        "cmp r1, r2\n"
        ".hword 0xf000, 0x80b1\n" /* beq.w 0x0059bc26 */
        "movs r1, r6\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        ".hword 0xd008\n"        /* beq 0x0059bade */
        "ldr.w r1, [r8, #8]\n"
        "mul r2, r0, r4\n"
        "add r2, r5\n"
        "ldr r2, [r2, #0x24]\n"
        "cmp r1, r2\n"
        ".hword 0xf280, 0x80a4\n" /* bge.w 0x0059bc26 */
        "mul r0, r0, r4\n"
        "add r0, r5\n"
    );
}
