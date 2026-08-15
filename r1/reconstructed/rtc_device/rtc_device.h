#ifndef OPENR1_RECONSTRUCTED_RTC_DEVICE_H
#define OPENR1_RECONSTRUCTED_RTC_DEVICE_H

/*
 * Provenance banner
 * -----------------
 * Family:         unknown_rtc_device_provider_candidate (Bravechip B210
 *                 "ChipletRing" platform `sys rtc` named-record layer).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (Ghidra bodies) and fresh Thumb disassembly of the three
 *                 Ghidra-missed bodies from the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  No upstream source, version, or license
 *                 exists for this family; reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Reduced stock functions (application image extents, end-exclusive):
 *
 *   0x00050DAA..<0x00050DB5  12   ops-table slot 7 veneer (-> op 0x20 tail)
 *   0x00050DB6..<0x00050DBF  10   ops-table slot 4 veneer (set-time forward)
 *   0x00050DE0..<0x00050DEB  12   shared registry-dispatch tail (op 0x20)
 *   0x00056274..<0x000562E0  108  8 Hz tick: epoch accumulation + alarm dispatch
 *   0x000562E0..<0x00056316  54   epoch -> 8-field calendar adapter (gmtime shim)
 *   0x00056318..<0x0005638E  118  named-record open + Nordic RTC start
 *   0x0005639C..<0x000563C0  36   epoch + subsecond snapshot
 *   0x000563F8..<0x00056440  72   named 44-byte calendar-record write
 *   0x00056444..<0x00056498  84   named callback binding
 *   0x0005649C..<0x00056502  102  named-record epoch/tick-divider initialize
 *
 * The 44-byte registration wrapper at 0x000563C4 and the 180-byte Nordic
 * nrfx_rtc_init body at 0x0007AD6C are NOT part of this family (R1
 * configuration adapter / Nordic SDK provider respectively).
 *
 * Correlation doc: docs/correlation/RTC-DEVICE-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Recovered family status scheme (positive codes shared with the interlocked
 * B210 platform families; see the boundary doc). */
enum {
    RTC_DEVICE_STATUS_OK = 0,
    RTC_DEVICE_STATUS_NAME_MISMATCH = 2,
    RTC_DEVICE_STATUS_BAD_ARGUMENT = 4,
    RTC_DEVICE_STATUS_LOOKUP_FAILED = 17
};

#define RTC_DEVICE_RECORD_COUNT 256u
#define RTC_DEVICE_CALENDAR_WORDS 11u /* 44-byte record: 8 used + 3 recovered padding */
#define RTC_DEVICE_TICKS_PER_SECOND 8u /* 32768 Hz / (4095 + 1) */

/* Recovered 44-byte calendar record.  The stock epoch->calendar adapter
 * fills the first eight words; the named calendar write copies all 44 bytes
 * verbatim.  The tick handler compares seconds/minutes against a record's
 * stored calendar and dispatches the bound callback with the current hour. */
typedef struct {
    uint32_t second;  /* +0x00 */
    uint32_t minute;  /* +0x04 */
    uint32_t hour;    /* +0x08 */
    uint32_t day;     /* +0x0C day of month */
    uint32_t month;   /* +0x10 1..12 */
    uint32_t year;    /* +0x14 full year (tm_year + 1900) */
    uint32_t weekday; /* +0x18 */
    uint32_t year_day;/* +0x1C 1..366 */
    uint32_t recovered_padding[3]; /* +0x20..+0x2B copied but never interpreted */
} rtc_device_calendar;

/* Recovered 0x40-byte request/response block shared by the set-time veneer,
 * the epoch initializer, and the snapshot path. */
typedef struct {
    rtc_device_calendar calendar;  /* +0x00 */
    uint32_t epoch_seconds;        /* +0x2C */
    int16_t utc_offset_minutes;    /* +0x30 */
    uint8_t reserved_32[6];        /* +0x32 */
    uint64_t millisecond_value;    /* +0x38 */
} rtc_device_time_block;

/* Alarm callback: invoked with the current local hour (uint8) when a record's
 * stored calendar second and minute match the freshly converted local time. */
typedef void (*rtc_device_alarm_callback)(uint8_t hour);

/* Recovered 88-byte named record (offsets verified against the stock image):
 *   +0x00 name pointer, +0x04 opened flag, +0x08 44-byte calendar,
 *   +0x34 embedded nrfx_rtc_t (8 bytes, opaque here), +0x3C callback,
 *   +0x40 embedded generic-registry record (24 bytes, owned by the still
 *   blocked registry family; kept as opaque storage). */
typedef struct {
    const char *name;                     /* +0x00 */
    uint8_t opened;                       /* +0x04 */
    uint8_t reserved_05[3];               /* +0x05 */
    rtc_device_calendar calendar;         /* +0x08 */
    uintptr_t rtc_instance[2];            /* +0x34 embedded nrfx_rtc_t */
    rtc_device_alarm_callback callback;   /* +0x3C */
    uintptr_t registry_record[6];         /* +0x40..+0x57 */
} rtc_device_record;

/* Recovered state root (stock: 0x2000737C; record table at +8, stock
 * 0x20007384). */
typedef struct {
    int16_t utc_offset_minutes; /* +0x00 signed UTC offset in minutes */
    uint16_t tick_divider;      /* +0x02 8 Hz divider, counts 0..7 */
    uint32_t epoch_seconds;     /* +0x04 epoch counter (offset not applied) */
    rtc_device_record records[RTC_DEVICE_RECORD_COUNT]; /* +0x08 */
} rtc_device_state;

/* Toolchain `struct tm` prefix mirror.  Stock delegates epoch breakdown to
 * the toolchain gmtime; the reconstruction keeps that dependency explicit
 * through the binding below. */
typedef struct {
    int32_t second;   /* tm_sec  */
    int32_t minute;   /* tm_min  */
    int32_t hour;     /* tm_hour */
    int32_t day;      /* tm_mday */
    int32_t month;    /* tm_mon  (0..11) */
    int32_t year;     /* tm_year (years since 1900) */
    int32_t weekday;  /* tm_wday */
    int32_t year_day; /* tm_yday (0..365) */
} rtc_device_broken_down;

/* Provider bindings.  Every dependency the stock code called directly
 * (toolchain gmtime, Nordic nrfx_rtc_*, app_error_handler, generic registry)
 * is an explicit, bindable seam; an unbound mandatory provider fails
 * explicitly instead of faulting. */
typedef bool (*rtc_device_breakdown_fn)(uint32_t epoch_seconds,
                                        rtc_device_broken_down *out);
typedef uint32_t (*rtc_device_nrfx_init_fn)(void *instance,
                                            uint16_t prescaler,
                                            uint8_t irq_priority);
typedef void (*rtc_device_nrfx_tick_enable_fn)(void *instance, bool enable);
typedef void (*rtc_device_nrfx_enable_fn)(void *instance);
typedef void (*rtc_device_fault_fn)(void);

/* Generic-registry seams (registry family still blocked).  `control`
 * reproduces dispatcher slot 0x20 (`FUN_00085D46`); `set_time` stands in for
 * the registry-family request-block path (`FUN_00050DF0` + dispatcher slot
 * 0x14) and receives the recovered (epoch, offset) pair. */
typedef uint32_t (*rtc_device_registry_control_fn)(void *device,
                                                   uint32_t operation,
                                                   void *argument);
typedef uint32_t (*rtc_device_registry_set_time_fn)(void *device,
                                                    uint32_t epoch_seconds,
                                                    int16_t utc_offset_minutes);

typedef struct {
    rtc_device_breakdown_fn breakdown; /* toolchain gmtime binding */
    rtc_device_nrfx_init_fn nrfx_init;
    rtc_device_nrfx_tick_enable_fn nrfx_tick_enable;
    rtc_device_nrfx_enable_fn nrfx_enable;
    rtc_device_fault_fn fault; /* app_error_handler binding; must not return on target */
} rtc_device_providers;

typedef struct {
    rtc_device_state state; /* exact recovered layout, at offset 0 */
    rtc_device_providers providers;
    void *registry_device; /* stock: cached `sys rtc` handle (0x20007690) */
    rtc_device_registry_control_fn registry_control;
    rtc_device_registry_set_time_fn registry_set_time;
} rtc_device;

/* Zeroes the state, installs the recovered fixed `sys rtc` record name at
 * slot 0 (stock: scatter-loaded data), and binds providers.  NULL providers
 * leave every provider-dependent path failing explicitly. */
void rtc_device_initialize(rtc_device *device,
                           const rtc_device_providers *providers);

/* 0x000562E0: epoch -> 8-field calendar adapter.  Converts through the bound
 * breakdown provider (toolchain gmtime in stock), then applies the recovered
 * field mapping: month +1, year +1900, year-day +1.  Returns
 * RTC_DEVICE_STATUS_OK or RTC_DEVICE_STATUS_BAD_ARGUMENT. */
uint32_t rtc_device_epoch_to_calendar(rtc_device *device, uint32_t epoch_seconds,
                                      rtc_device_calendar *out);

/* 0x00056318: named-record open.  Scans the record table for `*name`; on the
 * first open it initializes the embedded Nordic RTC instance with prescaler
 * 4095 and interrupt priority 6 (32768/4096 = 8 Hz), enables tick events,
 * starts the instance, and marks the record opened.  An already-open record
 * returns OK without re-initializing. */
uint32_t rtc_device_open(rtc_device *device, const char *const *name);

/* 0x00056274: one-second tick and calendar-callback dispatch.  Counts eight
 * RTC ticks per epoch second; on the eighth tick it advances the epoch,
 * converts local time (epoch plus signed UTC offset), walks the record
 * table, and invokes each record's bound callback with the current hour when
 * the record's stored calendar second and minute match. */
void rtc_device_tick(rtc_device *device);

/* 0x0005639C: epoch/subsecond snapshot.  Stores the raw epoch at +0x2C and
 * the 32-bit-wrapping millisecond value epoch*1000 + divider at +0x38. */
uint32_t rtc_device_snapshot(rtc_device *device, rtc_device_time_block *out);

/* 0x000563F8: named 44-byte calendar-record write (record slot 0). */
uint32_t rtc_device_calendar_write(rtc_device *device, const char *const *name,
                                   const rtc_device_calendar *calendar);

/* 0x00056444: named callback binding (record slot 0); NULL clears. */
uint32_t rtc_device_callback_bind(rtc_device *device, const char *const *name,
                                  rtc_device_alarm_callback callback);

/* 0x0005649C: named-record epoch/tick-divider initialization.  Applies the
 * signed UTC offset unconditionally (recovered order), then requires a name
 * match and an opened record before storing the epoch. */
uint32_t rtc_device_epoch_initialize(rtc_device *device, const char *const *name,
                                     const rtc_device_time_block *block);

/* Binds the generic-registry device handle and dispatch seams used by the
 * ops-table veneers (stock: `find("sys rtc")` cached at 0x20007690). */
void rtc_device_bind_registry(rtc_device *device, void *registry_device,
                              rtc_device_registry_control_fn control,
                              rtc_device_registry_set_time_fn set_time);

/* 0x00050DAA + 0x00050DE0: ops-table slot 7; forwards `argument` through
 * registry dispatcher slot 0x20 and returns 1 once forwarded.  Returns
 * RTC_DEVICE_STATUS_LOOKUP_FAILED when the registry seam is unbound (the
 * registry family is still blocked; stock returned 1 unconditionally). */
uint32_t rtc_device_ops_control(rtc_device *device, void *argument);

/* 0x00050DB6: ops-table slot 4; forwards the (epoch, UTC offset) pair through
 * the registry set-time path and returns 1 once forwarded.  Returns
 * RTC_DEVICE_STATUS_LOOKUP_FAILED when the registry seam is unbound. */
uint32_t rtc_device_ops_set_time(rtc_device *device, uint32_t epoch_seconds,
                                 int16_t utc_offset_minutes);

#endif
