/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio resolved-address callback matched to stock
 * AppDbHandleResolvedAddr at 0x0047AB6C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_resolved_uintptr;

typedef unsigned int (*open_cfw_mram_resolved_log_level_function)(void);
typedef void (*open_cfw_mram_resolved_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_resolved_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_MRAM_RESOLVED_RECORDS
#define OPEN_CFW_MRAM_RESOLVED_RECORDS \
    ((unsigned char *)(open_cfw_mram_resolved_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL
#define OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() \
    (((open_cfw_mram_resolved_log_level_function) \
        (open_cfw_mram_resolved_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_RESOLVED_LOG
#define OPEN_CFW_MRAM_RESOLVED_LOG(...) \
    (((open_cfw_mram_resolved_log_function) \
        (open_cfw_mram_resolved_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_RESOLVED_TRACE
#define OPEN_CFW_MRAM_RESOLVED_TRACE(...) \
    (((open_cfw_mram_resolved_trace_function) \
        (open_cfw_mram_resolved_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

#define OPEN_CFW_MRAM_RESOLVED_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_RESOLVED_RECORD_SIZE 200U

static __attribute__((always_inline)) inline const void *
open_cfw_mram_resolved_pointer(open_cfw_mram_resolved_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_resolved_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolved_invalid_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVED_LOG(
            1U,
            open_cfw_mram_resolved_pointer(0x0078A0D0U),
            open_cfw_mram_resolved_pointer(0x006D84BCU),
            open_cfw_mram_resolved_pointer(0x0077511CU),
            0x435U,
            open_cfw_mram_resolved_pointer(0x0071C038U)
        );
    }
    if (open_cfw_mram_resolved_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolved_pointer(0x00700304U);

        OPEN_CFW_MRAM_RESOLVED_TRACE(
            0x04000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolved_address_diagnostic(
    const unsigned char *address,
    unsigned int index
)
{
    if ((OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVED_LOG(
            4U,
            open_cfw_mram_resolved_pointer(0x0078A0D0U),
            open_cfw_mram_resolved_pointer(0x006D84BCU),
            open_cfw_mram_resolved_pointer(0x0077511CU),
            0x43BU,
            open_cfw_mram_resolved_pointer(0x006D5ED0U),
            (unsigned short)index,
            address[5U],
            address[4U],
            address[3U],
            address[2U],
            address[1U],
            address[0U]
        );
    }
    if (open_cfw_mram_resolved_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolved_pointer(0x006D4B20U);

        OPEN_CFW_MRAM_RESOLVED_TRACE(
            0x11C00000U,
            identity,
            identity,
            (unsigned short)index,
            address[5U],
            address[4U],
            address[3U],
            address[2U],
            address[1U],
            address[0U]
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolved_ltk_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVED_LOG(
            4U,
            open_cfw_mram_resolved_pointer(0x0078A0D0U),
            open_cfw_mram_resolved_pointer(0x006D84BCU),
            open_cfw_mram_resolved_pointer(0x0077511CU),
            0x440U,
            open_cfw_mram_resolved_pointer(0x006EB5D8U)
        );
    }
    if (open_cfw_mram_resolved_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolved_pointer(0x006E2540U);

        OPEN_CFW_MRAM_RESOLVED_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolved_no_ltk_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVED_LOG(
            2U,
            open_cfw_mram_resolved_pointer(0x0078A0D0U),
            open_cfw_mram_resolved_pointer(0x006D84BCU),
            open_cfw_mram_resolved_pointer(0x0077511CU),
            0x449U,
            open_cfw_mram_resolved_pointer(0x006E62D4U)
        );
    }
    if (open_cfw_mram_resolved_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolved_pointer(0x006DC4B4U);

        OPEN_CFW_MRAM_RESOLVED_TRACE(
            0x08000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_handle_resolved_address(
    const unsigned char *address,
    unsigned int index
)
{
    unsigned int record_index = (unsigned short)index;
    unsigned char *record;

    if (record_index >= OPEN_CFW_MRAM_RESOLVED_RECORD_COUNT) {
        open_cfw_mram_resolved_invalid_diagnostic();
        return 0U;
    }
    record = OPEN_CFW_MRAM_RESOLVED_RECORDS
        + record_index * OPEN_CFW_MRAM_RESOLVED_RECORD_SIZE;
    if (record[0x2FU] == 0U || record[0x30U] == 0U) {
        open_cfw_mram_resolved_invalid_diagnostic();
        return 0U;
    }

    open_cfw_mram_resolved_address_diagnostic(address, record_index);
    if ((record[0x2EU] & 1U) != 0U) {
        open_cfw_mram_resolved_ltk_diagnostic();
        return 1U;
    }

    open_cfw_mram_resolved_no_ltk_diagnostic();
    return 0U;
}
