#ifndef OPENR1_R1_RESET_REASON_H
#define OPENR1_R1_RESET_REASON_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_reset_trace.h"

#define R1_RESET_REASON_PIN UINT32_C(0x00000001)
#define R1_RESET_REASON_WATCHDOG UINT32_C(0x00000002)
#define R1_RESET_REASON_SOFTWARE UINT32_C(0x00000004)
#define R1_RESET_REASON_LOCKUP UINT32_C(0x00000008)
#define R1_RESET_REASON_SYSTEM_OFF_GPIO UINT32_C(0x00010000)
#define R1_RESET_REASON_SYSTEM_OFF_LPCOMP UINT32_C(0x00020000)
#define R1_RESET_REASON_SYSTEM_OFF_DEBUG UINT32_C(0x00040000)
#define R1_RESET_REASON_KNOWN_MASK UINT32_C(0x0007000f)

typedef struct {
    uint32_t raw;
    uint32_t recognized;
    bool power_on_or_brownout;
    bool software_trace_valid;
    bool reboot_caller_valid;
    r1_reset_trace_snapshot software_trace;
} r1_reset_reason_report;

bool r1_reset_reason_decode(uint32_t raw,
                            const r1_reset_trace_record *retained_trace,
                            r1_reset_reason_report *report);

#endif
