/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio database reset matched to stock AppDbDeleteAllRecords at
 * 0x0047ACF8.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_delete_uintptr;

typedef unsigned int (*open_cfw_mram_delete_log_level_function)(void);
typedef void (*open_cfw_mram_delete_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_delete_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_MRAM_DELETE_RECORDS
#define OPEN_CFW_MRAM_DELETE_RECORDS \
    ((volatile unsigned char *)(open_cfw_mram_delete_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_DELETE_LOG_LEVEL
#define OPEN_CFW_MRAM_DELETE_LOG_LEVEL() \
    (((open_cfw_mram_delete_log_level_function) \
        (open_cfw_mram_delete_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_DELETE_LOG
#define OPEN_CFW_MRAM_DELETE_LOG(...) \
    (((open_cfw_mram_delete_log_function) \
        (open_cfw_mram_delete_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_DELETE_TRACE
#define OPEN_CFW_MRAM_DELETE_TRACE(...) \
    (((open_cfw_mram_delete_trace_function) \
        (open_cfw_mram_delete_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_DELETE_CLEAR_PREFIX_BYTE
#define OPEN_CFW_MRAM_DELETE_CLEAR_PREFIX_BYTE(record, index) \
    ((record)[index] = 0U)
#endif

void open_cfw_mram_program_zero_region(void);

#ifndef OPEN_CFW_MRAM_DELETE_PROGRAM_ZERO_REGION
#define OPEN_CFW_MRAM_DELETE_PROGRAM_ZERO_REGION() \
    open_cfw_mram_program_zero_region()
#endif

#define OPEN_CFW_MRAM_DELETE_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_DELETE_RECORD_SIZE 200U
#define OPEN_CFW_MRAM_DELETE_ADDRESS_SIZE 6U

static __attribute__((always_inline)) inline const void *
open_cfw_mram_delete_pointer(open_cfw_mram_delete_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_delete_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_DELETE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_DELETE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_delete_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_DELETE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_DELETE_LOG(
            4U,
            open_cfw_mram_delete_pointer(0x0078A0D0U),
            open_cfw_mram_delete_pointer(0x006D84BCU),
            open_cfw_mram_delete_pointer(0x00775134U),
            0x45AU,
            open_cfw_mram_delete_pointer(0x0077514CU)
        );
    }
    if (open_cfw_mram_delete_trace_enabled()) {
        const void *identity =
            open_cfw_mram_delete_pointer(0x00751ECCU);

        OPEN_CFW_MRAM_DELETE_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_delete_all_records(void)
{
    volatile unsigned char *record = OPEN_CFW_MRAM_DELETE_RECORDS;
    unsigned int record_index;

    open_cfw_mram_delete_diagnostic();
    for (
        record_index = 0U;
        record_index < OPEN_CFW_MRAM_DELETE_RECORD_COUNT;
        ++record_index
    ) {
        unsigned int address_index;

        record[0x2FU] = 0U;
        record[0x30U] = 0U;
        for (
            address_index = 0U;
            address_index < OPEN_CFW_MRAM_DELETE_ADDRESS_SIZE;
            ++address_index
        ) {
            OPEN_CFW_MRAM_DELETE_CLEAR_PREFIX_BYTE(
                record,
                address_index
            );
        }
        record += OPEN_CFW_MRAM_DELETE_RECORD_SIZE;
    }
    OPEN_CFW_MRAM_DELETE_PROGRAM_ZERO_REGION();
}
