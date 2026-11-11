/* Stock 0x41438: merge a stored HRV hour into the day builder. */
#include <stdint.h>

#include "native_health_offline_consume.h"
#include "native_health_packet_flush.h"
#include "integer_eabi.h"
#include "../board/native_battery_memory.h"
#include "time_calendar/time_calendar.h"
#include <flashdb.h>

extern uint32_t r1_time_backend_timestamp(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(
    uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_2(
    uint32_t, const char *, uint32_t, uint32_t);

static const char future_ring[] =
    "[RING]hrv_sync skip future flash record:%u now:%u";
static const char future_sdk[] =
    "hrv_sync skip future flash record:%u now:%u";

static void note_future(uint32_t timestamp, uint32_t now)
{
    if ((r1_structured_log_mode_get() & 1u) ||
            (r1_structured_log_mode_get() & 4u)) {
        (void)r1_structured_log_format(
            0x08800000u, future_ring, future_ring, timestamp, now);
    }
    if (r1_structured_log_mode_get() & 2u) {
        nrf_log_frontend_std_2(
            0x001c0002u, future_sdk, timestamp, now);
    }
}

uint32_t r1_health_sync_provider_00041438(fdb_tsl_t tsl, void *argument)
{
    const volatile uint8_t *const descriptor = argument;
    volatile uint8_t *const record =
        (volatile uint8_t *)(uintptr_t)read32(descriptor + 4u);
    struct fdb_blob blob;
    fdb_blob_t view = fdb_blob_make(&blob, (void *)record, 128u);
    view = fdb_tsl_to_blob(tsl, view);
    if (fdb_blob_read(
            (fdb_db_t)(uintptr_t)read32(descriptor), view) != 128u) {
        return 1u;
    }

    const uint32_t timestamp = read32(record + 4u);
    const uint32_t now = r1_time_backend_timestamp();
    if (timestamp > now) {
        note_future(timestamp, now);
        return 0u;
    }

    time_calendar_datetime calendar = {0};
    const int32_t offset_seconds = (int32_t)(int16_t)read16(record) * 60;
    (void)time_calendar_utc_to_calendar(
        (int32_t)timestamp, (int16_t)read16(record), &calendar);
    const uint32_t seconds_since_midnight =
        (uint32_t)calendar.hour * 3600u +
        (uint32_t)calendar.minute * 60u + calendar.second;
    uint32_t day = timestamp - seconds_since_midnight;
    if (calendar.hour == 0u) {
        day -= 86400u;
    }

    if (read32(descriptor + 16u) != 0u) {
        const uint64_t shifted = (uint64_t)now + (int64_t)offset_seconds;
        uint64_t remainder;
        (void)r1_runtime_udivmod(shifted, 86400u, &remainder);
        const uint32_t today =
            (uint32_t)(shifted - remainder - offset_seconds);
        if (day >= today) {
            return 0u;
        }
    }

    const volatile uint8_t *const sample =
        record + read16(descriptor + 12u);
    if (read16(sample) == 0u) {
        return 0u;
    }

    volatile uint8_t *const builder =
        (volatile uint8_t *)(uintptr_t)read32(descriptor + 8u);
    const uint32_t slot = calendar.hour == 0u
        ? 23u : (uint32_t)calendar.hour - 1u;
    const uint32_t needs_reset = builder[192u] == 0u ||
        read32(builder + 196u) != day ||
        read16(builder + 200u) != read16(record);
    if (builder[192u] != 0u && needs_reset) {
        r1_hrv_sync_flush(builder);
    }
    if (needs_reset) {
        r1_hrv_sync_builder_reset(builder);
        write32(builder + 196u, day);
        write16(builder + 200u, read16(record));
    }
    if (builder[slot] == 0u) {
        builder[slot] = 1u;
        volatile uint8_t *const row = builder + 24u + slot * 7u;
        row[0] = (uint8_t)slot;
        write16(row + 1u, read16(sample));
        write16(row + 3u, read16(sample + 2u));
        write16(row + 5u, read16(sample + 4u));
        builder[192u] = (uint8_t)(builder[192u] + 1u);
    }
    if (read32(builder + 204u) < timestamp) {
        write32(builder + 204u, timestamp);
    }
    return 0u;
}
