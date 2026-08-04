/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the shared G2 2.2.6.10 Apollo string-length
 * primitive at 0x0044A43C. The exact stock boundary and reference inventory
 * are recorded in EVIDENCE.md.
 */

__attribute__((used, noinline))
unsigned int open_cfw_strlen(const char *text)
{
    const char *cursor = text;

    while (*cursor != '\0') {
        ++cursor;
    }
    return (unsigned int)(cursor - text);
}
