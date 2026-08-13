#include "openr1_reset_trace_port.h"

#include "nrf.h"

static r1_reset_trace_record retained_reset_trace
    __attribute__((section(".openr1_noinit"), aligned(4)));

r1_reset_trace_record *openr1_reset_trace_retained_record(void) {
    r1_reset_trace_initialize(&retained_reset_trace);
    return &retained_reset_trace;
}

void openr1_reset_trace_capture(uint8_t persist_tag, uint8_t reboot_caller,
                                uint32_t program_counter,
                                uint32_t return_address) {
    r1_reset_trace_record *record = openr1_reset_trace_retained_record();
    r1_reset_trace_set_persist_tag(record, persist_tag);
    r1_reset_trace_set_reboot_caller(record, reboot_caller);
    r1_reset_trace_capture_site(record, program_counter, return_address);
}

__attribute__((noreturn))
void openr1_reset_trace_fault_and_reset(uint32_t program_counter,
                                        uint32_t return_address) {
    r1_reset_trace_record *record = openr1_reset_trace_retained_record();
    r1_reset_trace_set_persist_tag(record, R1_RESET_TRACE_FAULT_TAG);
    r1_reset_trace_capture_site(record, program_counter, return_address);
    NVIC_SystemReset();
}

typedef struct {
    r1_reset_trace_record *(*retained_record)(void);
    void (*capture)(uint8_t, uint8_t, uint32_t, uint32_t);
    void (*fault_and_reset)(uint32_t, uint32_t);
    bool (*snapshot)(const r1_reset_trace_record *, r1_reset_trace_snapshot *);
} openr1_reset_trace_api;

__attribute__((used, section(".openr1_reset_trace_api")))
static const openr1_reset_trace_api reset_trace_api = {
    openr1_reset_trace_retained_record,
    openr1_reset_trace_capture,
    openr1_reset_trace_fault_and_reset,
    r1_reset_trace_get_snapshot,
};
