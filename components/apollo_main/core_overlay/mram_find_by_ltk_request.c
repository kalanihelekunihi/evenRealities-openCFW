/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio security-database lookup matched to the stock
 * AppDbFindByLtkReq-style routine at 0x0047ADD4.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_ltk_uintptr;

#ifndef OPEN_CFW_MRAM_LTK_RECORDS
#define OPEN_CFW_MRAM_LTK_RECORDS \
    ((volatile unsigned char *)(open_cfw_mram_ltk_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_LTK_COUNTER
#define OPEN_CFW_MRAM_LTK_COUNTER \
    ((volatile unsigned int *)(open_cfw_mram_ltk_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_LTK_COMPARE
int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);
#define OPEN_CFW_MRAM_LTK_COMPARE(left, right, length) \
    open_cfw_memory_compare((left), (right), (length))
#endif

#define OPEN_CFW_MRAM_LTK_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_LTK_RECORD_SIZE 200U
#define OPEN_CFW_MRAM_LTK_ACTIVE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_LTK_RANDOM_OFFSET 0x44U
#define OPEN_CFW_MRAM_LTK_RANDOM_SIZE 8U
#define OPEN_CFW_MRAM_LTK_DIVERSIFIER_OFFSET 0x4CU
#define OPEN_CFW_MRAM_LTK_TIMESTAMP_OFFSET 0xC4U

__attribute__((used, noinline))
unsigned char *open_cfw_mram_find_by_ltk_request(
    unsigned int encryption_diversifier,
    const unsigned char *random_number
)
{
    volatile unsigned char *record = OPEN_CFW_MRAM_LTK_RECORDS;
    unsigned int index;

#pragma clang loop unroll(disable)
    for (
        index = 0U;
        index < OPEN_CFW_MRAM_LTK_RECORD_COUNT;
        ++index
    ) {
        if (
            record[OPEN_CFW_MRAM_LTK_ACTIVE_OFFSET] != 0U
            && *(volatile unsigned short *)(
                record + OPEN_CFW_MRAM_LTK_DIVERSIFIER_OFFSET
            ) == (unsigned short)encryption_diversifier
            && OPEN_CFW_MRAM_LTK_COMPARE(
                (const void *)(
                    record + OPEN_CFW_MRAM_LTK_RANDOM_OFFSET
                ),
                random_number,
                OPEN_CFW_MRAM_LTK_RANDOM_SIZE
            ) == 0
        ) {
            *OPEN_CFW_MRAM_LTK_COUNTER =
                *OPEN_CFW_MRAM_LTK_COUNTER + 1U;
            *(volatile unsigned int *)(
                record + OPEN_CFW_MRAM_LTK_TIMESTAMP_OFFSET
            ) = *OPEN_CFW_MRAM_LTK_COUNTER;
            return (unsigned char *)record;
        }
        record += OPEN_CFW_MRAM_LTK_RECORD_SIZE;
    }
    return (unsigned char *)0;
}
