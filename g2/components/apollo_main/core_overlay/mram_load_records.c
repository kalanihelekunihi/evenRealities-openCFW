/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Apollo protected-MRAM record loader matched to stock entry
 * 0x004795DC (_CopyRecListFromNvmToRam).
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_load_uintptr;

typedef unsigned int (*open_cfw_mram_load_persist_function)(
    unsigned char *
);
typedef unsigned int (*open_cfw_mram_load_log_level_function)(void);
typedef void (*open_cfw_mram_load_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_load_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef void (*open_cfw_mram_load_hex_function)(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

#define OPEN_CFW_MRAM_LOAD_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_LOAD_NVM_STRIDE 0x100U
#define OPEN_CFW_MRAM_LOAD_RAM_STRIDE 0xC8U

#ifndef OPEN_CFW_MRAM_LOAD_NVM_BASE
#define OPEN_CFW_MRAM_LOAD_NVM_BASE \
    ((const volatile unsigned char *) \
        (open_cfw_mram_load_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_LOAD_ZERO_KEY
#define OPEN_CFW_MRAM_LOAD_ZERO_KEY \
    ((const void *)(open_cfw_mram_load_uintptr)0x00784FA0U)
#endif
#ifndef OPEN_CFW_MRAM_LOAD_CACHE_INVALIDATE
#define OPEN_CFW_MRAM_LOAD_CACHE_INVALIDATE(range, all) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(range), \
        (all) \
    )
#endif
#ifndef OPEN_CFW_MRAM_LOAD_PERSIST
#define OPEN_CFW_MRAM_LOAD_PERSIST(record) \
    (((open_cfw_mram_load_persist_function) \
        (open_cfw_mram_load_uintptr)0x00479B75U)((record)))
#endif
#ifndef OPEN_CFW_MRAM_LOAD_LOG_LEVEL
#define OPEN_CFW_MRAM_LOAD_LOG_LEVEL() \
    (((open_cfw_mram_load_log_level_function) \
        (open_cfw_mram_load_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_LOAD_LOG
#define OPEN_CFW_MRAM_LOAD_LOG(...) \
    (((open_cfw_mram_load_log_function) \
        (open_cfw_mram_load_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_LOAD_TRACE
#define OPEN_CFW_MRAM_LOAD_TRACE(...) \
    (((open_cfw_mram_load_trace_function) \
        (open_cfw_mram_load_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_LOAD_HEX
#define OPEN_CFW_MRAM_LOAD_HEX(...) \
    (((open_cfw_mram_load_hex_function) \
        (open_cfw_mram_load_uintptr)0x0043DACDU)(__VA_ARGS__))
#endif

int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_load_pointer(open_cfw_mram_load_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_load_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_LOAD_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_LOAD_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_pair0(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_MRAM_LOAD_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOAD_LOG(
            4U,
            open_cfw_mram_load_pointer(0x0078A0D0U),
            open_cfw_mram_load_pointer(0x006D84BCU),
            open_cfw_mram_load_pointer(0x0076936CU),
            line,
            open_cfw_mram_load_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_load_trace_enabled()) {
        const void *identity =
            open_cfw_mram_load_pointer(trace_identity);

        OPEN_CFW_MRAM_LOAD_TRACE(event, identity, identity);
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_pair1(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    unsigned int argument0
)
{
    if ((OPEN_CFW_MRAM_LOAD_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOAD_LOG(
            4U,
            open_cfw_mram_load_pointer(0x0078A0D0U),
            open_cfw_mram_load_pointer(0x006D84BCU),
            open_cfw_mram_load_pointer(0x0076936CU),
            line,
            open_cfw_mram_load_pointer(structured_identity),
            argument0
        );
    }
    if (open_cfw_mram_load_trace_enabled()) {
        const void *identity =
            open_cfw_mram_load_pointer(trace_identity);

        OPEN_CFW_MRAM_LOAD_TRACE(
            event,
            identity,
            identity,
            argument0
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_pair2(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    unsigned int argument0,
    unsigned int argument1
)
{
    if ((OPEN_CFW_MRAM_LOAD_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOAD_LOG(
            4U,
            open_cfw_mram_load_pointer(0x0078A0D0U),
            open_cfw_mram_load_pointer(0x006D84BCU),
            open_cfw_mram_load_pointer(0x0076936CU),
            line,
            open_cfw_mram_load_pointer(structured_identity),
            argument0,
            argument1
        );
    }
    if (open_cfw_mram_load_trace_enabled()) {
        const void *identity =
            open_cfw_mram_load_pointer(trace_identity);

        OPEN_CFW_MRAM_LOAD_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_pair3(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    unsigned int argument0,
    unsigned int argument1,
    unsigned int argument2
)
{
    if ((OPEN_CFW_MRAM_LOAD_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOAD_LOG(
            4U,
            open_cfw_mram_load_pointer(0x0078A0D0U),
            open_cfw_mram_load_pointer(0x006D84BCU),
            open_cfw_mram_load_pointer(0x0076936CU),
            line,
            open_cfw_mram_load_pointer(structured_identity),
            argument0,
            argument1,
            argument2
        );
    }
    if (open_cfw_mram_load_trace_enabled()) {
        const void *identity =
            open_cfw_mram_load_pointer(trace_identity);

        OPEN_CFW_MRAM_LOAD_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1,
            argument2
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_pair9(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    unsigned int argument0,
    unsigned int argument1,
    unsigned int argument2,
    unsigned int argument3,
    unsigned int argument4,
    unsigned int argument5,
    unsigned int argument6,
    unsigned int argument7,
    unsigned int argument8
)
{
    if ((OPEN_CFW_MRAM_LOAD_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOAD_LOG(
            4U,
            open_cfw_mram_load_pointer(0x0078A0D0U),
            open_cfw_mram_load_pointer(0x006D84BCU),
            open_cfw_mram_load_pointer(0x0076936CU),
            line,
            open_cfw_mram_load_pointer(structured_identity),
            argument0,
            argument1,
            argument2,
            argument3,
            argument4,
            argument5,
            argument6,
            argument7,
            argument8
        );
    }
    if (open_cfw_mram_load_trace_enabled()) {
        const void *identity =
            open_cfw_mram_load_pointer(trace_identity);

        OPEN_CFW_MRAM_LOAD_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1,
            argument2,
            argument3,
            argument4,
            argument5,
            argument6,
            argument7,
            argument8
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_from_nvm(
    unsigned char *destination,
    const volatile unsigned char *source
)
{
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_LOAD_RAM_STRIDE; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_to_ram(
    unsigned char *destination,
    const unsigned char *source
)
{
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_LOAD_RAM_STRIDE; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_load_clear(unsigned char *destination)
{
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_LOAD_RAM_STRIDE; ++index) {
        destination[index] = 0U;
    }
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_load_u32(const unsigned char *pointer)
{
    return (
        (unsigned int)pointer[0]
        | ((unsigned int)pointer[1] << 8U)
        | ((unsigned int)pointer[2] << 16U)
        | ((unsigned int)pointer[3] << 24U)
    );
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_load_key_mask(const unsigned char *record)
{
    static const unsigned char offsets[4] = {
        0x34U,
        0x50U,
        0x07U,
        0x1EU,
    };
    unsigned int mask = 0U;
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < 4U; ++index) {
        if (
            open_cfw_memory_compare(
                record + offsets[index],
                OPEN_CFW_MRAM_LOAD_ZERO_KEY,
                16U
            ) != 0
        ) {
            mask |= 1U << index;
        }
    }
    return mask;
}

/*
 * Load the protected 0x100-byte-stride MRAM slots into the caller's compact
 * 0xC8-byte-stride RAM table. Zero and erased first words terminate the scan
 * without modifying the current or subsequent RAM slots.
 */
__attribute__((used, noinline))
void open_cfw_mram_copy_record_list_to_ram(unsigned char *destination)
{
    const volatile unsigned char *source = OPEN_CFW_MRAM_LOAD_NVM_BASE;
    unsigned char record[OPEN_CFW_MRAM_LOAD_RAM_STRIDE];
    unsigned int loaded = 0U;
    unsigned int record_index;

    open_cfw_mram_load_pair0(
        0x13AU,
        0x00708FE4U,
        0x10000000U,
        0x006F16D0U
    );
    (void)OPEN_CFW_MRAM_LOAD_CACHE_INVALIDATE(0U, 1U);

    for (
        record_index = 0U;
        record_index < OPEN_CFW_MRAM_LOAD_RECORD_COUNT;
        ++record_index
    ) {
        unsigned int mask;

        open_cfw_mram_load_from_nvm(record, source);
        if (
            open_cfw_mram_load_u32(record) == 0U
            || open_cfw_mram_load_u32(record) == 0xFFFFFFFFU
        ) {
            open_cfw_mram_load_pair1(
                0x188U,
                0x00709064U,
                0x10400000U,
                0x006F1768U,
                (unsigned char)record_index
            );
            break;
        }

        if (record[0x30U] == 1U) {
            mask = open_cfw_mram_load_key_mask(record);
            if (record[0x2EU] != (unsigned char)mask) {
                open_cfw_mram_load_pair2(
                    0x15BU,
                    0x006D9E40U,
                    0x10800000U,
                    0x006A65B4U,
                    record[0x2EU],
                    (unsigned char)mask
                );
                record[0x2EU] = (unsigned char)mask;
                (void)OPEN_CFW_MRAM_LOAD_PERSIST(record);
            }
        }

        if (record[0x30U] == 1U && record[0x2EU] != 0U) {
            open_cfw_mram_load_to_ram(destination, record);
            destination[0x2FU] = 1U;
            destination[0x30U] = 1U;
            open_cfw_mram_load_pair2(
                0x16CU,
                0x00709024U,
                0x10800000U,
                0x006F171CU,
                (unsigned char)record_index,
                record[0x2EU]
            );
            if ((record[0x2EU] & 4U) != 0U) {
                OPEN_CFW_MRAM_LOAD_HEX(
                    open_cfw_mram_load_pointer(0x0078A0E8U),
                    16U,
                    destination + 7U,
                    16U
                );
            }
            open_cfw_mram_load_pair9(
                0x176U,
                0x006A68C4U,
                0x12400000U,
                0x006D5E58U,
                (unsigned char)record_index,
                record[0x2EU],
                record[0x30U],
                destination[5],
                destination[4],
                destination[3],
                destination[2],
                destination[1],
                destination[0]
            );
            ++loaded;
        }
        else {
            open_cfw_mram_load_pair3(
                0x17EU,
                0x006E61D8U,
                0x10C00000U,
                0x006DF4ECU,
                (unsigned char)record_index,
                record[0x30U],
                record[0x2EU]
            );
            open_cfw_mram_load_clear(destination);
            destination[0x2FU] = 0U;
            destination[0x30U] = 0U;
        }

        source += OPEN_CFW_MRAM_LOAD_NVM_STRIDE;
        destination += OPEN_CFW_MRAM_LOAD_RAM_STRIDE;
    }

    open_cfw_mram_load_pair1(
        0x18DU,
        0x007090A4U,
        0x10400000U,
        0x006F8294U,
        (unsigned char)loaded
    );
}
