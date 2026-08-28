/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Cortex-M55 non-local jump provider for the authenticated G2
 * FreeType ABI.  See JUMP_ABI_EVIDENCE.md for the bounded stock evidence.
 */

#if !defined(__arm__) && !defined(__thumb__)
#error "the FreeType jump provider is Cortex-M target-only"
#endif
#if OPEN_CFW_FREETYPE_JMP_BUF_BYTES != 128
#error "authenticated G2 IAR jmp_buf size is 128 bytes"
#endif
#if OPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT != 8
#error "the OpenCFW VFP jump provider requires 8-byte buffer alignment"
#endif

/*
 * Buffer layout:
 *   0x00..0x1f  r4-r11
 *   0x20        sp
 *   0x24        lr
 *   0x28..0x67  d8-d15
 *   0x68..0x7f  reserved by the observed G2 IAR jmp_buf ABI
 */

__attribute__((used, naked, returns_twice))
int open_cfw_freetype_external_setjmp(void *environment)
{
    __asm__ volatile(
        "mov r12, sp\n"
        "stmia r0!, {r4-r11}\n"
        "stmia r0!, {r12, lr}\n"
        "vstmia r0!, {d8-d15}\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

__attribute__((used, naked, noreturn))
void open_cfw_freetype_external_longjmp(void *environment, int value)
{
    __asm__ volatile(
        "cmp r1, #0\n"
        "it eq\n"
        "addeq r1, r1, #1\n"
        "ldmia r0!, {r4-r11}\n"
        "ldmia r0!, {r12, lr}\n"
        "vldmia r0!, {d8-d15}\n"
        "mov sp, r12\n"
        "movs r0, r1\n"
        "bx lr\n"
    );
}
