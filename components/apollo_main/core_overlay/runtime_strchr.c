/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the shared G2 2.2.6.10 Apollo character-search
 * primitive at 0x00481818. The exact stock boundary and reference inventory
 * are recorded in EVIDENCE.md.
 */

__attribute__((used, noinline))
char *open_cfw_strchr(const char *text, int character)
{
    const unsigned char *cursor = (const unsigned char *)text;
    const unsigned char needle = (unsigned char)character;

#pragma clang loop unroll(disable)
    while (*cursor != needle) {
        if (*cursor == '\0') {
            return (char *)0;
        }
        ++cursor;
    }

    return (char *)cursor;
}
