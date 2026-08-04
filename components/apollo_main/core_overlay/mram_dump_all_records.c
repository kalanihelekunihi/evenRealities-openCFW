/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio all-record diagnostic iterator matched to stock entry
 * 0x0047CA9C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_dump_all_uintptr;

#ifndef OPEN_CFW_MRAM_DUMP_ALL_RECORDS_BASE
#define OPEN_CFW_MRAM_DUMP_ALL_RECORDS_BASE() \
    (*(unsigned char *volatile *) \
        (open_cfw_mram_dump_all_uintptr)0x0078EE60U)
#endif
#ifndef OPEN_CFW_MRAM_DUMP_ALL_RECORD
#define OPEN_CFW_MRAM_DUMP_ALL_RECORD(record, index) \
    open_cfw_mram_record_diagnostic_dump((record), (index))
#endif

void open_cfw_mram_record_diagnostic_dump(
    const void *,
    unsigned int
);

__attribute__((used, noinline))
void open_cfw_mram_dump_all_records(void)
{
    unsigned char *record = OPEN_CFW_MRAM_DUMP_ALL_RECORDS_BASE();
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < 10U; ++index) {
        OPEN_CFW_MRAM_DUMP_ALL_RECORD(record, index);
        record += 200U;
    }
}
