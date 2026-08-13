/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 lookup-table bucket helper
 * at 0x0048277E...0x0048278B. Its sole caller uses the returned index to set
 * one bit in the dynamic lookup table's 32-bit key-presence bitmap.
 */

__attribute__((used, noinline))
unsigned char open_cfw_runtime_lookup_bucket_index(unsigned char key)
{
    unsigned char index = (unsigned char)(key >> 2);

    if (index > 31U) {
        index = 31U;
    }
    return index;
}
