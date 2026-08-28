/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio application-database address lookup matched to stock
 * AppDbFindByAddr at 0x0047AD74.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_find_uintptr;

typedef unsigned int (*open_cfw_mram_find_map_owner_function)(
    unsigned int
);
typedef unsigned int (*open_cfw_mram_find_compare_function)(
    const void *,
    const void *
);

#ifndef OPEN_CFW_MRAM_FIND_RECORDS
#define OPEN_CFW_MRAM_FIND_RECORDS \
    ((volatile unsigned char *)(open_cfw_mram_find_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_FIND_COUNTER
#define OPEN_CFW_MRAM_FIND_COUNTER \
    ((volatile unsigned int *)(open_cfw_mram_find_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_FIND_MAP_OWNER
#define OPEN_CFW_MRAM_FIND_MAP_OWNER(owner) \
    (((open_cfw_mram_find_map_owner_function) \
        (open_cfw_mram_find_uintptr)0x004D2AA9U)(owner))
#endif
#ifndef OPEN_CFW_MRAM_FIND_COMPARE
#define OPEN_CFW_MRAM_FIND_COMPARE(record, address) \
    (((open_cfw_mram_find_compare_function) \
        (open_cfw_mram_find_uintptr)0x004D294BU)( \
            (record), \
            (address) \
        ))
#endif

#define OPEN_CFW_MRAM_FIND_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_FIND_RECORD_SIZE 200U
#define OPEN_CFW_MRAM_FIND_OWNER_OFFSET 6U
#define OPEN_CFW_MRAM_FIND_ACTIVE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_FIND_TIMESTAMP_OFFSET 0xC4U

__attribute__((used, noinline))
unsigned char *open_cfw_mram_find_by_address(
    unsigned int owner,
    const unsigned char *address
)
{
    volatile unsigned char *record = OPEN_CFW_MRAM_FIND_RECORDS;
    unsigned char mapped_owner = (unsigned char)
        OPEN_CFW_MRAM_FIND_MAP_OWNER((unsigned char)owner);
    unsigned int index;

#pragma clang loop unroll(disable)
    for (
        index = 0U;
        index < OPEN_CFW_MRAM_FIND_RECORD_COUNT;
        ++index
    ) {
        if (
            record[OPEN_CFW_MRAM_FIND_ACTIVE_OFFSET] != 0U
            && record[OPEN_CFW_MRAM_FIND_OWNER_OFFSET] == mapped_owner
            && OPEN_CFW_MRAM_FIND_COMPARE(
                (const void *)record,
                address
            ) != 0U
        ) {
            *OPEN_CFW_MRAM_FIND_COUNTER =
                *OPEN_CFW_MRAM_FIND_COUNTER + 1U;
            *(volatile unsigned int *)(
                record + OPEN_CFW_MRAM_FIND_TIMESTAMP_OFFSET
            ) = *OPEN_CFW_MRAM_FIND_COUNTER;
            return (unsigned char *)record;
        }
        record += OPEN_CFW_MRAM_FIND_RECORD_SIZE;
    }
    return (unsigned char *)0;
}
