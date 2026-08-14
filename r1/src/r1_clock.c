#include "openr1/r1_clock.h"

void r1_clock_initialize(r1_clock *clock, uint32_t tick_frequency_hz) {
    if (clock == NULL) {
        return;
    }
    clock->epoch_seconds = 0u;
    clock->utc_offset_minutes = 0;
    clock->reference_ticks = 0u;
    clock->tick_frequency_hz = tick_frequency_hz;
    clock->synchronized = false;
}

r1_error r1_clock_synchronize(r1_clock *clock, uint32_t epoch_seconds,
                              int16_t utc_offset_minutes,
                              uint32_t reference_ticks) {
    if (clock == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (utc_offset_minutes < R1_CLOCK_UTC_OFFSET_MINUTES_MIN ||
        utc_offset_minutes > R1_CLOCK_UTC_OFFSET_MINUTES_MAX) {
        return R1_ERROR_ARGUMENT;
    }
    clock->epoch_seconds = epoch_seconds;
    clock->utc_offset_minutes = utc_offset_minutes;
    clock->reference_ticks = reference_ticks;
    clock->synchronized = true;
    return R1_OK;
}

bool r1_clock_now(const r1_clock *clock, uint32_t now_ticks,
                  uint32_t *epoch_seconds) {
    if (clock == NULL || epoch_seconds == NULL || !clock->synchronized ||
        clock->tick_frequency_hz == 0u) {
        return false;
    }
    const uint32_t elapsed_ticks = now_ticks - clock->reference_ticks;
    const uint32_t elapsed_seconds = elapsed_ticks / clock->tick_frequency_hz;
    uint32_t epoch = clock->epoch_seconds;
    if (UINT32_MAX - epoch < elapsed_seconds) {
        epoch = UINT32_MAX;
    } else {
        epoch += elapsed_seconds;
    }
    *epoch_seconds = epoch;
    return true;
}

bool r1_clock_local_now(const r1_clock *clock, uint32_t now_ticks,
                        uint32_t *local_seconds) {
    if (local_seconds == NULL) {
        return false;
    }
    uint32_t epoch = 0u;
    if (!r1_clock_now(clock, now_ticks, &epoch)) {
        return false;
    }
    const int64_t local = (int64_t)epoch +
        (int64_t)clock->utc_offset_minutes * INT64_C(60);
    *local_seconds = local <= 0 ? 0u : (uint32_t)local;
    return true;
}
