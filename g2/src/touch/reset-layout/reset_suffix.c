#include <stdint.h>

typedef struct { const uint32_t *source; uint32_t *target; uint32_t words; } touch_copy_record;
typedef struct { uint32_t *target; uint32_t words; } touch_zero_record;
extern void g2_touch_candidate_reset_tables(const touch_copy_record *, const touch_copy_record *,
                                            const touch_zero_record *, const touch_zero_record *);

/* Bounded post-SystemInit reset suffix: vector relocation, VTOR and tables.
 * This stops before the stock call to the C runtime at 0x3464. */
void g2_touch_candidate_reset_suffix(const uint32_t *flash_vectors,
                                     uint32_t *ram_vectors,
                                     volatile uint32_t *vtor,
                                     const touch_copy_record *copy_begin,
                                     const touch_copy_record *copy_end,
                                     const touch_zero_record *zero_begin,
                                     const touch_zero_record *zero_end)
{
    for (uint32_t i = 0; i < 48u; ++i) ram_vectors[i] = flash_vectors[i];
    *vtor = (uint32_t)ram_vectors;
    __asm volatile ("dsb sy" ::: "memory");
    g2_touch_candidate_reset_tables(copy_begin, copy_end, zero_begin, zero_end);
}
