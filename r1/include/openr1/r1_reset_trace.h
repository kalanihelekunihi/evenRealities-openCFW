#ifndef OPENR1_R1_RESET_TRACE_H
#define OPENR1_R1_RESET_TRACE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define R1_RESET_TRACE_BYTES 16u
#define R1_RESET_TRACE_CRC_INPUT_BYTES 14u
#define R1_RESET_TRACE_FIELD_COUNT 13u
#define R1_RESET_TRACE_PERSIST_TAG_INDEX 0u
#define R1_RESET_TRACE_REBOOT_CALLER_INDEX 1u
#define R1_RESET_TRACE_RETURN_ADDRESS_INDEX 2u
#define R1_RESET_TRACE_PROGRAM_COUNTER_INDEX 6u
#define R1_RESET_TRACE_FAULT_TAG 7u

typedef struct {
    uint8_t bytes[R1_RESET_TRACE_BYTES];
} r1_reset_trace_record;

typedef struct {
    uint8_t persist_tag;
    uint8_t reboot_caller;
    uint32_t return_address;
    uint32_t program_counter;
} r1_reset_trace_snapshot;

bool r1_reset_trace_valid(const r1_reset_trace_record *record);
void r1_reset_trace_clear(r1_reset_trace_record *record);
void r1_reset_trace_initialize(r1_reset_trace_record *record);
bool r1_reset_trace_read_byte(const r1_reset_trace_record *record,
                              uint8_t field_index, uint8_t *value);
bool r1_reset_trace_write_byte(r1_reset_trace_record *record,
                               uint8_t field_index, uint8_t value);
bool r1_reset_trace_read_return_address(const r1_reset_trace_record *record,
                                        uint32_t *value);
bool r1_reset_trace_read_program_counter(const r1_reset_trace_record *record,
                                         uint32_t *value);
void r1_reset_trace_clear_addresses(r1_reset_trace_record *record);
void r1_reset_trace_set_return_address(r1_reset_trace_record *record,
                                       uint32_t value);
void r1_reset_trace_set_program_counter(r1_reset_trace_record *record,
                                        uint32_t value);
void r1_reset_trace_set_reboot_caller(r1_reset_trace_record *record,
                                      uint8_t reboot_caller);
void r1_reset_trace_set_persist_tag(r1_reset_trace_record *record,
                                    uint8_t persist_tag);
void r1_reset_trace_capture_site(r1_reset_trace_record *record,
                                 uint32_t program_counter,
                                 uint32_t return_address);
bool r1_reset_trace_get_snapshot(const r1_reset_trace_record *record,
                                 r1_reset_trace_snapshot *snapshot);

#endif
