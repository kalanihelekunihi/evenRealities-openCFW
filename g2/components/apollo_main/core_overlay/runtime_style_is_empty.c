/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 style-empty predicate at
 * 0x00482A5A...0x00482A69. The stock leaf reads only byte offset 8 of the
 * shared 12-byte style/map descriptor and reports whether its dynamic
 * property count is zero.
 */

__attribute__((used, noinline))
int open_cfw_runtime_style_is_empty(const void *style)
{
    const unsigned char *bytes = (const unsigned char *)style;

    return bytes[8] == 0U;
}
