/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Apollo protected-MRAM record initialization wrapper matched to
 * stock entry 0x0047A85C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_initialize_uintptr;

#ifndef OPEN_CFW_MRAM_INITIALIZE_RECORDS
#define OPEN_CFW_MRAM_INITIALIZE_RECORDS \
    ((unsigned char *)(open_cfw_mram_initialize_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_INITIALIZE_CACHE
unsigned int open_cfw_cache_dcache_invalidate(
    const open_cfw_cache_range *,
    unsigned int
);
#define OPEN_CFW_MRAM_INITIALIZE_CACHE(range, all) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(open_cfw_mram_initialize_uintptr) \
            (range), \
        (all) \
    )
#endif
#ifndef OPEN_CFW_MRAM_INITIALIZE_LOAD
#define OPEN_CFW_MRAM_INITIALIZE_LOAD(records) \
    open_cfw_mram_copy_record_list_to_ram(records)
#endif
#ifndef OPEN_CFW_MRAM_INITIALIZE_SYNC
#define OPEN_CFW_MRAM_INITIALIZE_SYNC() \
    open_cfw_mram_sync_records()
#endif
#ifndef OPEN_CFW_MRAM_INITIALIZE_DUMP
#define OPEN_CFW_MRAM_INITIALIZE_DUMP(record, index) \
    open_cfw_mram_record_diagnostic_dump((record), (index))
#endif

void open_cfw_mram_copy_record_list_to_ram(unsigned char *);
void open_cfw_mram_sync_records(void);
void open_cfw_mram_record_diagnostic_dump(
    const void *,
    unsigned int
);

__attribute__((used, noinline))
void open_cfw_mram_initialize_records(void)
{
    unsigned char *record = OPEN_CFW_MRAM_INITIALIZE_RECORDS;
    unsigned int index;

    (void)OPEN_CFW_MRAM_INITIALIZE_CACHE(0U, 1U);
    OPEN_CFW_MRAM_INITIALIZE_LOAD(record);
    OPEN_CFW_MRAM_INITIALIZE_SYNC();
#pragma clang loop unroll(disable)
    for (index = 0U; index < 10U; ++index) {
        OPEN_CFW_MRAM_INITIALIZE_DUMP(record, index);
        record += 200U;
    }
}
