/*
 * Host tests for the reconstructed time/calendar provider family
 * (unknown_time_calendar_provider_candidate; see
 * r1/reconstructed/time_calendar/ and
 * r1/docs/correlation/TIME-CALENDAR-REDUCTION-CORRELATION.md).
 *
 * Expected values are derived from the recovered stock semantics: 1970
 * epoch, unsigned forward conversion, the 1970-2029 validating inverse
 * converter, signed-minute UTC offsets, and the recovered cache/sync
 * behavior of the datetime fill and backend-update adapter.  The forward
 * converter is additionally cross-checked against the host C library
 * gmtime over a wide sweep.
 */

#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#include "time_calendar/time_calendar.h"

/* ------------------------------------------------------------------ */
/* Fake clock backend                                                  */
/* ------------------------------------------------------------------ */

typedef struct {
    uint32_t timestamp;       /* value returned by get */
    uint32_t get_calls;
    void *get_context_seen;
    uint32_t update_calls;
    uint32_t update_epoch_seen;
    int32_t update_offset_seen;
    void *update_context_seen;
    int32_t update_result;    /* value returned by update */
} fake_backend_trace;

/* The fake keeps its sample state module-internally (as a real clock
 * backend would); the bound context is recorded, not dereferenced.  This
 * matters because the recovered timestamp thunk passes a NULL context. */
static fake_backend_trace *active_trace;

static uint32_t fake_backend_get(void *context) {
    assert(active_trace != NULL);
    ++active_trace->get_calls;
    active_trace->get_context_seen = context;
    return active_trace->timestamp;
}

static int32_t fake_backend_update(uint32_t epoch_seconds,
                                   int32_t utc_offset_minutes,
                                   void *context) {
    assert(active_trace != NULL);
    ++active_trace->update_calls;
    active_trace->update_epoch_seen = epoch_seconds;
    active_trace->update_offset_seen = utc_offset_minutes;
    active_trace->update_context_seen = context;
    return active_trace->update_result;
}

static const time_calendar_backend_ops fake_backend_ops = {
    .reserved_00 = {0u, 0u},
    .get = fake_backend_get,
    .reserved_0c = 0u,
    .update = fake_backend_update,
};

static const time_calendar_backend_ops fake_backend_ops_no_update = {
    .reserved_00 = {0u, 0u},
    .get = fake_backend_get,
    .reserved_0c = 0u,
    .update = NULL,
};

static const time_calendar_backend_ops fake_backend_ops_no_get = {
    .reserved_00 = {0u, 0u},
    .get = NULL,
    .reserved_0c = 0u,
    .update = fake_backend_update,
};

static void fake_reset(time_calendar *clock, fake_backend_trace *trace) {
    time_calendar_initialize(clock);
    memset(trace, 0, sizeof(*trace));
    trace->update_result = 1;
    active_trace = trace;
}

/* ------------------------------------------------------------------ */
/* 0x0005A7BC: Unix seconds -> broken-down Gregorian time              */
/* ------------------------------------------------------------------ */

static void expect_broken_down(const time_calendar_broken_down *broken,
                               uint32_t second, uint32_t minute,
                               uint32_t hour, uint32_t day, uint32_t month,
                               uint32_t year, uint32_t weekday,
                               uint32_t year_day) {
    assert(broken->second == second);
    assert(broken->minute == minute);
    assert(broken->hour == hour);
    assert(broken->day == day);
    assert(broken->month == month);
    assert(broken->year == year);
    assert(broken->weekday == weekday);
    assert(broken->year_day == year_day);
    assert(broken->zero_tail == 0u);
}

static void test_time_calendar_unix_to_broken_down(void) {
    time_calendar_broken_down broken;

    /* Civil-time reference vectors (weekday: Sunday = 0, month/yday 0-based). */
    assert(time_calendar_unix_to_broken_down(0u, &broken) == &broken);
    expect_broken_down(&broken, 0u, 0u, 0u, 1u, 0u, 70u, 4u, 0u);
    /* 2000 is a leap year (divisible by 400): 2000-02-29 00:00:00 UTC. */
    assert(time_calendar_unix_to_broken_down(951782400u, &broken) == &broken);
    expect_broken_down(&broken, 0u, 0u, 0u, 29u, 1u, 100u, 2u, 59u);
    /* Recovered leap-year early break: day 365 of 2000 is 2000-12-31. */
    assert(time_calendar_unix_to_broken_down(978220800u, &broken) == &broken);
    expect_broken_down(&broken, 0u, 0u, 0u, 31u, 11u, 100u, 0u, 365u);
    /* 2016-02-29 23:59:59 UTC. */
    assert(time_calendar_unix_to_broken_down(1456790399u, &broken) == &broken);
    expect_broken_down(&broken, 59u, 59u, 23u, 29u, 1u, 116u, 1u, 59u);
    /* 2100 is not a leap year: 2100-02-28 23:59:59 UTC. */
    assert(time_calendar_unix_to_broken_down(4107542399u, &broken) == &broken);
    expect_broken_down(&broken, 59u, 59u, 23u, 28u, 1u, 200u, 0u, 58u);
    /* April has 30 days: 2023-04-30 23:59:59 UTC. */
    assert(time_calendar_unix_to_broken_down(1682899199u, &broken) == &broken);
    expect_broken_down(&broken, 59u, 59u, 23u, 30u, 3u, 123u, 0u, 119u);
    /* Year rollover: 2023-12-31 23:59:59 UTC. */
    assert(time_calendar_unix_to_broken_down(1704067199u, &broken) == &broken);
    expect_broken_down(&broken, 59u, 59u, 23u, 31u, 11u, 123u, 0u, 364u);
    /* uint32 wraparound frontier: 2106-02-07 06:28:15 UTC. */
    assert(time_calendar_unix_to_broken_down(4294967295u, &broken) == &broken);
    expect_broken_down(&broken, 15u, 28u, 6u, 7u, 1u, 206u, 0u, 37u);

    /* NULL output falls back to one shared static buffer (stock 0x20016AE4). */
    time_calendar_broken_down *fallback =
        time_calendar_unix_to_broken_down(951782400u, NULL);
    assert(fallback != NULL);
    expect_broken_down(fallback, 0u, 0u, 0u, 29u, 1u, 100u, 2u, 59u);
    assert(time_calendar_unix_to_broken_down(0u, NULL) == fallback);
    expect_broken_down(fallback, 0u, 0u, 0u, 1u, 0u, 70u, 4u, 0u);

    /* Cross-check the field mapping against host gmtime over a wide sweep. */
    for (uint32_t epoch = 0u; epoch < 4000000000u; epoch += 63115200u) {
        time_t when = (time_t)epoch;
        const struct tm *reference = gmtime(&when);
        assert(reference != NULL);
        assert(time_calendar_unix_to_broken_down(epoch, &broken) == &broken);
        expect_broken_down(&broken,
                           (uint32_t)reference->tm_sec,
                           (uint32_t)reference->tm_min,
                           (uint32_t)reference->tm_hour,
                           (uint32_t)reference->tm_mday,
                           (uint32_t)reference->tm_mon,
                           (uint32_t)reference->tm_year,
                           (uint32_t)reference->tm_wday,
                           (uint32_t)reference->tm_yday);
    }
}

/* ------------------------------------------------------------------ */
/* 0x0005A8AC: broken-down Gregorian time -> Unix seconds              */
/* ------------------------------------------------------------------ */

static time_calendar_broken_down make_broken_down(uint32_t second,
                                                  uint32_t minute,
                                                  uint32_t hour,
                                                  uint32_t day,
                                                  uint32_t month,
                                                  uint32_t year) {
    time_calendar_broken_down broken;
    broken.second = second;
    broken.minute = minute;
    broken.hour = hour;
    broken.day = day;
    broken.month = month;
    broken.year = year;
    broken.weekday = 0u;
    broken.year_day = 0u;
    broken.zero_tail = 0u;
    return broken;
}

static void test_time_calendar_broken_down_to_unix(void) {
    /* Epoch and frontier values. */
    assert(time_calendar_broken_down_to_unix(
               &(time_calendar_broken_down){
                   0u, 0u, 0u, 1u, 0u, 70u, 0u, 0u, 0u}) == 0);
    /* Recovered upper bound: tm_year 129 -> 2029-12-31 23:59:59. */
    assert(time_calendar_broken_down_to_unix(
               &(time_calendar_broken_down){
                   59u, 59u, 23u, 31u, 11u, 129u, 0u, 0u, 0u}) == 1893455999);
    /* Leap years inside the validated window: 2000-02-29 and 2028-02-29. */
    assert(time_calendar_broken_down_to_unix(
               &(time_calendar_broken_down){
                   0u, 0u, 0u, 29u, 1u, 100u, 0u, 0u, 0u}) == 951782400);
    assert(time_calendar_broken_down_to_unix(
               &(time_calendar_broken_down){
                   0u, 0u, 0u, 29u, 1u, 128u, 0u, 0u, 0u}) == 1835395200);

    /* Round-trip through the forward converter across a wide sweep. */
    for (uint32_t epoch = 0u; epoch < 1893456000u; epoch += 26438400u) {
        time_calendar_broken_down broken;
        assert(time_calendar_unix_to_broken_down(epoch, &broken) == &broken);
        assert(time_calendar_broken_down_to_unix(&broken) == (int32_t)epoch);
    }

    /* Recovered validation boundaries: every out-of-range field fails -1. */
    time_calendar_broken_down broken =
        make_broken_down(0u, 0u, 0u, 1u, 0u, 70u);
    assert(time_calendar_broken_down_to_unix(NULL) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken.year = 69u;
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken.year = 130u;
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken = make_broken_down(0u, 0u, 0u, 1u, 12u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken = make_broken_down(0u, 0u, 0u, 0u, 0u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken = make_broken_down(0u, 0u, 0u, 32u, 0u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken = make_broken_down(0u, 0u, 24u, 1u, 0u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken = make_broken_down(0u, 60u, 0u, 1u, 0u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);
    broken = make_broken_down(60u, 0u, 0u, 1u, 0u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) ==
           TIME_CALENDAR_CONVERSION_INVALID);

    /* Recovered laxity: the day is range-checked only (1..31), so
     * 1970-02-31 converts, rolling into March (day 61 of 1970). */
    broken = make_broken_down(0u, 0u, 0u, 31u, 1u, 70u);
    assert(time_calendar_broken_down_to_unix(&broken) == 61 * 86400);
}

/* ------------------------------------------------------------------ */
/* 0x0005A990 / binding seam                                           */
/* ------------------------------------------------------------------ */

static void test_time_calendar_backend_snapshot(void) {
    time_calendar clock;
    fake_backend_trace trace;
    fake_reset(&clock, &trace);

    const time_calendar_backend_ops *backend =
        (const time_calendar_backend_ops *)(uintptr_t)0xdeadbeefu;
    void *context = (void *)(uintptr_t)0xfeedfaceu;
    /* Unregistered: returns 0 and leaves both outputs untouched. */
    assert(time_calendar_backend_snapshot(&clock, &backend, &context) == 0u);
    assert((uintptr_t)backend == (uintptr_t)0xdeadbeefu);
    assert((uintptr_t)context == (uintptr_t)0xfeedfaceu);
    assert(time_calendar_backend_snapshot(NULL, &backend, &context) == 0u);

    time_calendar_bind_backend(&clock, &fake_backend_ops, &trace);
    assert(time_calendar_backend_snapshot(&clock, &backend, &context) == 1u);
    assert(backend == &fake_backend_ops);
    assert(context == (void *)&trace);
    /* Either output may be NULL (stock tolerates both). */
    assert(time_calendar_backend_snapshot(&clock, NULL, &context) == 1u);
    assert(time_calendar_backend_snapshot(&clock, &backend, NULL) == 1u);
    assert(time_calendar_backend_snapshot(&clock, NULL, NULL) == 1u);

    /* Unbinding restores the explicit failure. */
    time_calendar_bind_backend(&clock, NULL, NULL);
    assert(time_calendar_backend_snapshot(&clock, &backend, &context) == 0u);
}

/* ------------------------------------------------------------------ */
/* 0x0008AF40 / 0x0008AE58: packed-datetime adapters                   */
/* ------------------------------------------------------------------ */

static void expect_datetime(const time_calendar_datetime *datetime,
                            uint16_t year, uint8_t month, uint8_t day,
                            uint8_t hour, uint8_t minute, uint8_t second,
                            uint8_t weekday) {
    assert(datetime->year == year);
    assert(datetime->month == month);
    assert(datetime->day == day);
    assert(datetime->hour == hour);
    assert(datetime->minute == minute);
    assert(datetime->second == second);
    assert(datetime->weekday == weekday);
}

static void test_time_calendar_utc_to_calendar(void) {
    time_calendar_datetime datetime;

    assert(time_calendar_utc_to_calendar(0, 0, &datetime) == 1u);
    expect_datetime(&datetime, 1970u, 1u, 1u, 0u, 0u, 0u, 4u);
    /* Positive offset: +90 minutes. */
    assert(time_calendar_utc_to_calendar(0, 90, &datetime) == 1u);
    expect_datetime(&datetime, 1970u, 1u, 1u, 1u, 30u, 0u, 4u);
    /* Negative offsets wrap in 32 bits (recovered add.w arithmetic):
     * epoch 0 with -60 minutes converts as 0xFFFFFC18. */
    assert(time_calendar_utc_to_calendar(0, -60, &datetime) == 1u);
    expect_datetime(&datetime, 2106u, 2u, 7u, 5u, 28u, 16u, 0u);
    /* Known civil vector: 2023-11-14 22:13:20 UTC, Tuesday. */
    assert(time_calendar_utc_to_calendar(1700000000, 0, &datetime) == 1u);
    expect_datetime(&datetime, 2023u, 11u, 14u, 22u, 13u, 20u, 2u);
    /* Same instant at +120 minutes rolls into the next local day. */
    assert(time_calendar_utc_to_calendar(1700000000, 120, &datetime) == 1u);
    expect_datetime(&datetime, 2023u, 11u, 15u, 0u, 13u, 20u, 3u);
    /* Bad argument. */
    assert(time_calendar_utc_to_calendar(0, 0, NULL) == 0u);
}

static void test_time_calendar_to_utc(void) {
    const time_calendar_datetime epoch_datetime =
        {1970u, 1u, 1u, 0u, 0u, 0u, 4u};
    assert(time_calendar_to_utc(&epoch_datetime, 0) == 0);
    /* Offset is subtracted in minutes: local 01:30 at +90 is epoch 0. */
    const time_calendar_datetime offset_datetime =
        {1970u, 1u, 1u, 1u, 30u, 0u, 4u};
    assert(time_calendar_to_utc(&offset_datetime, 90) == 0);
    /* Known civil vector: 2000-02-29 12:00:00 UTC. */
    const time_calendar_datetime leap_datetime =
        {2000u, 2u, 29u, 12u, 0u, 0u, 2u};
    assert(time_calendar_to_utc(&leap_datetime, 0) == 951825600);
    assert(time_calendar_to_utc(&leap_datetime, 60) == 951825600 - 3600);

    /* Recovered failure mapping: invalid input converts to 0, not -1. */
    const time_calendar_datetime bad_month = {2000u, 13u, 1u, 0u, 0u, 0u, 0u};
    assert(time_calendar_to_utc(&bad_month, 0) == 0);
    const time_calendar_datetime zero_month = {2000u, 0u, 1u, 0u, 0u, 0u, 0u};
    assert(time_calendar_to_utc(&zero_month, 0) == 0);
    /* Year below 1900 wraps out of the validated 1970-2029 window. */
    const time_calendar_datetime old_year = {1899u, 12u, 31u, 0u, 0u, 0u, 0u};
    assert(time_calendar_to_utc(&old_year, 0) == 0);
    const time_calendar_datetime future_year =
        {2030u, 1u, 1u, 0u, 0u, 0u, 0u};
    assert(time_calendar_to_utc(&future_year, 0) == 0);
    assert(time_calendar_to_utc(NULL, 0) == 0);

    /* Round-trip against the UTC-to-calendar adapter inside the window. */
    for (uint32_t epoch = 0u; epoch < 1893456000u; epoch += 38880000u) {
        time_calendar_datetime datetime;
        assert(time_calendar_utc_to_calendar((int32_t)epoch, 0,
                                             &datetime) == 1u);
        assert(time_calendar_to_utc(&datetime, 0) == (int32_t)epoch);
    }
}

/* ------------------------------------------------------------------ */
/* 0x0005AC74 / 0x0005ACA6: local hour and ten-minute bucket           */
/* ------------------------------------------------------------------ */

static void test_time_calendar_local_hour_and_bucket(void) {
    time_calendar clock;
    fake_backend_trace trace;
    fake_reset(&clock, &trace);

    /* Zero offset. */
    assert(time_calendar_local_hour(&clock, 0u) == 0u);
    assert(time_calendar_activity_bucket(&clock, 0u) == 0u);
    /* 2023-11-14 22:13:20 UTC: hour 22, bucket 22*6 + 13/10 = 133. */
    assert(time_calendar_local_hour(&clock, 1700000000u) == 22u);
    assert(time_calendar_activity_bucket(&clock, 1700000000u) == 133u);
    /* Last bucket of the day: 23:59 -> 23*6 + 5 = 143. */
    assert(time_calendar_local_hour(&clock, 86399u) == 23u);
    assert(time_calendar_activity_bucket(&clock, 86399u) == 143u);
    /* Bucket boundary: 09:59 -> 59, 10:00 -> 60. */
    assert(time_calendar_activity_bucket(&clock, 35999u) == 59u);
    assert(time_calendar_activity_bucket(&clock, 36000u) == 60u);

    /* +60 minute offset. */
    clock.state.utc_offset_minutes = 60;
    assert(time_calendar_local_hour(&clock, 0u) == 1u);
    assert(time_calendar_activity_bucket(&clock, 0u) == 6u);
    /* -60 minute offset wraps the epoch (recovered 32-bit arithmetic):
     * local 0xFFFFFC18 = 2106-02-07 05:28:16 -> hour 5, bucket 32. */
    clock.state.utc_offset_minutes = -60;
    assert(time_calendar_local_hour(&clock, 0u) == 5u);
    assert(time_calendar_activity_bucket(&clock, 0u) == 32u);
    /* -300 minutes: 2023-11-14 17:13 local -> hour 17, bucket 103. */
    clock.state.utc_offset_minutes = -300;
    assert(time_calendar_local_hour(&clock, 1700000000u) == 17u);
    assert(time_calendar_activity_bucket(&clock, 1700000000u) == 103u);
}

/* ------------------------------------------------------------------ */
/* 0x0008ADA4 / 0x0008AD40 / 0x0008AD64 / 0x0008ADB4 / flag accessors  */
/* ------------------------------------------------------------------ */

static void test_time_calendar_backend_accessors(void) {
    time_calendar clock;
    fake_backend_trace trace;
    fake_reset(&clock, &trace);

    /* Unbound: every backend-dependent accessor fails explicitly with 0
     * (stock dereferences the unbound record and faults). */
    assert(time_calendar_backend_timestamp(&clock) == 0u);
    assert(time_calendar_local_timestamp(&clock) == 0);
    assert(time_calendar_local_day_start(&clock) == 0u);
    assert(time_calendar_backend_timestamp(NULL) == 0u);

    time_calendar_bind_backend(&clock, &fake_backend_ops, &trace);
    trace.timestamp = 1700000000u;

    /* Thunk: raw backend timestamp, called with a NULL context. */
    assert(time_calendar_backend_timestamp(&clock) == 1700000000u);
    assert(trace.get_calls == 1u);
    assert(trace.get_context_seen == NULL);

    /* Local timestamp: plus signed offset * 60. */
    assert(time_calendar_local_timestamp(&clock) == 1700000000);
    clock.state.utc_offset_minutes = 120;
    assert(time_calendar_local_timestamp(&clock) == 1700000000 + 7200);
    clock.state.utc_offset_minutes = -300;
    assert(time_calendar_local_timestamp(&clock) == 1700000000 - 18000);

    /* UTC-offset and status accessors. */
    assert(time_calendar_utc_offset(&clock) == -300);
    assert(time_calendar_utc_offset(NULL) == 0);
    assert(time_calendar_status(&clock) == 0u);
    time_calendar_set_time_update_flag(&clock);
    assert(time_calendar_status(&clock) == 1u);
    time_calendar_set_time_update_flag(NULL); /* tolerated no-op */
    clock.state.time_update_pending = 0u;

    /* Local-day start: signed 64-bit day division minus the offset. */
    clock.state.utc_offset_minutes = 0;
    assert(time_calendar_local_day_start(&clock) == 1699920000u);
    /* +120 minutes pushes the local time into the next day:
     * local 1700007200 -> day 19676 -> 1700006400 - 7200. */
    clock.state.utc_offset_minutes = 120;
    assert(time_calendar_local_day_start(&clock) == 1699999200u);
    /* -300 minutes: local 1699982000 -> day 19675 -> 1699920000 + 18000. */
    clock.state.utc_offset_minutes = -300;
    assert(time_calendar_local_day_start(&clock) == 1699938000u);
}

/* ------------------------------------------------------------------ */
/* 0x0008AD08: registered clock-backend calendar lookup                */
/* ------------------------------------------------------------------ */

static void test_time_calendar_backend_calendar_lookup(void) {
    time_calendar clock;
    fake_backend_trace trace;
    fake_reset(&clock, &trace);
    time_calendar_datetime datetime;

    /* Unregistered / bad argument. */
    assert(time_calendar_backend_calendar_lookup(&clock, &datetime) == 0u);
    assert(time_calendar_backend_calendar_lookup(NULL, &datetime) == 0u);

    time_calendar_bind_backend(&clock, &fake_backend_ops, &trace);
    assert(time_calendar_backend_calendar_lookup(&clock, NULL) == 0u);

    trace.timestamp = 1700000000u;
    assert(time_calendar_backend_calendar_lookup(&clock, &datetime) == 1u);
    expect_datetime(&datetime, 2023u, 11u, 14u, 22u, 13u, 20u, 2u);
    /* The snapshot path passes the bound context to the get operation. */
    assert(trace.get_context_seen == (void *)&trace);

    /* The offset is applied: +120 minutes rolls into the next local day. */
    clock.state.utc_offset_minutes = 120;
    assert(time_calendar_backend_calendar_lookup(&clock, &datetime) == 1u);
    expect_datetime(&datetime, 2023u, 11u, 15u, 0u, 13u, 20u, 3u);

    /* A backend without a get operation fails explicitly. */
    time_calendar_bind_backend(&clock, &fake_backend_ops_no_get, &trace);
    assert(time_calendar_backend_calendar_lookup(&clock, &datetime) == 0u);
}

/* ------------------------------------------------------------------ */
/* 0x0008AC28: cached packed local-datetime fill                       */
/* ------------------------------------------------------------------ */

static void test_time_calendar_local_datetime_fill(void) {
    time_calendar clock;
    fake_backend_trace trace;
    fake_reset(&clock, &trace);
    time_calendar_packed_datetime packed;

    /* Unregistered: the output is left untouched. */
    packed.date = 0xa5a5a5a5u;
    packed.time = 0x5a5a5a5au;
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(packed.date == 0xa5a5a5a5u && packed.time == 0x5a5a5a5au);
    time_calendar_local_datetime_fill(NULL, &packed);
    assert(packed.date == 0xa5a5a5a5u && packed.time == 0x5a5a5a5au);
    time_calendar_bind_backend(&clock, &fake_backend_ops, &trace);
    time_calendar_local_datetime_fill(&clock, NULL); /* tolerated no-op */

    /* 2023-11-14 22:13:20 UTC, Tuesday. */
    trace.timestamp = 1700000000u;
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(packed.date ==
           (2023u | (11u << 16) | (14u << 24)));
    assert(packed.time ==
           (22u | (13u << 8) | (20u << 16) | (2u << 24)));
    assert(clock.state.cache_valid == 1u);
    assert(clock.state.cached_day_start == 1699920000u);

    /* Same local day: the date cache holds, the time fields advance. */
    trace.timestamp = 1700000060u;
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(packed.date == (2023u | (11u << 16) | (14u << 24)));
    assert(packed.time == (22u | (14u << 8) | (20u << 16) | (2u << 24)));

    /* Next local day: the date cache is reconverted. */
    trace.timestamp = 1700010000u; /* 2023-11-15 01:00:00 UTC */
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(packed.date == (2023u | (11u << 16) | (15u << 24)));
    assert(packed.time == (1u | (0u << 8) | (0u << 16) | (3u << 24)));
    assert(clock.state.cached_day_start == 1700006400u);

    /* Recovered negative-local-epoch quirk: the date path uses the
     * 32-bit-wrapped local epoch (2106-02-07) while the time path divides
     * the signed 64-bit remainder as unsigned, yielding a wrapped hour. */
    fake_reset(&clock, &trace);
    time_calendar_bind_backend(&clock, &fake_backend_ops, &trace);
    clock.state.utc_offset_minutes = -60;
    trace.timestamp = 0u;
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(packed.date == (2106u | (2u << 16) | (7u << 24)));
    assert(packed.time == (85u | (28u << 8) | (16u << 16) | (0u << 24)));
}

/* ------------------------------------------------------------------ */
/* 0x0008AEB0: registered clock-backend update adapter                 */
/* ------------------------------------------------------------------ */

static void test_time_calendar_backend_update(void) {
    time_calendar clock;
    fake_backend_trace trace;
    fake_reset(&clock, &trace);
    time_calendar_packed_datetime packed;

    /* Unregistered and bad-argument paths return 0 without side effects. */
    assert(time_calendar_backend_update(&clock, 100u, 0) == 0);
    assert(time_calendar_backend_update(NULL, 100u, 0) == 0);

    /* Registered backend without an update operation returns 0. */
    time_calendar_bind_backend(&clock, &fake_backend_ops_no_update, &trace);
    assert(time_calendar_backend_update(&clock, 100u, 0) == 0);
    assert(trace.update_calls == 0u);

    /* Successful update: offset stored, cache invalidated, one-shot sync
     * state records the pre-update backend timestamp. */
    time_calendar_bind_backend(&clock, &fake_backend_ops, &trace);
    trace.timestamp = 1700000000u;
    trace.get_calls = 0u;
    trace.update_calls = 0u;
    trace.timestamp = 1699999000u; /* pre-update sample value */
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(clock.state.cache_valid == 1u);
    assert(time_calendar_backend_update(&clock, 1700001000u, 90) == 1);
    assert(trace.update_calls == 1u);
    assert(trace.update_epoch_seen == 1700001000u);
    assert(trace.update_offset_seen == 90);
    assert(trace.update_context_seen == (void *)&trace);
    assert(clock.state.utc_offset_minutes == 90);
    assert(clock.state.cache_valid == 0u);
    assert(clock.registration.sync_pending == 1u);
    assert(clock.registration.pre_update_timestamp == 1699999000u);

    /* One-shot: a second successful update does not re-sample or overwrite
     * the preserved timestamp. */
    const uint32_t get_calls_after_first = trace.get_calls;
    trace.timestamp = 1700005000u;
    assert(time_calendar_backend_update(&clock, 1700006000u, 90) == 1);
    assert(trace.get_calls == get_calls_after_first);
    assert(clock.registration.pre_update_timestamp == 1699999000u);
    assert(clock.registration.sync_pending == 1u);

    /* Failed update with a changed offset: the offset and the cache
     * invalidation still apply (recovered pre-call ordering), but the sync
     * state is untouched. */
    trace.update_result = 0;
    time_calendar_local_datetime_fill(&clock, &packed);
    assert(clock.state.cache_valid == 1u);
    assert(time_calendar_backend_update(&clock, 1700007000u, 120) == 0);
    assert(clock.state.utc_offset_minutes == 120);
    assert(clock.state.cache_valid == 0u);
    assert(clock.registration.pre_update_timestamp == 1699999000u);
    assert(clock.registration.sync_pending == 1u);

    /* Offset truncation: the stored offset is the low 16 bits, while the
     * backend receives the full 32-bit argument (recovered strh/operand). */
    trace.update_result = 1;
    assert(time_calendar_backend_update(&clock, 1700008000u, 65536 + 45) ==
           1);
    assert(trace.update_offset_seen == 65536 + 45);
    assert(clock.state.utc_offset_minutes == 45);

    /* Backend without a get operation: the preserved sample is 0 but the
     * one-shot state is still recorded on success. */
    fake_reset(&clock, &trace);
    time_calendar_bind_backend(&clock, &fake_backend_ops_no_get, &trace);
    assert(time_calendar_backend_update(&clock, 100u, 0) == 1);
    assert(clock.registration.sync_pending == 1u);
    assert(clock.registration.pre_update_timestamp == 0u);
}

/* ------------------------------------------------------------------ */

void test_reconstructed_time_calendar(void) {
    test_time_calendar_unix_to_broken_down();
    test_time_calendar_broken_down_to_unix();
    test_time_calendar_backend_snapshot();
    test_time_calendar_utc_to_calendar();
    test_time_calendar_to_utc();
    test_time_calendar_local_hour_and_bucket();
    test_time_calendar_backend_accessors();
    test_time_calendar_backend_calendar_lookup();
    test_time_calendar_local_datetime_fill();
    test_time_calendar_backend_update();
}
