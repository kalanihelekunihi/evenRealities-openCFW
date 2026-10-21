/*
 * Provenance banner
 * -----------------
 * Family:         unknown_time_calendar_provider_candidate (Bravechip B210
 *                 "ChipletRing" platform clock-backend, Unix/Gregorian
 *                 conversion, timezone, calendar-adapter, and local
 *                 hour/bucket cluster).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (all sixteen Ghidra bodies) cross-checked against fresh
 *                 Thumb disassembly from the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  Reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Per-function mapping (stock extent, end-exclusive / size -> symbol here):
 *
 *   0x0005A7BC..<0x0005A8A0  228 -> time_calendar_unix_to_broken_down
 *   0x0005A8AC..<0x0005A984  216 -> time_calendar_broken_down_to_unix
 *   0x0005A990..<0x0005A9B0   32 -> time_calendar_backend_snapshot
 *   0x0005AC74..<0x0005ACA6   50 -> time_calendar_activity_bucket
 *   0x0005ACA6..<0x0005ACC4   30 -> time_calendar_local_hour
 *   0x0008AC28..<0x0008ACF2  202 -> time_calendar_local_datetime_fill
 *   0x0008AD08..<0x0008AD3C   52 -> time_calendar_backend_calendar_lookup
 *   0x0008AD40..<0x0008AD5C   28 -> time_calendar_local_timestamp
 *   0x0008AD64..<0x0008AD90   44 -> time_calendar_local_day_start
 *   0x0008AD98..<0x0008AD9E    6 -> time_calendar_status
 *   0x0008ADA4..<0x0008ADAE   10 -> time_calendar_backend_timestamp
 *   0x0008ADB4..<0x0008ADBC    8 -> time_calendar_utc_offset
 *   0x0008AE58..<0x0008AEA4   76 -> time_calendar_to_utc
 *   0x0008AEA4..<0x0008AEAC    8 -> time_calendar_set_time_update_flag
 *   0x0008AEB0..<0x0008AF38  136 -> time_calendar_backend_update
 *   0x0008AF40..<0x0008AF8A   74 -> time_calendar_utc_to_calendar
 *
 * Observable behavior is preserved; restructuring is limited to the explicit
 * backend binding (stock reached the backend through shared globals and
 * dereferenced it unchecked) and NULL guards that return the family's
 * recovered failure values (0 for the bool-style functions, -1 for the
 * validating inverse converter).  Every divergence is listed in
 * docs/correlation/TIME-CALENDAR-REDUCTION-CORRELATION.md.
 */

#include "time_calendar/time_calendar.h"

/* The recovered field offsets are a property of the 32-bit target ABI; on
 * wider host pointer ABIs the C layout legitimately differs, so the exact
 * layout asserts apply to the target ABI only. */
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(time_calendar_broken_down) == 36u,
               "recovered broken-down time is 36 bytes");
_Static_assert(sizeof(time_calendar_datetime) == 8u,
               "recovered packed datetime is 8 bytes");
_Static_assert(offsetof(time_calendar_backend_ops, get) == 0x08u,
               "backend ops +0x08");
_Static_assert(offsetof(time_calendar_backend_ops, update) == 0x10u,
               "backend ops +0x10");
_Static_assert(sizeof(time_calendar_backend_ops) == 0x14u,
               "recovered backend ops record is 20 bytes");
_Static_assert(offsetof(time_calendar_registration, pre_update_timestamp) == 0x04u,
               "registration +0x04");
_Static_assert(offsetof(time_calendar_registration, backend) == 0x08u,
               "registration +0x08");
_Static_assert(offsetof(time_calendar_registration, backend_registered) == 0x0Cu,
               "registration +0x0C");
_Static_assert(offsetof(time_calendar_registration, snapshot_backend) == 0x10u,
               "registration +0x10");
_Static_assert(offsetof(time_calendar_registration, context) == 0x14u,
               "registration +0x14");
_Static_assert(sizeof(time_calendar_registration) == 0x18u,
               "recovered registration record is 24 bytes");
_Static_assert(offsetof(time_calendar_state, utc_offset_minutes) == 0x08u,
               "state +0x08");
_Static_assert(offsetof(time_calendar_state, registered) == 0x0Au,
               "state +0x0A");
_Static_assert(offsetof(time_calendar_state, time_update_pending) == 0x0Bu,
               "state +0x0B");
_Static_assert(offsetof(time_calendar_state, reserved_0c) == 0x0Cu,
               "cache invalidation span begins at state +0x0C");
_Static_assert(offsetof(time_calendar_state, cached_day_start) == 0x10u,
               "state +0x10");
_Static_assert(offsetof(time_calendar_state, cached_year) == 0x14u,
               "state +0x14");
_Static_assert(offsetof(time_calendar_state, cached_month) == 0x16u,
               "state +0x16");
_Static_assert(offsetof(time_calendar_state, cached_day) == 0x17u,
               "state +0x17");
_Static_assert(offsetof(time_calendar_state, cached_hour) == 0x18u,
               "state +0x18");
_Static_assert(offsetof(time_calendar_state, cached_minute) == 0x19u,
               "state +0x19");
_Static_assert(offsetof(time_calendar_state, cached_second) == 0x1Au,
               "state +0x1A");
_Static_assert(offsetof(time_calendar_state, cached_weekday) == 0x1Bu,
               "state +0x1B");
_Static_assert(offsetof(time_calendar_state, cache_valid) == 0x1Cu,
               "state +0x1C");
_Static_assert(sizeof(time_calendar_state) == 0x20u,
               "recovered state root is 32 bytes");
#endif

/* Recovered 20-byte cache invalidation (stock: memset thunk 0x000277AA over
 * state +0x0C..+0x1F).  The span from reserved_0c to the end of the struct
 * is exactly those bytes on the 32-bit target ABI (asserted above) and the
 * equivalent fields on wider host ABIs.  Local loop; the freestanding build
 * uses no libc. */
static void cache_invalidate(time_calendar_state *state) {
    uint8_t *bytes = (uint8_t *)state;
    for (size_t index = offsetof(time_calendar_state, reserved_0c);
            index < sizeof(*state); ++index) {
        bytes[index] = 0u;
    }
}

/* Evidence-derived data: the stock image carries two identical private
 * 24-byte dual month-length tables (non-leap row then leap row), one per
 * converter translation unit, at 0x00099C5C (forward converter) and
 * 0x00099C74 (inverse converter).  Bytes read from the rebuilt image. */
static const uint8_t month_days_forward[24] = {
    31u, 28u, 31u, 30u, 31u, 30u, 31u, 31u, 30u, 31u, 30u, 31u,
    31u, 29u, 31u, 30u, 31u, 30u, 31u, 31u, 30u, 31u, 30u, 31u
};
static const uint8_t month_days_inverse[24] = {
    31u, 28u, 31u, 30u, 31u, 30u, 31u, 31u, 30u, 31u, 30u, 31u,
    31u, 29u, 31u, 30u, 31u, 30u, 31u, 31u, 30u, 31u, 30u, 31u
};

/* Stock NULL-output fallback for the forward converter (0x20016AE4): one
 * shared static buffer, returned to the caller. */
static time_calendar_broken_down unix_to_broken_down_fallback;

/* Recovered Gregorian leap rule: divisible by 4 and not by 100, or by 400.
 * (The stock mod-4 miss path still tests mod 400; the rule is identical.) */
static bool is_leap_year(uint32_t year) {
    return (((year & 3u) == 0u) && ((year % 100u) != 0u)) ||
           ((year % 400u) == 0u);
}


int32_t time_calendar_broken_down_to_unix(
        const time_calendar_broken_down *broken_down) {
    if (broken_down == NULL) {
        return TIME_CALENDAR_CONVERSION_INVALID;
    }
    /* Recovered hard validation (unsigned range tests, in stock order). */
    if (broken_down->year - TIME_CALENDAR_MIN_TM_YEAR >
            TIME_CALENDAR_MAX_TM_YEAR - TIME_CALENDAR_MIN_TM_YEAR) {
        return TIME_CALENDAR_CONVERSION_INVALID;
    }
    if (broken_down->month > 11u || broken_down->day - 1u > 30u ||
            broken_down->hour > 23u || broken_down->minute > 59u ||
            broken_down->second > 59u) {
        return TIME_CALENDAR_CONVERSION_INVALID;
    }
    const uint32_t full_year = broken_down->year + 1900u;
    uint32_t days = 0u;
    for (uint32_t year = TIME_CALENDAR_EPOCH_YEAR; year < full_year; ++year) {
        days += is_leap_year(year) ? 366u : 365u;
    }
    const uint8_t *table =
        is_leap_year(full_year) ? month_days_inverse + 12 : month_days_inverse;
    for (uint32_t index = 1u; index < broken_down->month + 1u; ++index) {
        days += table[index - 1u];
    }
    const uint32_t epoch = broken_down->second +
        (days + broken_down->day - 1u) * TIME_CALENDAR_SECONDS_PER_DAY +
        broken_down->hour * TIME_CALENDAR_SECONDS_PER_HOUR +
        broken_down->minute * TIME_CALENDAR_SECONDS_PER_MINUTE;
    return (int32_t)epoch;
}
uint32_t time_calendar_utc_to_calendar(int32_t epoch_seconds,
                                       int32_t utc_offset_minutes,
                                       time_calendar_datetime *out) {
    if (out == NULL) {
        return 0u;
    }
    /* Recovered 32-bit wrap arithmetic (stock: rsb/lsl scale, add.w). */
    const uint32_t local = (uint32_t)epoch_seconds +
        (uint32_t)utc_offset_minutes * TIME_CALENDAR_SECONDS_PER_MINUTE;
    time_calendar_broken_down broken_down;
    const time_calendar_broken_down *filled =
        time_calendar_unix_to_broken_down(local, &broken_down);
    if (filled == NULL) {
        /* Unreachable with a valid buffer; stock keeps the same check. */
        return 0u;
    }
    out->year = (uint16_t)(filled->year + 1900u);
    out->month = (uint8_t)(filled->month + 1u);
    out->day = (uint8_t)filled->day;
    out->hour = (uint8_t)filled->hour;
    out->minute = (uint8_t)filled->minute;
    out->second = (uint8_t)filled->second;
    out->weekday = (uint8_t)filled->weekday;
    return 1u;
}
int32_t time_calendar_to_utc(const time_calendar_datetime *datetime,
                             int32_t utc_offset_minutes) {
    if (datetime == NULL) {
        return 0;
    }
    /* Recovered field mapping into the nine-word struct; the byte-to-word
     * subtractions wrap, so out-of-range fields fail the recovered
     * validation instead of converting. */
    time_calendar_broken_down broken_down;
    broken_down.second = datetime->second;
    broken_down.minute = datetime->minute;
    broken_down.hour = datetime->hour;
    broken_down.day = datetime->day;
    broken_down.month = (uint32_t)datetime->month - 1u;
    broken_down.year = (uint32_t)datetime->year - 1900u;
    broken_down.weekday = datetime->weekday;
    broken_down.year_day = 0u;
    broken_down.zero_tail = 0u;
    const int32_t epoch = time_calendar_broken_down_to_unix(&broken_down);
    if (epoch == TIME_CALENDAR_CONVERSION_INVALID) {
        return 0;
    }
    return (int32_t)((uint32_t)epoch -
                     (uint32_t)utc_offset_minutes *
                         TIME_CALENDAR_SECONDS_PER_MINUTE);
}
