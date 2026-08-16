#ifndef OPENR1_RESET_ZEPHYR_H
#define OPENR1_RESET_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_reset_reason.h"
#include "openr1/r1_reset_trace.h"

void openr1_reset_zephyr_initialize(void);
bool openr1_reset_zephyr_latest(r1_reset_reason_report *report);
r1_reset_trace_record *openr1_reset_zephyr_retained_record(void);
void openr1_reset_zephyr_capture(uint8_t persist_tag, uint8_t reboot_caller,
                                 uint32_t program_counter,
                                 uint32_t return_address);
__attribute__((noreturn))
void openr1_reset_zephyr_fault_and_reset(uint32_t program_counter,
                                         uint32_t return_address);

#endif
