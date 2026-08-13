#include "openr1_reset_reason.h"

#include "nrf_power.h"

#include "openr1_reset_trace_port.h"

static r1_reset_reason_report latest_report;
static bool latest_report_available;

void openr1_reset_reason_initialize(void) {
    const uint32_t raw = nrf_power_resetreas_get();
    latest_report_available = r1_reset_reason_decode(
        raw, openr1_reset_trace_retained_record(), &latest_report);
    nrf_power_resetreas_clear(raw);
}

bool openr1_reset_reason_latest(r1_reset_reason_report *report) {
    if (!latest_report_available || report == NULL) {
        return false;
    }
    *report = latest_report;
    return true;
}

typedef struct {
    void (*initialize)(void);
    bool (*latest)(r1_reset_reason_report *);
} openr1_reset_reason_api;

__attribute__((used, section(".openr1_reset_reason_api")))
static const openr1_reset_reason_api reset_reason_api = {
    openr1_reset_reason_initialize,
    openr1_reset_reason_latest,
};
