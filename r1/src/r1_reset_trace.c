#include "openr1/r1_reset_trace.h"

#include "openr1/r1_crc.h"

#define R1_RESET_TRACE_VALID_MARKER 0u
#define R1_RESET_TRACE_STORAGE_OFFSET 1u
#define R1_RESET_TRACE_CRC_OFFSET 14u
#define R1_RESET_TRACE_U32_BYTES 4u

static void clear_bytes(uint8_t *bytes, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

static uint16_t stored_crc(const r1_reset_trace_record *record) {
    return (uint16_t)((uint16_t)record->bytes[R1_RESET_TRACE_CRC_OFFSET] |
                      ((uint16_t)record->bytes[R1_RESET_TRACE_CRC_OFFSET + 1u]
                       << 8u));
}

static void seal(r1_reset_trace_record *record) {
    const uint16_t crc = r1_crc16_modbus(
        record->bytes, R1_RESET_TRACE_CRC_INPUT_BYTES);
    record->bytes[R1_RESET_TRACE_CRC_OFFSET] = (uint8_t)crc;
    record->bytes[R1_RESET_TRACE_CRC_OFFSET + 1u] = (uint8_t)(crc >> 8u);
}

static void ensure_valid(r1_reset_trace_record *record) {
    if (!r1_reset_trace_valid(record)) {
        r1_reset_trace_clear(record);
    }
}

static uint32_t read_u32(const r1_reset_trace_record *record,
                         uint8_t field_index) {
    uint32_t value = 0u;
    for (uint8_t offset = 0u; offset < R1_RESET_TRACE_U32_BYTES; ++offset) {
        value |= (uint32_t)record->bytes[
            R1_RESET_TRACE_STORAGE_OFFSET + field_index + offset]
            << (8u * offset);
    }
    return value;
}

static void write_u32(r1_reset_trace_record *record, uint8_t field_index,
                      uint32_t value) {
    ensure_valid(record);
    for (uint8_t offset = 0u; offset < R1_RESET_TRACE_U32_BYTES; ++offset) {
        record->bytes[R1_RESET_TRACE_STORAGE_OFFSET + field_index + offset] =
            (uint8_t)(value >> (8u * offset));
    }
    seal(record);
}

bool r1_reset_trace_valid(const r1_reset_trace_record *record) {
    if (record == NULL ||
        record->bytes[0] != R1_RESET_TRACE_VALID_MARKER) {
        return false;
    }
    return stored_crc(record) == r1_crc16_modbus(
        record->bytes, R1_RESET_TRACE_CRC_INPUT_BYTES);
}

void r1_reset_trace_clear(r1_reset_trace_record *record) {
    if (record == NULL) {
        return;
    }
    clear_bytes(record->bytes, sizeof(record->bytes));
    seal(record);
}

void r1_reset_trace_initialize(r1_reset_trace_record *record) {
    if (record != NULL) {
        ensure_valid(record);
    }
}

bool r1_reset_trace_read_byte(const r1_reset_trace_record *record,
                              uint8_t field_index, uint8_t *value) {
    if (value == NULL || field_index >= R1_RESET_TRACE_FIELD_COUNT ||
        !r1_reset_trace_valid(record)) {
        return false;
    }
    *value = record->bytes[R1_RESET_TRACE_STORAGE_OFFSET + field_index];
    return true;
}

bool r1_reset_trace_write_byte(r1_reset_trace_record *record,
                               uint8_t field_index, uint8_t value) {
    if (record == NULL || field_index >= R1_RESET_TRACE_FIELD_COUNT) {
        return false;
    }
    ensure_valid(record);
    record->bytes[0] = R1_RESET_TRACE_VALID_MARKER;
    record->bytes[R1_RESET_TRACE_STORAGE_OFFSET + field_index] = value;
    seal(record);
    return true;
}

bool r1_reset_trace_read_return_address(const r1_reset_trace_record *record,
                                        uint32_t *value) {
    if (value == NULL || !r1_reset_trace_valid(record)) {
        return false;
    }
    *value = read_u32(record, R1_RESET_TRACE_RETURN_ADDRESS_INDEX);
    return true;
}

bool r1_reset_trace_read_program_counter(const r1_reset_trace_record *record,
                                         uint32_t *value) {
    if (value == NULL || !r1_reset_trace_valid(record)) {
        return false;
    }
    *value = read_u32(record, R1_RESET_TRACE_PROGRAM_COUNTER_INDEX);
    return true;
}

void r1_reset_trace_clear_addresses(r1_reset_trace_record *record) {
    if (record == NULL) {
        return;
    }
    ensure_valid(record);
    for (uint8_t index = R1_RESET_TRACE_RETURN_ADDRESS_INDEX;
         index < R1_RESET_TRACE_PROGRAM_COUNTER_INDEX +
                     R1_RESET_TRACE_U32_BYTES;
         ++index) {
        record->bytes[R1_RESET_TRACE_STORAGE_OFFSET + index] = 0u;
    }
    seal(record);
}

void r1_reset_trace_set_return_address(r1_reset_trace_record *record,
                                       uint32_t value) {
    if (record != NULL) {
        write_u32(record, R1_RESET_TRACE_RETURN_ADDRESS_INDEX, value);
    }
}

void r1_reset_trace_set_program_counter(r1_reset_trace_record *record,
                                        uint32_t value) {
    if (record != NULL) {
        write_u32(record, R1_RESET_TRACE_PROGRAM_COUNTER_INDEX, value);
    }
}

void r1_reset_trace_set_reboot_caller(r1_reset_trace_record *record,
                                      uint8_t reboot_caller) {
    if (record == NULL) {
        return;
    }
    r1_reset_trace_clear_addresses(record);
    (void)r1_reset_trace_write_byte(
        record, R1_RESET_TRACE_REBOOT_CALLER_INDEX, reboot_caller);
}

void r1_reset_trace_set_persist_tag(r1_reset_trace_record *record,
                                    uint8_t persist_tag) {
    if (record == NULL) {
        return;
    }
    if (persist_tag != R1_RESET_TRACE_FAULT_TAG) {
        r1_reset_trace_clear_addresses(record);
    }
    (void)r1_reset_trace_write_byte(
        record, R1_RESET_TRACE_PERSIST_TAG_INDEX, persist_tag);
}

void r1_reset_trace_capture_site(r1_reset_trace_record *record,
                                 uint32_t program_counter,
                                 uint32_t return_address) {
    if (record == NULL) {
        return;
    }
    if (program_counter != 0u) {
        r1_reset_trace_set_program_counter(record, program_counter);
    }
    if (return_address != 0u) {
        r1_reset_trace_set_return_address(record, return_address);
    }
}

bool r1_reset_trace_get_snapshot(const r1_reset_trace_record *record,
                                 r1_reset_trace_snapshot *snapshot) {
    if (snapshot == NULL || !r1_reset_trace_valid(record)) {
        return false;
    }
    snapshot->persist_tag = record->bytes[
        R1_RESET_TRACE_STORAGE_OFFSET + R1_RESET_TRACE_PERSIST_TAG_INDEX];
    snapshot->reboot_caller = record->bytes[
        R1_RESET_TRACE_STORAGE_OFFSET + R1_RESET_TRACE_REBOOT_CALLER_INDEX];
    snapshot->return_address = read_u32(
        record, R1_RESET_TRACE_RETURN_ADDRESS_INDEX);
    snapshot->program_counter = read_u32(
        record, R1_RESET_TRACE_PROGRAM_COUNTER_INDEX);
    return true;
}
