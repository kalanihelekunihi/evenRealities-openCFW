/* SPDX-License-Identifier: FTL */
/* Typed boundary for the authenticated clean-room Cortex-M55 provider. */
#ifndef OPEN_CFW_FREETYPE_TARGET_SETJMP_H
#define OPEN_CFW_FREETYPE_TARGET_SETJMP_H

#if !defined(OPEN_CFW_FREETYPE_JMP_BUF_BYTES) || \
    !defined(OPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT)
#error "select the target setjmp provider buffer size and alignment"
#endif
#if OPEN_CFW_FREETYPE_JMP_BUF_BYTES != 128
#error "authenticated G2 FreeType jmp_buf size is 128 bytes"
#endif
#if OPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT != 8
#error "OpenCFW Cortex-M55 jump buffers require 8-byte alignment"
#endif

typedef struct open_cfw_freetype_external_jump_buffer {
    _Alignas(OPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT)
    unsigned char opaque[OPEN_CFW_FREETYPE_JMP_BUF_BYTES];
} jmp_buf[1];

int open_cfw_freetype_external_setjmp(jmp_buf environment);
_Noreturn void open_cfw_freetype_external_longjmp(
    jmp_buf environment,
    int value
);

#define setjmp(environment) \
    open_cfw_freetype_external_setjmp(environment)
#define longjmp(environment, value) \
    open_cfw_freetype_external_longjmp((environment), (value))

#endif
