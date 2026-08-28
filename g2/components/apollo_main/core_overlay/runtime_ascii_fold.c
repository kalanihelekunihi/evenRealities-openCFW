/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the shared G2 2.2.6.10 Apollo ASCII case-folding
 * primitive at 0x00481830. The exact stock boundary and reference inventory
 * are recorded in EVIDENCE.md.
 */

__attribute__((used, noinline))
unsigned int open_cfw_ascii_fold_lower(unsigned int value)
{
    return value | 0x20U;
}
