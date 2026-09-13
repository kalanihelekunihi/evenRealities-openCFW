/* SPDX-License-Identifier: MIT */
/* Specialization for the closed RFFT512 component's immutable CFFT256
 * descriptor. The original 240 halfword entries encode i < reverse8(i),
 * in ascending i order. Generate those same swaps without storing a table.
 * Incremental reversal visits identical pairs; word swaps require the same
 * word-aligned sample buffer as the original packed helper.
 * This is not a replacement for the generic table-driven public helper. */
#include <stdint.h>
void open_cfw_gx8002_backup_bit_reverse(int16_t *samples,
                                      unsigned entries,
                                      const uint16_t *table)
{
    (void)entries;
    (void)table;
    unsigned reversed = 0;
    for (unsigned i = 1; i < 256; ++i) {
        unsigned bit = 128;
        while (reversed & bit) { reversed ^= bit; bit >>= 1; }
        reversed ^= bit;
        if (i < reversed) {
            typedef uint32_t alias_word __attribute__((may_alias));
            alias_word *words = (alias_word *)samples;
            uint32_t value = words[i];
            words[i] = words[reversed];
            words[reversed] = value;
        }
    }
}
