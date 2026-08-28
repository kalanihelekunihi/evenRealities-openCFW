/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 leaf predicate at
 * 0x00482708...0x00482715. The stock helper reads only byte offset 8 of its
 * lookup context and reports whether that byte is the 0xff sentinel. Its
 * three callers use that sentinel to select the static, zero-terminated
 * key/value representation and to reject dynamic-table mutation.
 *
 * The immediately preceding helper at 0x004826FC deliberately remains
 * opaque. Its exact epilogue restores the caller's saved r7 into r0 after
 * calling the stock zero-fill routine, so its observable return register is
 * a compiler-artifact-sensitive part of the ABI that portable C must not
 * guess at.
 */

__attribute__((used, noinline))
int open_cfw_runtime_lookup_is_static(const void *context)
{
    const unsigned char *bytes = (const unsigned char *)context;

    return bytes[8] == 0xFFU;
}
