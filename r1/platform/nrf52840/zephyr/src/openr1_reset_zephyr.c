#include "openr1_reset_zephyr.h"

#include <hal/nrf_power.h>
#include <zephyr/fatal.h>
#include <zephyr/linker/section_tags.h>

typedef struct {
    void (*initialize)(void);
    bool (*latest)(r1_reset_reason_report *);
    r1_reset_trace_record *(*retained_record)(void);
    void (*capture)(uint8_t, uint8_t, uint32_t, uint32_t);
    void (*fault_and_reset)(uint32_t, uint32_t);
} openr1_reset_zephyr_api;

static r1_reset_trace_record retained_reset_trace __noinit;
static r1_reset_reason_report latest_report;
static bool latest_report_available;

r1_reset_trace_record *openr1_reset_zephyr_retained_record(void) {
    r1_reset_trace_initialize(&retained_reset_trace);
    return &retained_reset_trace;
}

void openr1_reset_zephyr_capture(uint8_t persist_tag, uint8_t reboot_caller,
                                 uint32_t program_counter,
                                 uint32_t return_address) {
    r1_reset_trace_record *record = openr1_reset_zephyr_retained_record();
    r1_reset_trace_set_persist_tag(record, persist_tag);
    r1_reset_trace_set_reboot_caller(record, reboot_caller);
    r1_reset_trace_capture_site(record, program_counter, return_address);
}

__attribute__((noreturn))
void openr1_reset_zephyr_fault_and_reset(uint32_t program_counter,
                                         uint32_t return_address) {
    r1_reset_trace_record *record = openr1_reset_zephyr_retained_record();
    r1_reset_trace_set_persist_tag(record, R1_RESET_TRACE_FAULT_TAG);
    r1_reset_trace_capture_site(record, program_counter, return_address);
    NVIC_SystemReset();
    __builtin_unreachable();
}

void openr1_reset_zephyr_initialize(void) {
    const uint32_t raw = nrf_power_resetreas_get(NRF_POWER);
    latest_report_available = r1_reset_reason_decode(
        raw, openr1_reset_zephyr_retained_record(), &latest_report);
    nrf_power_resetreas_clear(NRF_POWER, raw);
}

bool openr1_reset_zephyr_latest(r1_reset_reason_report *report) {
    if (!latest_report_available || report == NULL) {
        return false;
    }
    *report = latest_report;
    return true;
}

void k_sys_fatal_error_handler(unsigned int reason,
                               const struct arch_esf *esf) {
    const uint32_t program_counter = esf != NULL ? esf->basic.pc : 0u;
    const uint32_t return_address = esf != NULL ? esf->basic.lr : 0u;
    const uint8_t reboot_caller =
        reason <= UINT8_MAX ? (uint8_t)reason : UINT8_MAX;
    openr1_reset_zephyr_capture(
        R1_RESET_TRACE_FAULT_TAG, reboot_caller,
        program_counter, return_address);
    openr1_reset_zephyr_fault_and_reset(program_counter, return_address);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_reset_zephyr_api reset_zephyr_api = {
    openr1_reset_zephyr_initialize,
    openr1_reset_zephyr_latest,
    openr1_reset_zephyr_retained_record,
    openr1_reset_zephyr_capture,
    openr1_reset_zephyr_fault_and_reset,
};
