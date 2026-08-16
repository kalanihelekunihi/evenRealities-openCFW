/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral recreation of the IAR DLIB %[...] scanset membership
 * matcher in the official Even Realities G2 2.2.6.10 Apollo-main image
 * (stock body [0x004D2112,0x004D2158), 70 bytes), bounded by the formatted-I/O
 * audit in docs/research/g2-iar-dlib-format-io-recovery.md.
 *
 * The stock leaf interprets a compiled scanset table as a byte stream of two
 * entry kinds, walking it with a remaining-byte countdown:
 *
 *   - range triple: any window of three or more remaining bytes whose second
 *     byte is '-' (0x2D) matches when table[0] <= ch <= table[2]; a non-match
 *     consumes three bytes; and
 *   - literal entry: any other byte matches when it equals ch and consumes
 *     one byte.
 *
 * A trailing window of fewer than three bytes is matched as literals only,
 * so a trailing '-' can never start a range.  The character is masked to
 * eight bits (stock UXTB).  The matcher returns 1 on membership and 0 on
 * table exhaustion; it performs no calls, no literal-pool loads, and no
 * writes, which is why it is the cluster's cleanest clean-room candidate.
 *
 * This file is a behavioral re-expression written from the bounded audit's
 * control-flow recovery, not decompiler output.  DLIB itself is proprietary
 * IAR runtime; no IAR source or object bytes are imported here.
 */

/*
 * Match character `ch` against the compiled scanset table at `table`,
 * interpreted over `table_bytes` remaining bytes.  Returns 1 if the scanset
 * contains the character, 0 otherwise.
 */
int open_cfw_iar_scanset_match(
    const unsigned char *table,
    unsigned int table_bytes,
    unsigned int ch
)
{
    const unsigned char *cursor = table;
    unsigned int remaining = table_bytes;
    unsigned int value = ch & 0xFFu;

    while (remaining >= 3u) {
        if (cursor[1] == 0x2Du) {
            /* Range triple: lo '-' hi. */
            if (value >= cursor[0] && cursor[2] >= value) {
                return 1;
            }
            cursor += 3;
            remaining -= 3u;
        } else {
            /* Single literal entry. */
            if (*cursor == value) {
                return 1;
            }
            cursor += 1;
            remaining -= 1u;
        }
    }
    while (remaining != 0u) {
        /* Sub-triple tail: literals only, '-' loses its range meaning. */
        if (*cursor == value) {
            return 1;
        }
        cursor += 1;
        remaining -= 1u;
    }
    return 0;
}
