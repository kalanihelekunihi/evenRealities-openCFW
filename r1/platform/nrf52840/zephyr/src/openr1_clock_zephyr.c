#include "openr1_clock_zephyr.h"

#include <errno.h>
#include <stdint.h>
#include <time.h>

#include <zephyr/kernel.h>

#include "openr1/r1_clock.h"
#include "openr1/r1_runtime.h"
#include "openr1_databases_zephyr.h"
#include "time_calendar/time_calendar.h"

#define OPENR1_CLOCK_CADENCE_TICKS 1024u
/* The hour transition is delivered in this thread and may synchronously run
 * the exact 128-byte record builder plus FlashDB append. Keep enough stack for
 * that admitted path instead of retaining the query-only worker allocation. */
#define OPENR1_CLOCK_STACK_BYTES 1536u

typedef struct {
    bool (*epoch)(uint32_t *);
    bool (*utc_offset)(int16_t *);
    bool (*local_tm)(struct tm *);
} openr1_clock_zephyr_api;

static r1_clock platform_clock;
static r1_runtime *platform_runtime;
static struct k_thread clock_thread;
K_THREAD_STACK_DEFINE(clock_stack, OPENR1_CLOCK_STACK_BYTES);
K_MUTEX_DEFINE(clock_mutex);
static uint32_t adopted_epoch;
static int16_t adopted_offset_minutes;
static bool adoption_valid;
static bool clock_ready;
static bool local_hour_known;
static uint8_t last_local_hour;

static uint32_t current_ticks(void) {
    return (uint32_t)k_uptime_ticks();
}

bool openr1_clock_zephyr_adopt_phone_time(uint32_t epoch_seconds,
                                          int16_t utc_offset_minutes) {
    if (!clock_ready || k_is_in_isr() ||
        k_mutex_lock(&clock_mutex, K_FOREVER) != 0) {
        return false;
    }
    bool adopted = false;
    if (r1_clock_synchronize(&platform_clock, epoch_seconds,
                             utc_offset_minutes, current_ticks()) == R1_OK) {
        adopted_epoch = epoch_seconds;
        adopted_offset_minutes = utc_offset_minutes;
        adoption_valid = true;
        adopted = true;
    }
    (void)k_mutex_unlock(&clock_mutex);
    return adopted;
}

static void clock_worker(void *first, void *second, void *third) {
    (void)first;
    (void)second;
    (void)third;
    for (;;) {
        const uint32_t state_epoch = platform_runtime->device.unix_seconds;
        const int16_t state_offset =
            (int16_t)platform_runtime->device.timezone_minutes_raw;
        bool changed = false;
        if (state_epoch != 0u &&
            k_mutex_lock(&clock_mutex, K_FOREVER) == 0) {
            changed = !adoption_valid || state_epoch != adopted_epoch ||
                state_offset != adopted_offset_minutes;
            (void)k_mutex_unlock(&clock_mutex);
        }
        if (changed) {
            uint32_t old_epoch = 0u;
            int16_t old_offset = 0;
            const bool old_clock_available =
                openr1_clock_zephyr_epoch(&old_epoch) &&
                openr1_clock_zephyr_utc_offset(&old_offset);
            const r1_health_time_transition transition = {
                .old_utc_offset_minutes =
                    old_clock_available ? old_offset : 0,
                .new_utc_offset_minutes = state_offset,
                .old_timestamp_seconds = old_clock_available ? old_epoch : 0u,
                .new_timestamp_seconds = state_epoch,
            };
            r1_health_time_transition_result plan;
            if (openr1_clock_zephyr_adopt_phone_time(
                    state_epoch, state_offset) &&
                r1_health_plan_time_transition(&transition, &plan) == R1_OK &&
                plan.subscriber_broadcast_requested) {
                (void)openr1_databases_zephyr_multicast_time_transition(
                    &transition);
                /* A material correction establishes a new hour baseline; it
                 * is not itself an elapsed local-hour boundary. */
                local_hour_known = false;
            }
        }
        struct tm local;
        if (openr1_clock_zephyr_local_tm(&local) &&
            local.tm_hour >= 0 && local.tm_hour < 24) {
            const uint8_t current_local_hour = (uint8_t)local.tm_hour;
            if (local_hour_known && current_local_hour != last_local_hour) {
                (void)openr1_databases_zephyr_multicast_hour(
                    current_local_hour);
            }
            last_local_hour = current_local_hour;
            local_hour_known = true;
        }
        k_sleep(K_TICKS(OPENR1_CLOCK_CADENCE_TICKS));
    }
}

int openr1_clock_zephyr_initialize(r1_runtime *runtime) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    if (clock_ready) {
        return -EALREADY;
    }
    r1_clock_initialize(&platform_clock, CONFIG_SYS_CLOCK_TICKS_PER_SEC);
    platform_runtime = runtime;
    adopted_epoch = 0u;
    adopted_offset_minutes = 0;
    adoption_valid = false;
    local_hour_known = false;
    last_local_hour = 0u;
    clock_ready = true;
    (void)k_thread_create(
        &clock_thread, clock_stack, K_THREAD_STACK_SIZEOF(clock_stack),
        clock_worker, NULL, NULL, NULL, K_LOWEST_APPLICATION_THREAD_PRIO,
        0, K_NO_WAIT);
    (void)k_thread_name_set(&clock_thread, "openr1-clock");
    return 0;
}

bool openr1_clock_zephyr_epoch(uint32_t *epoch_seconds) {
    if (!clock_ready || epoch_seconds == NULL || k_is_in_isr() ||
        k_mutex_lock(&clock_mutex, K_FOREVER) != 0) {
        return false;
    }
    const bool available = r1_clock_now(
        &platform_clock, current_ticks(), epoch_seconds);
    (void)k_mutex_unlock(&clock_mutex);
    return available;
}

bool openr1_clock_zephyr_utc_offset(int16_t *utc_offset_minutes) {
    if (!clock_ready || utc_offset_minutes == NULL || k_is_in_isr() ||
        k_mutex_lock(&clock_mutex, K_FOREVER) != 0) {
        return false;
    }
    uint32_t epoch = 0u;
    const bool available = r1_clock_now(
        &platform_clock, current_ticks(), &epoch);
    if (available) {
        *utc_offset_minutes = platform_clock.utc_offset_minutes;
    }
    (void)k_mutex_unlock(&clock_mutex);
    return available;
}

bool openr1_clock_zephyr_local_tm(struct tm *out) {
    if (!clock_ready || out == NULL || k_is_in_isr() ||
        k_mutex_lock(&clock_mutex, K_FOREVER) != 0) {
        return false;
    }
    uint32_t local_seconds = 0u;
    const bool available = r1_clock_local_now(
        &platform_clock, current_ticks(), &local_seconds);
    bool converted = false;
    if (available) {
        time_calendar_broken_down broken;
        if (time_calendar_unix_to_broken_down(
                local_seconds, &broken) == &broken) {
            *out = (struct tm){
                .tm_sec = (int)broken.second,
                .tm_min = (int)broken.minute,
                .tm_hour = (int)broken.hour,
                .tm_mday = (int)broken.day,
                .tm_mon = (int)broken.month,
                .tm_year = (int)broken.year,
                .tm_wday = (int)broken.weekday,
                .tm_yday = (int)broken.year_day,
                .tm_isdst = 0,
            };
            converted = true;
        }
    }
    (void)k_mutex_unlock(&clock_mutex);
    return available && converted;
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_clock_zephyr_api clock_zephyr_api = {
    openr1_clock_zephyr_epoch,
    openr1_clock_zephyr_utc_offset,
    openr1_clock_zephyr_local_tm,
};
