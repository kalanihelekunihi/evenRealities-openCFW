#include "openr1/r1_reset_reason.h"

static void clear_report(r1_reset_reason_report *report) {
    report->raw = 0u;
    report->recognized = 0u;
    report->power_on_or_brownout = false;
    report->software_trace_valid = false;
    report->reboot_caller_valid = false;
    report->software_trace.persist_tag = 0u;
    report->software_trace.reboot_caller = 0u;
    report->software_trace.return_address = 0u;
    report->software_trace.program_counter = 0u;
}

bool r1_reset_reason_decode(uint32_t raw,
                            const r1_reset_trace_record *retained_trace,
                            r1_reset_reason_report *report) {
    if (report == NULL) {
        return false;
    }

    clear_report(report);
    report->raw = raw;
    report->recognized = raw & R1_RESET_REASON_KNOWN_MASK;
    report->power_on_or_brownout = raw == 0u;

    if ((raw & R1_RESET_REASON_SOFTWARE) != 0u) {
        report->software_trace_valid = r1_reset_trace_get_snapshot(
            retained_trace, &report->software_trace);
        report->reboot_caller_valid = report->software_trace_valid &&
            report->software_trace.persist_tag == 2u;
    }
    return true;
}
