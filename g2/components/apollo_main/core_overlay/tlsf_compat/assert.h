/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_TLSF_COMPAT_ASSERT_H
#define OPEN_CFW_TLSF_COMPAT_ASSERT_H

/*
 * TLSF assertions stop deterministically inside the source-owned overlay.
 * The implementation intentionally has no dependency on a hosted C runtime.
 */
void open_cfw_tlsf_assert_fail(
    const char *expression,
    const char *file,
    unsigned int line
) __attribute__((noreturn, noinline, used));

#define assert(expression) \
    ((expression) \
        ? (void)0 \
        : open_cfw_tlsf_assert_fail( \
            #expression, \
            __FILE__, \
            (unsigned int)__LINE__ \
        ))

#endif
