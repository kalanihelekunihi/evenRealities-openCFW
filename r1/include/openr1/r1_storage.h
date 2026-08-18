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
#define R1_LOG_BIN_PARTITION_BYTES UINT32_C(0x0000c000)
#define R1_LOG_BIN_SECTOR_BYTES UINT32_C(0x00001000)
#define R1_LOG_BIN_SECTOR_COUNT 12u
#define R1_LOG_BIN_ERASED_PROBE_OFFSET UINT32_C(4)
#define R1_LOG_BIN_MAX_WRITE_BYTES R1_LOG_BIN_SECTOR_BYTES
#define R1_STRUCTURED_LOG_CACHE_BYTES UINT32_C(0x00002000)
#define R1_STRUCTURED_LOG_PREFIX_BYTES 12u
#define R1_STRUCTURED_LOG_ARGUMENT_BYTES 32u
#define R1_STRUCTURED_LOG_RECORD_BYTES \
    (R1_STRUCTURED_LOG_PREFIX_BYTES + R1_STRUCTURED_LOG_ARGUMENT_BYTES)
#define R1_STRUCTURED_LOG_STRING_BYTES 16u
#define R1_STRUCTURED_LOG_IMMEDIATE_BYTES 236u
#define R1_STRUCTURED_LOG_PERSIST_BYTES R1_FLASH_PAGE_BYTES
#define R1_STRUCTURED_LOG_PERSIST_GATE_TICKS UINT32_C(10000)
#define R1_STRUCTURED_LOG_MODE_STORAGE UINT8_C(0x01)
#define R1_STRUCTURED_LOG_MODE_IMMEDIATE UINT8_C(0x80)
#define R1_SLEEP_SYNC_MARK_EVENT UINT16_C(0x2001)
#define R1_SLEEP_SYNC_MODEL_IDENTIFIER UINT16_C(0x0601)
#define R1_SLEEP_SYNC_ACK_CONTEXT_BYTES 12u
#define R1_STORAGE_TASK_QUEUE_CAPACITY 10u
#define R1_STORAGE_TASK_RECORD_BYTES 16u
#define R1_STORAGE_TASK_SYNC_GROUP 0u
#define R1_STORAGE_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_STORAGE_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_STORAGE_TASK_DISPATCH_FLAG UINT32_C(1u << 22)
#define R1_STORAGE_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_STORAGE_TASK_STARTUP_ACTION_COUNT 2u
#define R1_STORAGE_TASK_DELAYED_EVENT UINT16_C(0x2005)
#define R1_STORAGE_TASK_DELAYED_EVENT_TICKS UINT32_C(3072)
#define R1_SERVICE_TASK_QUEUE_CAPACITY 50u
#define R1_SERVICE_TASK_RECORD_BYTES 16u
#define R1_SERVICE_TASK_SYNC_GROUP 7u
#define R1_SERVICE_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_SERVICE_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_SERVICE_TASK_DISPATCH_FLAG UINT32_C(1u << 22)
#define R1_SERVICE_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_SERVICE_TASK_STARTUP_ACTION_COUNT 10u

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

#define R1_FLASH_SLOT_HEADER_BYTES 24u
#define R1_FLASH_SLOT_MAGIC_OFFSET 12u

typedef struct {
    bool found;
    bool provider_read_failed;
    uint8_t latest_slot;
    uint8_t next_slot;
    size_t read_count;
} r1_latest_valid_flash_slot_scan_result;

r1_error r1_latest_valid_flash_slot_scan_adapter(
    const r1_flash *flash, uint32_t base_offset, uint32_t slot_bytes,
    uint8_t slot_count, uint32_t expected_magic,
    r1_latest_valid_flash_slot_scan_result *result);

typedef struct {
    uint8_t *bytes;
    uint32_t size;
    uint32_t mutations_before_failure;
    uint32_t bytes_before_failure;
    uint32_t program_operations;
    uint32_t erase_operations;
    uint32_t byte_mutations;
    bool byte_failure_enabled;
} r1_memory_flash;

void r1_memory_flash_initialize(r1_memory_flash *memory, uint8_t *bytes, uint32_t size);
void r1_memory_flash_fail_after(r1_memory_flash *memory, uint32_t successful_mutations);
/* Injects a conservative power cut within a program or erase operation after
 * exactly `successful_bytes` byte mutations. UINT32_MAX disables the byte
 * fault. This supplements, rather than replaces, whole-operation faults. */
void r1_memory_flash_fail_after_bytes(
    r1_memory_flash *memory, uint32_t successful_bytes);
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

typedef struct {
    const r1_flash *flash;
    uint32_t partition_offset;
    uint16_t current_sector;
    uint16_t sector_offset;
    bool bound;
    bool initialized;
} r1_log_bin_store;

typedef struct {
    uint8_t *bytes;
    uint32_t capacity;
    uint32_t read_index;
    uint32_t write_index;
    uint32_t last_persist_tick;
    uint8_t mode;
    uint8_t severity_threshold;
    uint8_t sequence;
    bool initialized;
} r1_structured_log_cache;

typedef enum {
    R1_STRUCTURED_LOG_ACTION_NONE = 0,
    R1_STRUCTURED_LOG_ACTION_IMMEDIATE_READY,
    R1_STRUCTURED_LOG_ACTION_PERSIST_READY
} r1_structured_log_action;

typedef enum {
    R1_STRUCTURED_LOG_ARGUMENT_U32 = 0,
    R1_STRUCTURED_LOG_ARGUMENT_U64,
    R1_STRUCTURED_LOG_ARGUMENT_FLOAT64,
    R1_STRUCTURED_LOG_ARGUMENT_STRING
} r1_structured_log_argument_type;

typedef struct {
    r1_structured_log_argument_type type;
    union {
        uint32_t u32;
        uint64_t u64;
        double floating;
        const char *string;
    } value;
} r1_structured_log_argument;

typedef struct {
    bool appended;
    bool filtered;
    uint16_t record_bytes;
    r1_structured_log_action action;
} r1_structured_log_encode_result;

typedef struct {
    bool eligible;
    bool ep_magic_present;
    uint8_t log_sector_count;
    uint16_t cache_bytes;
    uint16_t crash_bytes;
    uint32_t total_bytes;
    uint32_t checksum;
} r1_log_export_info;

typedef struct {
    const r1_flash *flash;
    r1_structured_log_cache *cache;
    const uint8_t *crash;
    uint32_t ep_offset;
    uint32_t log_offset;
    uint8_t log_sector_order[R1_LOG_BIN_SECTOR_COUNT];
    r1_log_export_info info;
    bool active;
} r1_log_export_snapshot;

typedef enum {
    R1_EP_INITIALIZATION_READY = 0,
    R1_EP_INITIALIZATION_PARTITION_NOT_FOUND,
    R1_EP_INITIALIZATION_DEVICE_NOT_FOUND,
    R1_EP_INITIALIZATION_PARTITION_TOO_SMALL
} r1_ep_initialization_reason;

typedef struct {
    bool initialized;
    bool retain_partition;
    bool retain_device;
    bool scan_cursor;
    r1_ep_initialization_reason reason;
} r1_ep_initialization_plan;

typedef struct {
    bool context_present;
    bool publish_event;
    bool publish_failed;
    bool release_context;
    uint16_t event_identifier;
    size_t event_payload_length;
} r1_sleep_sync_ack_plan;

typedef struct {
    bool context_present;
    bool callback_result;
    bool skip_synchronized_record;
    bool invoke_packet_builder;
    uint8_t report_type;
    uint16_t stage_count;
    uint16_t model_identifier;
} r1_sleep_sync_report_plan;

typedef enum {
    R1_FDS_PERSISTENCE_EVENT_NONE = 0,
    R1_FDS_PERSISTENCE_RECORD_SUCCEEDED = 9,
    R1_FDS_PERSISTENCE_RECORD_FAILED = 10,
    R1_FDS_PERSISTENCE_FILE_DELETE_SUCCEEDED = 11,
    R1_FDS_PERSISTENCE_FILE_DELETE_FAILED = 12,
    R1_FDS_PERSISTENCE_GC_SUCCEEDED = 20,
    R1_FDS_PERSISTENCE_GC_FAILED = 21
} r1_fds_persistence_event;

typedef struct {
    bool publish_event;
    bool updated_record;
    bool clear_file_bookkeeping;
    bool mark_retry_pending;
    bool request_next_queued_operation;
    r1_fds_persistence_event persistence_event;
    uint16_t logical_record_key;
    uint32_t record_id;
    uint32_t provider_result;
} r1_fds_event_plan;

typedef enum {
    R1_STORAGE_TASK_BACKEND_INITIALIZE = 0,
    R1_STORAGE_TASK_SCHEDULE_DELAYED_EVENT
} r1_storage_task_startup_action;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    const char *registry_name;
    uint32_t watchdog_ticks;
    r1_storage_task_startup_action
        actions[R1_STORAGE_TASK_STARTUP_ACTION_COUNT];
    size_t action_count;
} r1_storage_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool dispatch_event_record;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool wait_again;
} r1_storage_task_flag_plan;

typedef enum {
    R1_SERVICE_TASK_HARDWARE_INITIALIZE = 0,
    R1_SERVICE_TASK_HEALTH_DATABASE_START,
    R1_SERVICE_TASK_HEART_RATE_CACHE_REFRESH,
    R1_SERVICE_TASK_SPO2_CACHE_REFRESH,
    R1_SERVICE_TASK_TEMPERATURE_CACHE_REFRESH,
    R1_SERVICE_TASK_STRESS_CACHE_REFRESH,
    R1_SERVICE_TASK_ACTIVITY_CACHE_REFRESH,
    R1_SERVICE_TASK_SLEEP_DATABASE_START,
    R1_SERVICE_TASK_HRV_CACHE_REFRESH,
    R1_SERVICE_TASK_PROTOCOL_STATE_RESET
} r1_service_task_startup_action;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    const char *registry_name;
    uint32_t watchdog_ticks;
    r1_service_task_startup_action
        actions[R1_SERVICE_TASK_STARTUP_ACTION_COUNT];
    size_t action_count;
} r1_service_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool dispatch_event_record;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool wait_again;
} r1_service_task_flag_plan;

r1_error r1_export_plan_command(
    r1_export_state *state, const r1_export_observation *observation,
    r1_export_plan *plan);
r1_error r1_ep_scan_cursor(const uint8_t *records, size_t length,
                           r1_ep_scan_result *result);
/* Provider-backed form of the recovered ep.bin recovery scan. It reads only
 * fixed eight-byte records and returns cursor/timestamp metadata; record
 * payload bytes are never returned to the caller. */
r1_error r1_ep_scan_flash_cursor(
    const r1_flash *flash, uint32_t partition_offset,
    r1_ep_scan_result *result);

/* Exact recovered log.bin circular-page writer. The API can append only to
 * the fixed 12-page partition supplied at bind time and has no read/export or
 * arbitrary erase surface. */
r1_error r1_log_bin_bind(
    r1_log_bin_store *store, const r1_flash *flash,
    uint32_t partition_offset, uint32_t partition_bytes);
uint16_t r1_log_bin_sector_count(const r1_log_bin_store *store);
r1_error r1_log_bin_initialize(r1_log_bin_store *store);
r1_error r1_log_bin_write(
    r1_log_bin_store *store, const uint8_t *input, size_t length);

/* Clean-room reconstruction of the product's private structured-log cache.
 * The cache has no transport surface. Its read API is explicit about peek
 * versus consume, and the bounded snapshot source may use offset peek only
 * while a platform freezes producers. The periodic writer can target only a
 * bound log.bin store. */
r1_error r1_structured_log_cache_initialize(
    r1_structured_log_cache *cache, uint8_t *bytes, size_t capacity);
size_t r1_structured_log_cache_count(
    const r1_structured_log_cache *cache);
size_t r1_structured_log_cache_free(
    const r1_structured_log_cache *cache);
r1_error r1_structured_log_cache_read(
    r1_structured_log_cache *cache, uint8_t *output, size_t length,
    bool consume);
r1_error r1_structured_log_cache_peek(
    const r1_structured_log_cache *cache, size_t offset,
    uint8_t *output, size_t length);
r1_error r1_structured_log_cache_append(
    r1_structured_log_cache *cache, const uint8_t *input, size_t length,
    r1_structured_log_action *action);
void r1_structured_log_threshold_set(
    r1_structured_log_cache *cache, uint8_t threshold);
uint8_t r1_structured_log_mode_get(
    const r1_structured_log_cache *cache);
void r1_structured_log_mode_set(
    r1_structured_log_cache *cache, uint8_t mode);
r1_error r1_structured_log_encode_typed(
    r1_structured_log_cache *cache, uint32_t metadata,
    uint32_t tick, uint32_t timestamp,
    const r1_structured_log_argument *arguments, size_t argument_count,
    r1_structured_log_encode_result *result);
r1_error r1_structured_log_encode_format(
    r1_structured_log_cache *cache, uint32_t metadata,
    uint32_t tick, uint32_t timestamp, const char *format,
    const r1_structured_log_argument *arguments, size_t argument_count,
    r1_structured_log_encode_result *result);
r1_error r1_structured_log_periodic_persist(
    r1_structured_log_cache *cache, r1_log_bin_store *store,
    uint32_t tick, bool export_active,
    uint8_t scratch[R1_STRUCTURED_LOG_PERSIST_BYTES], bool *persisted);

/* Bounded composite diagnostic virtual file recovered from the retail
 * log.bin provider. This layer performs no transport and grants no flash
 * mutation. A platform must freeze all three producers for snapshot life and
 * apply owner authorization before exposing begin/read/finish. */
r1_error r1_log_export_snapshot_prepare(
    r1_log_export_snapshot *snapshot, const r1_flash *flash,
    uint32_t ep_offset, uint32_t log_offset,
    r1_structured_log_cache *cache,
    const uint8_t *crash, size_t crash_length,
    uint8_t scratch[R1_LOG_BIN_SECTOR_BYTES]);
r1_error r1_log_export_snapshot_read(
    const r1_log_export_snapshot *snapshot, uint32_t offset,
    uint8_t *output, size_t length);
void r1_log_export_snapshot_finish(r1_log_export_snapshot *snapshot);
r1_error r1_ep_plan_initialization(
    bool already_initialized, bool partition_found, bool device_found,
    uint32_t partition_bytes, r1_ep_initialization_plan *plan);
r1_error r1_sleep_sync_plan_acknowledgement(
    bool context_present, bool event_publish_succeeded,
    r1_sleep_sync_ack_plan *plan);
r1_error r1_sleep_sync_plan_report_callback(
    bool context_present, uint8_t synchronization_flag,
    uint8_t report_type, uint16_t stage_count,
    r1_sleep_sync_report_plan *plan);
r1_error r1_fds_plan_event(
    uint8_t provider_event_id, uint32_t provider_result,
    uint16_t record_key, uint32_t record_id, bool metadata_validated,
    bool retry_already_pending, r1_fds_event_plan *plan);
r1_error r1_storage_task_plan_startup(
    bool queue_created, r1_storage_task_startup_plan *plan);
r1_error r1_storage_task_plan_flags(
    uint32_t flags, r1_storage_task_flag_plan *plan);
r1_error r1_service_task_plan_startup(
    bool queue_created, r1_service_task_startup_plan *plan);
r1_error r1_service_task_plan_flags(
    uint32_t flags, r1_service_task_flag_plan *plan);

#endif
