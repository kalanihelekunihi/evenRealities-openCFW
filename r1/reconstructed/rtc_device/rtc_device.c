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
 *                 Bravechip source.  Reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Per-function mapping (stock extent, end-exclusive / size -> symbol here):
 *
 *   0x00050DAA..<0x00050DB5  12  -> rtc_device_ops_control (slot 7 veneer)
 *   0x00050DB6..<0x00050DBF  10  -> rtc_device_ops_set_time (slot 4 veneer)
 *   0x00050DE0..<0x00050DEB  12  -> rtc_device_ops_control tail (op 0x20)
 *   0x00056274..<0x000562E0  108 -> rtc_device_tick
 *   0x000562E0..<0x00056316  54  -> rtc_device_epoch_to_calendar
 *   0x00056318..<0x0005638E  118 -> rtc_device_open
 *   0x0005639C..<0x000563C0  36  -> rtc_device_snapshot
 *   0x000563F8..<0x00056440  72  -> rtc_device_calendar_write
 *   0x00056444..<0x00056498  84  -> rtc_device_callback_bind
 *   0x0005649C..<0x00056502  102 -> rtc_device_epoch_initialize
 *
 * Observable behavior is preserved; restructuring is limited to explicit
 * provider bindings (toolchain gmtime, Nordic nrfx_rtc_*, app_error_handler,
 * generic registry), pointer/argument validation, and a full (NULL-guarded)
 * record scan.  Every divergence is listed in
 * docs/correlation/RTC-DEVICE-REDUCTION-CORRELATION.md.
 */

#include "rtc_device/rtc_device.h"

/* The recovered field offsets are a property of the 32-bit target ABI; on
 * wider host pointer ABIs the C layout legitimately differs, so the exact
 * layout asserts apply to the target ABI only. */
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(rtc_device_calendar) == 44u, "recovered calendar is 44 bytes");
_Static_assert(offsetof(rtc_device_record, opened) == 0x04u, "record +0x04");
_Static_assert(offsetof(rtc_device_record, calendar) == 0x08u, "record +0x08");
_Static_assert(offsetof(rtc_device_record, rtc_instance) == 0x34u, "record +0x34");
_Static_assert(offsetof(rtc_device_record, callback) == 0x3Cu, "record +0x3C");
_Static_assert(offsetof(rtc_device_record, registry_record) == 0x40u, "record +0x40");
_Static_assert(sizeof(rtc_device_record) == 88u, "recovered record is 88 bytes");
_Static_assert(offsetof(rtc_device_state, tick_divider) == 0x02u, "state +0x02");
_Static_assert(offsetof(rtc_device_state, epoch_seconds) == 0x04u, "state +0x04");
_Static_assert(offsetof(rtc_device_state, records) == 0x08u, "state +0x08");
#endif
_Static_assert(offsetof(rtc_device_time_block, epoch_seconds) == 0x2Cu, "block +0x2C");
_Static_assert(offsetof(rtc_device_time_block, utc_offset_minutes) == 0x30u, "block +0x30");
_Static_assert(offsetof(rtc_device_time_block, millisecond_value) == 0x38u, "block +0x38");
_Static_assert(sizeof(rtc_device_time_block) == 0x40u, "recovered block is 64 bytes");

/* Recovered fixed device name (stock: scatter-loaded record data, leaked
 * string "sys rtc"; registration itself is R1 configuration, family
 * r1_device_registry_configuration_adapter). */
#define RTC_DEVICE_FIXED_NAME "sys rtc"

/* Stock ops-table veneers return 1 once the registry dispatch ran. */
#define RTC_DEVICE_OPS_FORWARDED UINT32_C(1)

/* Recovered Nordic RTC configuration: prescaler 4095 (32768/4096 = 8 Hz),
 * interrupt priority 6 (const 8-byte config at stock 0x0009A638 with the
 * prescaler overridden to 0xFFF). */
#define RTC_DEVICE_PRESCALER UINT16_C(4095)
#define RTC_DEVICE_IRQ_PRIORITY UINT8_C(6)

/* Local strcmp; the freestanding build does not use libc string.h. */
static bool text_equal(const char *left, const char *right) {
    while (*left != '\0' && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

void rtc_device_initialize(rtc_device *device,
                           const rtc_device_providers *providers) {
    if (device == NULL) {
        return;
    }
    uint8_t *bytes = (uint8_t *)device;
    for (size_t index = 0; index < sizeof(*device); ++index) {
        bytes[index] = 0u;
    }
    if (providers != NULL) {
        device->providers.breakdown = providers->breakdown;
        device->providers.nrfx_init = providers->nrfx_init;
        device->providers.nrfx_tick_enable = providers->nrfx_tick_enable;
        device->providers.nrfx_enable = providers->nrfx_enable;
        device->providers.fault = providers->fault;
    }
    device->state.records[0].name = RTC_DEVICE_FIXED_NAME;
}

uint32_t rtc_device_epoch_to_calendar(rtc_device *device, uint32_t epoch_seconds,
                                      rtc_device_calendar *out) {
    if (device == NULL || out == NULL ||
            device->providers.breakdown == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    rtc_device_broken_down broken_down;
    if (!device->providers.breakdown(epoch_seconds, &broken_down)) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    /* Recovered field mapping (0x000562E0): month +1, year +1900, year-day +1. */
    out->second = (uint32_t)broken_down.second;
    out->minute = (uint32_t)broken_down.minute;
    out->hour = (uint32_t)broken_down.hour;
    out->day = (uint32_t)broken_down.day;
    out->month = (uint32_t)(broken_down.month + 1);
    out->year = (uint32_t)(broken_down.year + 1900);
    out->weekday = (uint32_t)broken_down.weekday;
    out->year_day = (uint32_t)(broken_down.year_day + 1);
    out->recovered_padding[0] = 0u;
    out->recovered_padding[1] = 0u;
    out->recovered_padding[2] = 0u;
    return RTC_DEVICE_STATUS_OK;
}

uint32_t rtc_device_open(rtc_device *device, const char *const *name) {
    if (device == NULL || name == NULL || *name == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    size_t index = 0u;
    bool found = false;
    for (index = 0u; index < RTC_DEVICE_RECORD_COUNT; ++index) {
        const char *record_name = device->state.records[index].name;
        if (record_name != NULL && text_equal(record_name, *name)) {
            found = true;
            break;
        }
    }
    if (!found) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    rtc_device_record *record = &device->state.records[index];
    if (record->opened != 0u) {
        return RTC_DEVICE_STATUS_OK;
    }
    const rtc_device_providers *providers = &device->providers;
    if (providers->nrfx_init == NULL || providers->nrfx_tick_enable == NULL ||
            providers->nrfx_enable == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    void *instance = (void *)record->rtc_instance;
    uint32_t init_status = providers->nrfx_init(instance, RTC_DEVICE_PRESCALER,
                                                RTC_DEVICE_IRQ_PRIORITY);
    if (init_status != RTC_DEVICE_STATUS_OK && providers->fault != NULL) {
        /* Stock calls app_error_handler here and continues; on target the
         * fault handler does not return. */
        providers->fault();
    }
    providers->nrfx_tick_enable(instance, true);
    providers->nrfx_enable(instance);
    record->opened = 1u;
    return RTC_DEVICE_STATUS_OK;
}

void rtc_device_tick(rtc_device *device) {
    if (device == NULL) {
        return;
    }
    rtc_device_state *state = &device->state;
    if (state->tick_divider < (uint16_t)(RTC_DEVICE_TICKS_PER_SECOND - 1u)) {
        state->tick_divider = (uint16_t)(state->tick_divider + 1u);
        return;
    }
    state->epoch_seconds += 1u;
    /* Recovered: local = epoch + (signed offset in minutes) * 60, with
     * 32-bit wrap arithmetic (rsb/add.w shift pair in stock). */
    int32_t offset_seconds = (int32_t)state->utc_offset_minutes * 60;
    uint32_t local_epoch = state->epoch_seconds + (uint32_t)offset_seconds;
    rtc_device_calendar calendar;
    if (rtc_device_epoch_to_calendar(device, local_epoch, &calendar) !=
            RTC_DEVICE_STATUS_OK) {
        /* Unbound breakdown provider: stock always linked gmtime.  The epoch
         * advance above is stock behavior; dispatch is skipped explicitly. */
        state->tick_divider = 0u;
        return;
    }
    for (size_t index = 0u; index < RTC_DEVICE_RECORD_COUNT; ++index) {
        rtc_device_record *record = &state->records[index];
        if (record->calendar.minute == calendar.minute &&
                record->calendar.second == calendar.second &&
                record->callback != NULL) {
            record->callback((uint8_t)calendar.hour);
        }
    }
    state->tick_divider = 0u;
}

uint32_t rtc_device_snapshot(rtc_device *device, rtc_device_time_block *out) {
    if (device == NULL || out == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    const rtc_device_state *state = &device->state;
    out->epoch_seconds = state->epoch_seconds;
    /* Recovered 32-bit computation (epoch*1000 + divider) widened into the
     * 64-bit store; the wrap at 2^32 is stock behavior. */
    uint32_t millisecond_value =
        state->epoch_seconds * UINT32_C(1000) + (uint32_t)state->tick_divider;
    out->millisecond_value = (uint64_t)millisecond_value;
    return RTC_DEVICE_STATUS_OK;
}

uint32_t rtc_device_calendar_write(rtc_device *device, const char *const *name,
                                   const rtc_device_calendar *calendar) {
    if (device == NULL || name == NULL || *name == NULL || calendar == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    rtc_device_record *record = &device->state.records[0];
    if (record->name == NULL || !text_equal(record->name, *name)) {
        return RTC_DEVICE_STATUS_NAME_MISMATCH;
    }
    /* Recovered verbatim 44-byte copy (stock: memmove of 0x2C bytes). */
    for (size_t index = 0u; index < RTC_DEVICE_CALENDAR_WORDS; ++index) {
        ((uint32_t *)&record->calendar)[index] =
            ((const uint32_t *)calendar)[index];
    }
    return RTC_DEVICE_STATUS_OK;
}

uint32_t rtc_device_callback_bind(rtc_device *device, const char *const *name,
                                  rtc_device_alarm_callback callback) {
    if (device == NULL || name == NULL || *name == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    rtc_device_record *record = &device->state.records[0];
    if (record->name == NULL || !text_equal(record->name, *name)) {
        return RTC_DEVICE_STATUS_NAME_MISMATCH;
    }
    record->callback = callback;
    return RTC_DEVICE_STATUS_OK;
}

uint32_t rtc_device_epoch_initialize(rtc_device *device, const char *const *name,
                                     const rtc_device_time_block *block) {
    if (device == NULL || name == NULL || *name == NULL || block == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    /* Recovered order: the signed UTC offset is applied before the name and
     * opened-state checks, so it lands even on the failure paths. */
    device->state.utc_offset_minutes = block->utc_offset_minutes;
    rtc_device_record *record = &device->state.records[0];
    if (record->name == NULL || !text_equal(record->name, *name) ||
            record->opened == 0u) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    device->state.epoch_seconds = block->epoch_seconds;
    /* Recovered validation conversion (stock: gmtime into a discarded stack
     * record); side-effect free, result intentionally unused. */
    rtc_device_calendar discarded;
    (void)rtc_device_epoch_to_calendar(device, block->epoch_seconds, &discarded);
    return RTC_DEVICE_STATUS_OK;
}

void rtc_device_bind_registry(rtc_device *device, void *registry_device,
                              rtc_device_registry_control_fn control,
                              rtc_device_registry_set_time_fn set_time) {
    if (device == NULL) {
        return;
    }
    device->registry_device = registry_device;
    device->registry_control = control;
    device->registry_set_time = set_time;
}

uint32_t rtc_device_ops_control(rtc_device *device, void *argument) {
    if (device == NULL || device->registry_control == NULL) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    /* Shared tail 0x00050DE0: dispatcher(device, 0, argument), slot 0x20. */
    (void)device->registry_control(device->registry_device, 0u, argument);
    return RTC_DEVICE_OPS_FORWARDED;
}

uint32_t rtc_device_ops_set_time(rtc_device *device, uint32_t epoch_seconds,
                                 int16_t utc_offset_minutes) {
    if (device == NULL || device->registry_set_time == NULL) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    (void)device->registry_set_time(device->registry_device, epoch_seconds,
                                    utc_offset_minutes);
    return RTC_DEVICE_OPS_FORWARDED;
}
