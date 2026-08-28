/*
 * SPDX-License-Identifier: MIT
 *
 * Exact source replacement for the G2 2.2.6.10 formatting span adapter at
 * 0x004910E8. The bounded caller, argument layout, and downstream ABI are
 * recorded in EVIDENCE.md.
 */

#ifdef OPEN_CFW_FORMAT_SPAN_HOST

#ifndef OPEN_CFW_FORMAT_SPAN_LENGTH
#define OPEN_CFW_FORMAT_SPAN_LENGTH(argument) \
    (*(const unsigned short *)(const void *)( \
        (const unsigned char *)(argument) + 0x12U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_SPAN_DATA
#define OPEN_CFW_FORMAT_SPAN_DATA(argument) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(argument) + 0x1CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_SPAN_WRITE
#define OPEN_CFW_FORMAT_SPAN_WRITE(output, data, length) \
    (((unsigned int (*)(void *, const void *, unsigned int))0x00490DB7U)( \
        (output), \
        (data), \
        (length) \
    ))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_span(void *output, const void *argument)
{
    return OPEN_CFW_FORMAT_SPAN_WRITE(
        output,
        OPEN_CFW_FORMAT_SPAN_DATA(argument),
        OPEN_CFW_FORMAT_SPAN_LENGTH(argument)
    );
}

#else

/*
 * The named BL displacement is valid only after the builder copies these
 * bytes to 0x004910E8. The overlay symbol is a deterministic builder input
 * and is not linked as a callable runtime implementation.
 */
__attribute__((used, noinline, naked))
unsigned int open_cfw_format_span(void *output, const void *argument)
{
    __asm volatile(
        ".syntax unified\n"
        "push {r7, lr}\n"
        "ldrh r2, [r1, #0x12]\n"
        "ldr r1, [r1, #0x1c]\n"
        ".equ open_cfw_format_span_writer_delta, -0x338\n"
        "bl . + open_cfw_format_span_writer_delta\n"
        "pop {r1, pc}\n"
    );
}

#endif
