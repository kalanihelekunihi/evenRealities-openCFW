#ifndef OPENR1_R1_STORAGE_H
#define OPENR1_R1_STORAGE_H

#include <stddef.h>
#include <stdint.h>

#include <stdbool.h>

#include "openr1/r1_protocol.h"

#define R1_FLASH_PAGE_BYTES 4096u
#define R1_STORAGE_PARTITION_COUNT 7u
#define R1_EXPORT_CONTROL_BYTES 10u
#define R1_EXPORT_MAX_CHUNK_BYTES 4096u
#define R1_EXPORT_INTERFRAME_DELAY_MS 50u
#define R1_EP_PARTITION_BYTES 8192u
#define R1_EP_RECORD_BYTES 8u
#define R1_EP_RECORD_COUNT 1024u
#define R1_EP_RECORD_MAGIC UINT8_C(0x0a)

typedef struct {
    const char *name;
    uint32_t offset;
    uint32_t length;
} r1_partition;

extern const r1_partition r1_storage_partitions[R1_STORAGE_PARTITION_COUNT];
const r1_partition *r1_storage_partition(const char *name);

typedef bool (*r1_flash_read_fn)(void *context, uint32_t offset,
                                 uint8_t *output, size_t length);
typedef bool (*r1_flash_program_fn)(void *context, uint32_t offset,
                                    const uint8_t *input, size_t length);
typedef bool (*r1_flash_erase_fn)(void *context, uint32_t offset, size_t length);

typedef struct {
    void *context;
    uint32_t size;
    r1_flash_read_fn read;
    r1_flash_program_fn program;
    r1_flash_erase_fn erase;
} r1_flash;

r1_error r1_flash_read(const r1_flash *flash, uint32_t offset,
                       uint8_t *output, size_t length);
r1_error r1_flash_program(const r1_flash *flash, uint32_t offset,
                          const uint8_t *input, size_t length);
r1_error r1_flash_erase(const r1_flash *flash, uint32_t offset, size_t length);

typedef struct {
    uint8_t *bytes;
    uint32_t size;
    uint32_t mutations_before_failure;
    uint32_t program_operations;
    uint32_t erase_operations;
} r1_memory_flash;

void r1_memory_flash_initialize(r1_memory_flash *memory, uint8_t *bytes, uint32_t size);
void r1_memory_flash_fail_after(r1_memory_flash *memory, uint32_t successful_mutations);
r1_flash r1_memory_flash_interface(r1_memory_flash *memory);

typedef struct {
    uint32_t total_bytes;
    uint32_t offset;
    bool active;
} r1_export_state;

typedef struct {
    uint8_t command;
    uint8_t result;
    bool metadata_available;
    uint32_t total_bytes;
    uint32_t checksum;
} r1_export_observation;

typedef struct {
    uint8_t control[R1_EXPORT_CONTROL_BYTES];
    size_t control_length;
    bool send_data_marker;
    uint32_t delay_before_data_ms;
    bool start_provider;
    bool finalize_provider;
    bool reset_offset;
    uint32_t read_offset;
    size_t read_length;
} r1_export_plan;

typedef struct {
    uint16_t write_cursor;
    uint16_t first_free_index;
    uint16_t latest_timestamp_index;
    uint32_t latest_timestamp;
    bool first_free_found;
    bool latest_nonzero_timestamp_found;
    bool all_records_have_magic;
} r1_ep_scan_result;

r1_error r1_export_plan_command(
    r1_export_state *state, const r1_export_observation *observation,
    r1_export_plan *plan);
r1_error r1_ep_scan_cursor(const uint8_t *records, size_t length,
                           r1_ep_scan_result *result);

#endif
