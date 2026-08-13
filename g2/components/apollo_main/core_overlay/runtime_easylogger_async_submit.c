/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production clean-room source recovery of Apollo main's G2-specific EasyLogger
 * asynchronous submission wrapper at 0x0044AA80...0x0044AA97 in firmware
 * 2.2.6.10.
 *
 * This is downstream transport glue, not pristine EasyLogger
 * elog_async_output.  The private record builder, event-flags handle, and
 * CMSIS event-flags wrapper remain explicit retained seams.
 */

typedef __UINT8_TYPE__ open_cfw_easylogger_async_u8;
typedef __UINT32_TYPE__ open_cfw_easylogger_async_u32;

_Static_assert(
    sizeof(open_cfw_easylogger_async_u8) == 1U,
    "G2 EasyLogger async byte ABI changed"
);
_Static_assert(
    sizeof(open_cfw_easylogger_async_u32) == 4U,
    "G2 EasyLogger async word ABI changed"
);

extern open_cfw_easylogger_async_u32
open_cfw_g2_easylogger_async_record_build_single_owner(
    const char *buffer,
    open_cfw_easylogger_async_u32 length,
    open_cfw_easylogger_async_u32 metadata,
    open_cfw_easylogger_async_u32 level
);

extern void * volatile
    open_cfw_retained_easylogger_async_event_flags;

extern open_cfw_easylogger_async_u32
open_cfw_retained_os_event_flags_set(
    void *event_flags,
    open_cfw_easylogger_async_u32 flags
);

__attribute__((used, noinline))
void open_cfw_g2_easylogger_async_submit(
    const char *buffer,
    open_cfw_easylogger_async_u32 length,
    open_cfw_easylogger_async_u32 level
)
{
    (void)open_cfw_g2_easylogger_async_record_build_single_owner(
        buffer,
        length,
        0U,
        (open_cfw_easylogger_async_u32)(open_cfw_easylogger_async_u8)level
    );
    (void)open_cfw_retained_os_event_flags_set(
        open_cfw_retained_easylogger_async_event_flags,
        1U
    );
}
