#include <stdint.h>

typedef struct {
    const uint32_t *source;
    uint32_t *target;
    uint32_t words;
} touch_copy_record;

typedef struct {
    uint32_t *target;
    uint32_t words;
} touch_zero_record;

/* Bounded source for the copy/zero table loops at 0x4692..0x46d6.
 * Records and ranges are supplied by linker layout; hardware SystemInit,
 * vector dispatch and the following call at 0x46d6 are outside this body. */
void g2_touch_candidate_reset_tables(const touch_copy_record *copy_begin,
                                     const touch_copy_record *copy_end,
                                     const touch_zero_record *zero_begin,
                                     const touch_zero_record *zero_end)
{
    for (const touch_copy_record *record=copy_begin;record<copy_end;record++) {
        for (uint32_t i=0;i<record->words;i++)
            record->target[i]=record->source[i];
    }
    for (const touch_zero_record *record=zero_begin;record<zero_end;record++) {
        for (uint32_t i=0;i<record->words;i++) record->target[i]=0u;
    }
}
