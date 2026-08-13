#ifndef OPENR1_RESET_TRACE_PORT_H
#define OPENR1_RESET_TRACE_PORT_H

#include <stdint.h>

#include "openr1/r1_reset_trace.h"

r1_reset_trace_record *openr1_reset_trace_retained_record(void);
void openr1_reset_trace_capture(uint8_t persist_tag, uint8_t reboot_caller,
                                uint32_t program_counter,
                                uint32_t return_address);
__attribute__((noreturn))
void openr1_reset_trace_fault_and_reset(uint32_t program_counter,
                                        uint32_t return_address);

#endif
