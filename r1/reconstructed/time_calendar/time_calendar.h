#ifndef OPENR1_RECONSTRUCTED_TIME_CALENDAR_H
#define OPENR1_RECONSTRUCTED_TIME_CALENDAR_H

/*
 * Provenance banner
 * -----------------
 * Family:         unknown_time_calendar_provider_candidate (Bravechip B210
 *                 "ChipletRing" platform clock-backend, Unix/Gregorian
 *                 conversion, timezone, calendar-adapter, and local
 *                 hour/bucket cluster; interlocked with the `sys rtc`
 *                 named-record layer).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (all sixteen Ghidra bodies) cross-checked against fresh
 *                 Thumb disassembly from the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin
 *                 (arm-none-eabi-objdump; literal pools and the two 24-byte
 *                 month tables read directly from the image).
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  No upstream source, version, or license
 *                 exists for this family; reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Reduced stock functions (application image extents, end-exclusive):
 *
 *   0x0005A7BC..<0x0005A8A0  228  Unix seconds -> broken-down Gregorian time
 *   0x0005A8AC..<0x0005A984  216  broken-down Gregorian time -> Unix seconds
 *   0x0005A990..<0x0005A9B0   32  registered clock-backend snapshot
 *   0x0005AC74..<0x0005ACA6   50  local ten-minute activity bucket
 *   0x0005ACA6..<0x0005ACC4   30  local hour
 *   0x0008AC28..<0x0008ACF2  202  cached packed local-datetime fill
 *   0x0008AD08..<0x0008AD3C   52  registered clock-backend lookup
 *   0x0008AD40..<0x0008AD5C   28  local timestamp accessor
 *   0x0008AD64..<0x0008AD90   44  local-day start calculator
 *   0x0008AD98..<0x0008AD9E    6  time-status accessor
 *   0x0008ADA4..<0x0008ADAE   10  clock-backend timestamp thunk
 *   0x0008ADB4..<0x0008ADBC    8  signed UTC-offset accessor
 *   0x0008AE58..<0x0008AEA4   76  calendar-to-UTC adapter
 *   0x0008AEA4..<0x0008AEAC    8  time-update flag setter
 *   0x0008AEB0..<0x0008AF38  136  registered clock-backend update adapter
 *   0x0008AF40..<0x0008AF8A   74  UTC-to-calendar adapter
 *
 * Recovered data (evidence-derived, not authored content): two identical
 * 24-byte dual month-length tables at 0x00099C5C and 0x00099C74 (non-leap
 * row then leap row), one per converter translation unit; constants 1970,
 * 1900, 86400; validation bounds 70/129 (tm_year), 11/31/23/59.
 *
 * Correlation doc: docs/correlation/TIME-CALENDAR-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Recovered failure conventions of this family.  The bool-style accessors
 * and adapters return 1 on success and 0 on any failure (including the
 * bad-argument cases the stock code already checks); the validating inverse
 * converter returns -1 (stock: 0xFFFFFFFF) on NULL or out-of-range input. */
#define TIME_CALENDAR_CONVERSION_INVALID ((int32_t)-1)

#define TIME_CALENDAR_SECONDS_PER_DAY UINT32_C(86400)
#define TIME_CALENDAR_SECONDS_PER_HOUR UINT32_C(3600)
#define TIME_CALENDAR_SECONDS_PER_MINUTE UINT32_C(60)
#define TIME_CALENDAR_EPOCH_YEAR UINT32_C(1970)

/* Recovered validation bounds of the inverse converter (0x0005A8AC):
 * tm_year in [70,129] (1970-2029), month <= 11, day in [1,31],
 * hour <= 23, minute/second <= 59. */
#define TIME_CALENDAR_MIN_TM_YEAR UINT32_C(70)
#define TIME_CALENDAR_MAX_TM_YEAR UINT32_C(129)

/* Recovered nine-word broken-down time (stock 32-bit struct-tm mirror,
 * 36 bytes; zero-based month and day-of-year, year offset from 1900,
 * Sunday = 0, trailing word always written 0). */
typedef struct {
    uint32_t second;    /* +0x00 */
    uint32_t minute;    /* +0x04 */
    uint32_t hour;      /* +0x08 */
    uint32_t day;       /* +0x0C day of month, 1..31 */
    uint32_t month;     /* +0x10 zero-based */
    uint32_t year;      /* +0x14 years since 1900 */
    uint32_t weekday;   /* +0x18 Sunday = 0 */
    uint32_t year_day;  /* +0x1C zero-based */
    uint32_t zero_tail; /* +0x20 always 0 */
} time_calendar_broken_down;

/* Recovered packed 8-byte public calendar (stock wire/struct layout):
 * full year, one-based month, day, hour, minute, second, weekday. */
typedef struct {
    uint16_t year;   /* +0x00 full year */
    uint8_t month;   /* +0x02 1..12 */
    uint8_t day;     /* +0x03 */
    uint8_t hour;    /* +0x04 */
    uint8_t minute;  /* +0x05 */
    uint8_t second;  /* +0x06 */
    uint8_t weekday; /* +0x07 Sunday = 0 */
} time_calendar_datetime;

/* Recovered packed output of the cached local-datetime fill (0x0008AC28):
 * two little-endian words copied verbatim from the state root. */
typedef struct {
    uint32_t date; /* year | month << 16 | day << 24 */
    uint32_t time; /* hour | minute << 8 | second << 16 | weekday << 24 */
} time_calendar_packed_datetime;

/* Registered clock-backend operations table (recovered slot offsets:
 * get-timestamp at +0x08, update at +0x10; the remaining words are owned by
 * the still-blocked generic-registry interlock and kept opaque). */
typedef uint32_t (*time_calendar_backend_get_fn)(void *context);
typedef int32_t (*time_calendar_backend_update_fn)(uint32_t epoch_seconds,
                                                   int32_t utc_offset_minutes,
                                                   void *context);
typedef struct {
    uintptr_t reserved_00[2];                 /* +0x00..+0x07 */
    time_calendar_backend_get_fn get;         /* +0x08 */
    uintptr_t reserved_0c;                    /* +0x0C */
    time_calendar_backend_update_fn update;   /* +0x10 */
} time_calendar_backend_ops;

/* Recovered registration/sync state root (stock 0x20006820).  The snapshot
 * sub-record used by 0x0005A990 begins at +0x0C (stock 0x2000682C). */
typedef struct {
    uint8_t sync_pending;                     /* +0x00 one-shot sync flag */
    uint8_t reserved_01[3];                   /* +0x01 */
    uint32_t pre_update_timestamp;            /* +0x04 preserved backend time */
    const time_calendar_backend_ops *backend; /* +0x08 thunk/lookup record */
    uint8_t backend_registered;               /* +0x0C snapshot flag */
    uint8_t reserved_0d[3];                   /* +0x0D */
    const time_calendar_backend_ops *snapshot_backend; /* +0x10 */
    void *context;                            /* +0x14 backend context */
} time_calendar_registration;

/* Recovered time state root (stock 0x20016AC4).  The 20-byte region
 * +0x0C..+0x1F is the packed-datetime cache invalidated as a block by the
 * update adapter. */
typedef struct {
    uintptr_t reserved_00[2];   /* +0x00..+0x07 */
    int16_t utc_offset_minutes; /* +0x08 signed UTC offset in minutes */
    uint8_t registered;         /* +0x0A */
    uint8_t time_update_pending;/* +0x0B status / time-update flag */
    uint32_t reserved_0c;       /* +0x0C cleared with the cache block */
    uint32_t cached_day_start;  /* +0x10 UTC epoch of the cached local day */
    uint16_t cached_year;       /* +0x14 */
    uint8_t cached_month;       /* +0x16 */
    uint8_t cached_day;         /* +0x17 */
    uint8_t cached_hour;        /* +0x18 */
    uint8_t cached_minute;      /* +0x19 */
    uint8_t cached_second;      /* +0x1A */
    uint8_t cached_weekday;     /* +0x1B */
    uint8_t cache_valid;        /* +0x1C */
    uint8_t reserved_1d[3];     /* +0x1D..+0x1F */
} time_calendar_state;

/* Module container: exact recovered state at offset 0, then the recovered
 * registration/sync record.  All stock-global dependencies live here; the
 * clock backend itself is bound explicitly (fail-explicit when unbound). */
typedef struct {
    time_calendar_state state;
    time_calendar_registration registration;
} time_calendar;

/* Zeroes all state.  NULL is tolerated (no-op). */
void time_calendar_initialize(time_calendar *clock);

/* Binding seam standing in for the out-of-family stock registration path
 * (generic-registry interlock): installs the backend operations table and
 * context at both recovered slots and raises the two registered flags.
 * NULL backend unbinds; every backend-dependent path then fails explicitly
 * (returns 0) instead of faulting as the stock code would. */
void time_calendar_bind_backend(time_calendar *clock,
                                const time_calendar_backend_ops *backend,
                                void *context);

/* 0x0005A7BC: Unix seconds -> broken-down Gregorian time.  Fills the
 * nine-word struct and returns it; a NULL output falls back to a shared
 * static buffer (stock 0x20016AE4) whose pointer is returned.  Input is the
 * full uint32 epoch domain (stock uses unsigned division throughout). */
time_calendar_broken_down *time_calendar_unix_to_broken_down(
    uint32_t epoch_seconds, time_calendar_broken_down *out);

/* 0x0005A8AC: broken-down Gregorian time -> Unix seconds with hard range
 * validation; returns TIME_CALENDAR_CONVERSION_INVALID (-1) on NULL or
 * out-of-range input.  Day-of-month is only range-checked (1..31), not
 * checked against the month length (recovered laxity). */
int32_t time_calendar_broken_down_to_unix(
    const time_calendar_broken_down *broken_down);

/* 0x0005A990: registered clock-backend snapshot.  Returns 1 and stores the
 * backend operations table and context through the (individually optional)
 * outputs, or 0 when no backend is registered. */
uint32_t time_calendar_backend_snapshot(
    const time_calendar *clock,
    const time_calendar_backend_ops **backend_out, void **context_out);

/* 0x0005AF40: UTC-to-calendar adapter.  Applies the signed minute offset
 * with 32-bit wrap arithmetic (stock add.w), converts, and packs the public
 * 8-byte datetime.  Returns 1 on success, 0 for a NULL output. */
uint32_t time_calendar_utc_to_calendar(int32_t epoch_seconds,
                                       int32_t utc_offset_minutes,
                                       time_calendar_datetime *out);

/* 0x0008AE58: calendar-to-UTC adapter.  Converts the packed datetime to
 * epoch seconds and subtracts offset*60.  Returns 0 for NULL input or when
 * the validating converter rejects the datetime (stock maps -1 to 0). */
int32_t time_calendar_to_utc(const time_calendar_datetime *datetime,
                             int32_t utc_offset_minutes);

/* 0x0005AC74: local ten-minute activity bucket of `epoch_seconds` under the
 * current offset: (hour * 6 + minute / 10) & 0xFF. */
uint8_t time_calendar_activity_bucket(const time_calendar *clock,
                                      uint32_t epoch_seconds);

/* 0x0005ACA6: local hour of `epoch_seconds` under the current offset. */
uint8_t time_calendar_local_hour(const time_calendar *clock,
                                 uint32_t epoch_seconds);

/* 0x0008AC28: cached packed local-datetime fill.  No-op unless a backend is
 * registered and bound and `out` is non-NULL.  The date fields are
 * reconverted only when the cached local-day start changes; the time fields
 * are recomputed on every call.  Recovered quirk: the time-of-day derives
 * from the signed 64-bit remainder used with unsigned division, so
 * pre-1970 local epochs yield wrapped hour values (see correlation doc). */
void time_calendar_local_datetime_fill(time_calendar *clock,
                                       time_calendar_packed_datetime *out);

/* 0x0008AD08: registered clock-backend calendar lookup.  Samples the
 * backend timestamp through the snapshot record and converts it with the
 * current offset.  Returns 1 on success, 0 otherwise. */
uint32_t time_calendar_backend_calendar_lookup(time_calendar *clock,
                                               time_calendar_datetime *out);

/* 0x0008ADA4: clock-backend timestamp thunk; calls the registered get
 * operation with a NULL context (stock passes constant 0).  Returns 0 when
 * unbound (stock dereferences unchecked). */
uint32_t time_calendar_backend_timestamp(const time_calendar *clock);

/* 0x0008AD40: local timestamp accessor: backend timestamp plus the signed
 * offset in minutes times 60, with 32-bit wrap.  Returns 0 when unbound. */
int32_t time_calendar_local_timestamp(const time_calendar *clock);

/* 0x0008AD64: UTC epoch of the current local-day start, computed with
 * signed 64-bit division of (timestamp + offset*60) by 86400.  The returned
 * high word is the recovered (borrow-free) product high word. */
uint64_t time_calendar_local_day_start(const time_calendar *clock);

/* 0x0008ADB4: signed UTC-offset accessor (minutes). */
int32_t time_calendar_utc_offset(const time_calendar *clock);

/* 0x0008AD98: time-status accessor (state byte +0x0B). */
uint8_t time_calendar_status(const time_calendar *clock);

/* 0x0008AEA4: time-update flag setter (state byte +0x0B = 1). */
void time_calendar_set_time_update_flag(time_calendar *clock);

/* 0x0008AEB0: registered clock-backend update adapter.  Requires the
 * registered flag, a snapshot backend, and a non-NULL update operation.
 * Stores a changed offset (truncated to int16) and invalidates the
 * packed-datetime cache, preserves the pre-update backend timestamp exactly
 * once (while sync_pending != 1), calls the backend update operation with
 * (epoch, offset, context), and on a nonzero result invalidates the cache
 * again and records the one-shot sync state.  Returns the backend result. */
int32_t time_calendar_backend_update(time_calendar *clock,
                                     uint32_t epoch_seconds,
                                     int32_t utc_offset_minutes);

#endif
