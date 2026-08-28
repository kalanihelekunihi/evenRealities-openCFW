/* SPDX-License-Identifier: MIT */
/*
 * Freestanding prefix for the reviewed Matthew Conte TLSF v3.1 snapshot.
 *
 * This file is deliberately a prefix rather than a modified copy of TLSF.
 * A build translation unit includes this file immediately before the
 * byte-preserved third_party/tlsf/tlsf.c source. The macros below rename the
 * complete public API while the compatibility headers replace the three
 * hosted-library seams used by that source.
 */

#include "tlsf_compat/assert.h"
#include "tlsf_compat/limits.h"
#include "tlsf_compat/stddef.h"
#include "tlsf_compat/stdio.h"
#include "tlsf_compat/stdlib.h"
#include "tlsf_compat/string.h"

_Static_assert(CHAR_BIT == 8, "TLSF requires eight-bit bytes");
_Static_assert(sizeof(char) == 1, "unexpected character ABI");
_Static_assert(sizeof(short) == 2, "unexpected short ABI");
_Static_assert(sizeof(int) == 4, "TLSF requires a 32-bit int");
_Static_assert(sizeof(long) == 4, "Apollo510 uses an ILP32 ABI");
_Static_assert(sizeof(long long) == 8, "unexpected long-long ABI");
_Static_assert(sizeof(void *) == 4, "Apollo510 requires 32-bit pointers");
_Static_assert(sizeof(size_t) == 4, "Apollo510 requires 32-bit size_t");
_Static_assert(sizeof(ptrdiff_t) == 4, "Apollo510 requires 32-bit ptrdiff_t");
_Static_assert(_Alignof(void *) == 4, "unexpected pointer alignment");
_Static_assert(UINT_MAX == 0xFFFFFFFFU, "unexpected unsigned-int range");

#if defined(__arm__) && !defined(__wasm32__)
typedef void (*open_cfw_tlsf_diagnostic_handler_fn)(void *context);

typedef unsigned int (*open_cfw_tlsf_diagnostic_vformat_fn)(
    char *destination,
    const char *format,
    void *arguments
);

#define OPEN_CFW_TLSF_DIAGNOSTIC_HANDLER() \
    (*(open_cfw_tlsf_diagnostic_handler_fn *)(void *)0x200742F0U)
#define OPEN_CFW_TLSF_DIAGNOSTIC_CONTEXT ((void *)0x2006B930U)
#define OPEN_CFW_TLSF_DIAGNOSTIC_ARGUMENT_CURSOR(arguments) \
    ((arguments).__ap)
#define OPEN_CFW_TLSF_DIAGNOSTIC_VFORMAT(destination, format, arguments) \
    (((open_cfw_tlsf_diagnostic_vformat_fn)0x00473037U)( \
        (char *)(destination), \
        (format), \
        (void *)(arguments) \
    ))
#endif

void open_cfw_tlsf_assert_fail(
    const char *expression,
    const char *file,
    unsigned int line
)
{
    /*
     * Assertions describe allocator corruption or an invalid caller contract.
     * Stop locally and deterministically; do not continue with damaged heap
     * metadata and do not introduce a stock fatal-handler dependency.
     */
    open_cfw_tlsf_diagnostic(
        "TLSF assertion failed: %s (%s:%u)\n",
        expression,
        file,
        line
    );

    for (;;) {
        __asm__ volatile("" ::: "memory");
    }
}

__attribute__((noinline, used))
int open_cfw_tlsf_diagnostic(const char *format, ...)
{
#if defined(__arm__) && !defined(__wasm32__)
    open_cfw_tlsf_diagnostic_handler_fn handler =
        OPEN_CFW_TLSF_DIAGNOSTIC_HANDLER();
    __builtin_va_list arguments;
    unsigned int result;

    /*
     * Preserve the stock TLSF printf boundary through the same reviewed
     * formatter/context/callback ABI as open_cfw_log_format_dispatch.
     */
    if (handler == (open_cfw_tlsf_diagnostic_handler_fn)0) {
        return 0;
    }
    __builtin_va_start(arguments, format);
    result = OPEN_CFW_TLSF_DIAGNOSTIC_VFORMAT(
        OPEN_CFW_TLSF_DIAGNOSTIC_CONTEXT,
        format,
        OPEN_CFW_TLSF_DIAGNOSTIC_ARGUMENT_CURSOR(arguments)
    );
    __builtin_va_end(arguments);
    handler = OPEN_CFW_TLSF_DIAGNOSTIC_HANDLER();
    handler(OPEN_CFW_TLSF_DIAGNOSTIC_CONTEXT);
    return (int)result;
#else
    /*
     * The wasm32 execution oracle has no firmware logging environment. Keep
     * diagnostics deterministic there while executing the allocator itself.
     */
    (void)format;
    return 0;
#endif
}

__attribute__((noinline, used))
void *open_cfw_tlsf_memcpy(
    void *destination,
    const void *source,
    size_t byte_count
)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    size_t index;

    for (index = 0; index < byte_count; ++index) {
        output[index] = input[index];
    }

    return destination;
}

/*
 * Clang advertises GCC compatibility macros. TLSF uses those identities to
 * select compiler builtins; remove them before the vendored source is parsed
 * so the reviewed generic ffs/fls implementation is selected instead.
 */
#ifdef __GNUC__
#undef __GNUC__
#endif
#ifdef __GNUC_MINOR__
#undef __GNUC_MINOR__
#endif
#ifdef __GNUC_PATCHLEVEL__
#undef __GNUC_PATCHLEVEL__
#endif
#ifdef __GNUC_STDC_INLINE__
#undef __GNUC_STDC_INLINE__
#endif

/* Public TLSF types. */
#define tlsf_t open_cfw_tlsf_t
#define pool_t open_cfw_tlsf_pool_t
#define tlsf_walker open_cfw_tlsf_walker

/* Complete public TLSF function API. */
#define tlsf_create open_cfw_tlsf_create
#define tlsf_create_with_pool open_cfw_tlsf_create_with_pool
#define tlsf_destroy open_cfw_tlsf_destroy
#define tlsf_get_pool open_cfw_tlsf_get_pool
#define tlsf_add_pool open_cfw_tlsf_add_pool
#define tlsf_remove_pool open_cfw_tlsf_remove_pool
#define tlsf_malloc open_cfw_tlsf_malloc
#define tlsf_memalign open_cfw_tlsf_memalign
#define tlsf_realloc open_cfw_tlsf_realloc
#define tlsf_free open_cfw_tlsf_free
#define tlsf_block_size open_cfw_tlsf_block_size
#define tlsf_size open_cfw_tlsf_size
#define tlsf_align_size open_cfw_tlsf_align_size
#define tlsf_block_size_min open_cfw_tlsf_block_size_min
#define tlsf_block_size_max open_cfw_tlsf_block_size_max
#define tlsf_pool_overhead open_cfw_tlsf_pool_overhead
#define tlsf_alloc_overhead open_cfw_tlsf_alloc_overhead
#define tlsf_walk_pool open_cfw_tlsf_walk_pool
#define tlsf_check open_cfw_tlsf_check
#define tlsf_check_pool open_cfw_tlsf_check_pool
