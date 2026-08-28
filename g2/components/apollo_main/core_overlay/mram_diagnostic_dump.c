/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Apollo MRAM record diagnostic dump matched to stock entry
 * 0x004789B0.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_dump_uintptr;

typedef unsigned int (*open_cfw_mram_dump_log_level_function)(void);
typedef void (*open_cfw_mram_dump_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_dump_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef void (*open_cfw_mram_dump_hex_function)(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

#ifndef OPEN_CFW_MRAM_DUMP_BASE
#define OPEN_CFW_MRAM_DUMP_BASE \
    ((const volatile unsigned char *) \
        (open_cfw_mram_dump_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_DUMP_LOG_LEVEL
#define OPEN_CFW_MRAM_DUMP_LOG_LEVEL() \
    (((open_cfw_mram_dump_log_level_function) \
        (open_cfw_mram_dump_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_DUMP_LOG
#define OPEN_CFW_MRAM_DUMP_LOG(...) \
    (((open_cfw_mram_dump_log_function) \
        (open_cfw_mram_dump_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_DUMP_TRACE
#define OPEN_CFW_MRAM_DUMP_TRACE(...) \
    (((open_cfw_mram_dump_trace_function) \
        (open_cfw_mram_dump_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_DUMP_HEX
#define OPEN_CFW_MRAM_DUMP_HEX(...) \
    (((open_cfw_mram_dump_hex_function) \
        (open_cfw_mram_dump_uintptr)0x0043DACDU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_mram_dump_pointer(open_cfw_mram_dump_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_dump_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_DUMP_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_DUMP_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_dump_u16(const volatile unsigned char *pointer)
{
    return (
        (unsigned int)pointer[0]
        | ((unsigned int)pointer[1] << 8U)
    );
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_dump_u32(const volatile unsigned char *pointer)
{
    return (
        (unsigned int)pointer[0]
        | ((unsigned int)pointer[1] << 8U)
        | ((unsigned int)pointer[2] << 16U)
        | ((unsigned int)pointer[3] << 24U)
    );
}

static __attribute__((always_inline)) inline void
open_cfw_mram_dump_pair0(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_MRAM_DUMP_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_DUMP_LOG(
            severity,
            open_cfw_mram_dump_pointer(0x0078A0D0U),
            open_cfw_mram_dump_pointer(0x006D84BCU),
            open_cfw_mram_dump_pointer(0x0077DD6CU),
            line,
            open_cfw_mram_dump_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_dump_trace_enabled()) {
        const void *identity =
            open_cfw_mram_dump_pointer(trace_identity);

        OPEN_CFW_MRAM_DUMP_TRACE(event, identity, identity);
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_dump_pair1(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_dump_uintptr argument
)
{
    if ((OPEN_CFW_MRAM_DUMP_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_DUMP_LOG(
            severity,
            open_cfw_mram_dump_pointer(0x0078A0D0U),
            open_cfw_mram_dump_pointer(0x006D84BCU),
            open_cfw_mram_dump_pointer(0x0077DD6CU),
            line,
            open_cfw_mram_dump_pointer(structured_identity),
            argument
        );
    }
    if (open_cfw_mram_dump_trace_enabled()) {
        const void *identity =
            open_cfw_mram_dump_pointer(trace_identity);

        OPEN_CFW_MRAM_DUMP_TRACE(
            event,
            identity,
            identity,
            argument
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_dump_pair2(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_dump_uintptr argument0,
    open_cfw_mram_dump_uintptr argument1
)
{
    if ((OPEN_CFW_MRAM_DUMP_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_DUMP_LOG(
            severity,
            open_cfw_mram_dump_pointer(0x0078A0D0U),
            open_cfw_mram_dump_pointer(0x006D84BCU),
            open_cfw_mram_dump_pointer(0x0077DD6CU),
            line,
            open_cfw_mram_dump_pointer(structured_identity),
            argument0,
            argument1
        );
    }
    if (open_cfw_mram_dump_trace_enabled()) {
        const void *identity =
            open_cfw_mram_dump_pointer(trace_identity);

        OPEN_CFW_MRAM_DUMP_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_dump_pair6(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_dump_uintptr argument0,
    open_cfw_mram_dump_uintptr argument1,
    open_cfw_mram_dump_uintptr argument2,
    open_cfw_mram_dump_uintptr argument3,
    open_cfw_mram_dump_uintptr argument4,
    open_cfw_mram_dump_uintptr argument5
)
{
    if ((OPEN_CFW_MRAM_DUMP_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_DUMP_LOG(
            severity,
            open_cfw_mram_dump_pointer(0x0078A0D0U),
            open_cfw_mram_dump_pointer(0x006D84BCU),
            open_cfw_mram_dump_pointer(0x0077DD6CU),
            line,
            open_cfw_mram_dump_pointer(structured_identity),
            argument0,
            argument1,
            argument2,
            argument3,
            argument4,
            argument5
        );
    }
    if (open_cfw_mram_dump_trace_enabled()) {
        const void *identity =
            open_cfw_mram_dump_pointer(trace_identity);

        OPEN_CFW_MRAM_DUMP_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1,
            argument2,
            argument3,
            argument4,
            argument5
        );
    }
}

static __attribute__((always_inline)) inline
open_cfw_mram_dump_uintptr
open_cfw_mram_dump_enum_label(unsigned int value)
{
    if (value == 0U) {
        return 0x0078CA14U;
    }
    if (value == 1U) {
        return 0x0078CA1CU;
    }
    return 0x0078CA24U;
}

static __attribute__((always_inline)) inline
open_cfw_mram_dump_uintptr
open_cfw_mram_dump_boolean_label(unsigned int value)
{
    return value != 0U ? 0x0078CA2CU : 0x0078CA34U;
}

static __attribute__((always_inline)) inline
open_cfw_mram_dump_uintptr
open_cfw_mram_dump_enabled_label(unsigned int value)
{
    return value != 0U ? 0x0078A100U : 0x00784EF0U;
}

/*
 * Emit the complete stock diagnostic view for one 0x100-byte protected MRAM
 * record. The first caller argument is ignored by the stock implementation;
 * the record is always selected from the fixed 0x007FF000 table.
 */
__attribute__((used, noinline))
void open_cfw_mram_record_diagnostic_dump(
    const void *ignored_record,
    unsigned int record_index
)
{
    const volatile unsigned char *record;
    unsigned int index;

    (void)ignored_record;
    record_index = (unsigned char)record_index;
    record = OPEN_CFW_MRAM_DUMP_BASE + (record_index << 8U);

    if (record == (const volatile unsigned char *)0) {
        open_cfw_mram_dump_pair0(
            1U,
            0xB5U,
            0x00769238U,
            0x04000000U,
            0x00747634U
        );
        return;
    }

    open_cfw_mram_dump_pair1(
        4U,
        0xB9U,
        0x0074765CU,
        0x10400000U,
        0x00726CECU,
        record_index
    );
    open_cfw_mram_dump_pair6(
        4U,
        0xBDU,
        0x00731814U,
        0x11800000U,
        0x00712550U,
        record[5],
        record[4],
        record[3],
        record[2],
        record[1],
        record[0]
    );
    open_cfw_mram_dump_pair2(
        4U,
        0xC1U,
        0x00775044U,
        0x10800000U,
        0x00751DACU,
        open_cfw_mram_dump_enum_label(record[6]),
        record[6]
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC2U,
        0x0077DD80U,
        0x10400000U,
        0x0075DD70U,
        open_cfw_mram_dump_enabled_label(record[0x2FU])
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC3U,
        0x0077DD94U,
        0x10400000U,
        0x0075DD90U,
        open_cfw_mram_dump_enabled_label(record[0x30U])
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC4U,
        0x0077505CU,
        0x10400000U,
        0x0075DDB0U,
        open_cfw_mram_dump_u32(record + 0xC4U)
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC5U,
        0x00775074U,
        0x10400000U,
        0x00751DD0U,
        record[0x2EU]
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC6U,
        0x00751DF4U,
        0x10400000U,
        0x0073C0BCU,
        open_cfw_mram_dump_boolean_label(record[0x31U])
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC7U,
        0x0077DDA8U,
        0x10400000U,
        0x0075DDD0U,
        open_cfw_mram_dump_boolean_label(record[0x32U])
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xC8U,
        0x0077508CU,
        0x10400000U,
        0x00751E18U,
        record[0x2EU]
    );

    OPEN_CFW_MRAM_DUMP_HEX(
        open_cfw_mram_dump_pointer(0x0078A0E8U),
        0x10U,
        (const void *)(record + 7U),
        0x10U
    );
    OPEN_CFW_MRAM_DUMP_HEX(
        open_cfw_mram_dump_pointer(0x0078A0F4U),
        0x10U,
        (const void *)(record + 0x1EU),
        0x10U
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xD0U,
        0x00769254U,
        0x10000000U,
        0x00747684U
    );
    OPEN_CFW_MRAM_DUMP_HEX(
        open_cfw_mram_dump_pointer(0x00784EE0U),
        0x10U,
        (const void *)(record + 0x34U),
        0x10U
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xD3U,
        0x0075DDF0U,
        0x10400000U,
        0x007476ACU,
        record[0x4EU]
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xD4U,
        0x00769270U,
        0x10400000U,
        0x007476D4U,
        open_cfw_mram_dump_enabled_label(record[0x4FU])
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xD7U,
        0x0076928CU,
        0x10000000U,
        0x007476FCU
    );
    OPEN_CFW_MRAM_DUMP_HEX(
        open_cfw_mram_dump_pointer(0x00784F00U),
        0x10U,
        (const void *)(record + 0x50U),
        0x10U
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xD9U,
        0x007692A8U,
        0x10400000U,
        0x00747724U,
        record[0x6AU]
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xDCU,
        0x007692C4U,
        0x10000000U,
        0x0074774CU
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xDDU,
        0x007750A4U,
        0x10400000U,
        0x00751E3CU,
        open_cfw_mram_dump_u32(record + 0x80U)
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xDEU,
        0x007750BCU,
        0x10400000U,
        0x00751E60U,
        record[0x84U]
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xE0U,
        0x00784F10U,
        0x10000000U,
        0x007750D4U
    );
    for (index = 0U; index < 10U; ++index) {
        unsigned int value =
            open_cfw_mram_dump_u16(record + 0x6CU + (index << 1U));

        if (value != 0U) {
            open_cfw_mram_dump_pair2(
                4U,
                0xE3U,
                0x00784F20U,
                0x10800000U,
                0x007750ECU,
                index,
                value
            );
        }
    }
    open_cfw_mram_dump_pair0(
        4U,
        0xE7U,
        0x007692E0U,
        0x10000000U,
        0x00747774U
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xE9U,
        0x0078CA3CU,
        0x10400000U,
        0x00784F30U,
        record[0x85U]
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xEDU,
        0x007692FCU,
        0x10000000U,
        0x0074779CU
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xEEU,
        0x0077DDBCU,
        0x10400000U,
        0x0075DE10U,
        open_cfw_mram_dump_boolean_label(record[0x86U])
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xF2U,
        0x00784F40U,
        0x10000000U,
        0x00769318U
    );
    for (index = 0U; index < 21U; ++index) {
        unsigned int value =
            open_cfw_mram_dump_u16(record + 0x98U + (index << 1U));

        if (value != 0U) {
            open_cfw_mram_dump_pair1(
                4U,
                0xF5U,
                0x0078CA44U,
                0x10400000U,
                0x0077DDD0U,
                value
            );
        }
    }
    open_cfw_mram_dump_pair1(
        4U,
        0xF9U,
        0x00769334U,
        0x10400000U,
        0x00751E84U,
        record[0xC2U]
    );
    open_cfw_mram_dump_pair1(
        4U,
        0xFAU,
        0x00784F50U,
        0x10400000U,
        0x00769350U,
        open_cfw_mram_dump_boolean_label(record[0xC3U])
    );
    open_cfw_mram_dump_pair0(
        4U,
        0xFBU,
        0x0075DE30U,
        0x10000000U,
        0x0073C0E8U
    );
}
