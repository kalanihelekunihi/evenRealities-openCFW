#include "openr1_databases.h"

#include <stddef.h>
#include <string.h>
#include <time.h>

#include "cmsis_os2.h"
#include "fal.h"
#include "flashdb.h"
#include "FreeRTOS.h"

#include "openr1/r1_event_bus.h"
#include "openr1/r1_peer_target.h"
#include "openr1/r1_state.h"
#include "openr1_clock.h"
#include "openr1_event_bus.h"
#include "openr1_storage.h"

/* Recovered health.db schema payload lengths: byte 1 of each of the six
 * 16-byte schema descriptors in the stock table at 0x00099BF4.  Their sum
 * (42) plus the 8-byte record overhead passes the 128-byte startup gate. */
static const uint8_t health_schema_bytes[R1_HEALTH_DB_SCHEMA_COUNT] = {
    3u, 3u, 3u, 3u, 24u, 6u,
};

static r1_kv_store kv_store;
static bool kv_ready;

static struct fdb_tsdb health_tsdb;
static osMutexId_t health_mutex;
static bool health_ready;
static r1_health_db_startup_result health_startup_result;

static r1_sleep_db sleep_db;
static bool sleep_ready;

/* Platform instance of the R1 private event bus.  The health startup
 * controller subscribes its recovered time-listener channels (bus slots 1
 * then 0) here.  openr1_databases_initialize binds the queue handoff
 * through openr1_event_bus_bind: one CMSIS queue per event-id window plus
 * a consumer thread that delivers records through r1_event_bus_multicast
 * (openr1_event_bus.c).  If the bind fails the sink stays unbound, the
 * error is recorded, and r1_event_bus_publish keeps returning
 * R1_ERROR_UNSUPPORTED on this instance.  Subscription is single-threaded
 * (the storage worker); any publisher must take the stock bus mutex role. */
static r1_event_bus event_bus;
static volatile uint32_t time_listener_deliveries;

static volatile uint32_t databases_error;
static volatile uint32_t recovery_records_visited;

#define OPENR1_DATABASES_PERSIST_REG1_FLAG UINT32_C(0x00000001)
#define OPENR1_DATABASES_NV_RECOVERY_FLAG UINT32_C(0x00000002)
#define OPENR1_DATABASES_REMOVE_RING_FLAG UINT32_C(0x00000004)
#define OPENR1_DATABASES_NV_RECOVERY_QUEUE_DEPTH 2u

static osThreadId_t databases_worker_thread;
/* Deferred REG1 persist request: the EUS dispatch runs on the SoftDevice
 * event thread, where openr1_storage rejects flash mutations, so the writer
 * only records the request and wakes the storage worker.  Two rapid writes
 * collapse to the latest value, which is the desired end state. */
static volatile bool reg1_persist_pending;
static volatile bool reg1_persist_enabled;
static bool reg1_enabled;
static osMessageQueueId_t nv_recovery_queue;
static volatile bool remove_ring_pending;

typedef struct {
    uint16_t expected_crc;
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES];
} openr1_nv_recovery_request;

static StaticTask_t databases_control_block;
static StackType_t databases_stack[configMINIMAL_STACK_SIZE * 3u];

/* Retained across a watchdog or software reset so the health startup
 * controller can perform the recovered crash-time handoff and one-shot
 * snapshot restore. */
static r1_health_crash_record health_crash_record
    __attribute__((section(".openr1_noinit"), aligned(4)));
static r1_activity_history health_activity;
static r1_health_u8_history health_heart_rate;
static r1_health_u8_accumulator health_heart_rate_accumulator;
static r1_health_u8_history health_spo2;
static r1_health_u16_history health_hrv;

static void databases_record_error(uint32_t error) {
    if (databases_error == 0u) {
        databases_error = error;
    }
}

static void health_tsdb_lock(fdb_db_t database) {
    (void)database;
    if (health_mutex != NULL) {
        (void)osMutexAcquire(health_mutex, osWaitForever);
    }
}

static void health_tsdb_unlock(fdb_db_t database) {
    (void)database;
    if (health_mutex != NULL) {
        (void)osMutexRelease(health_mutex);
    }
}

static void health_control(void *context, r1_health_db_control control) {
    (void)context;
    /* Recovered control values 2 then 3 are FDB_TSDB_CTRL_SET_LOCK and
     * FDB_TSDB_CTRL_SET_UNLOCK; they register the callbacks with FlashDB. */
    fdb_tsdb_control(
        &health_tsdb,
        control == R1_HEALTH_DB_LOCK_CONTROL
            ? FDB_TSDB_CTRL_SET_LOCK : FDB_TSDB_CTRL_SET_UNLOCK,
        control == R1_HEALTH_DB_LOCK_CONTROL
            ? health_tsdb_lock : health_tsdb_unlock);
}

static fdb_time_t health_get_time(void) {
    /* Fail closed: r1_clock_now reports no time before the first phone
     * synchronization and none is ever fabricated.  The FlashDB callback type
     * cannot carry an error, so an unsynchronized clock yields timestamp 0,
     * which consumers must not treat as a real sample time. */
    uint32_t epoch = 0u;
    if (!openr1_clock_epoch(&epoch)) {
        return (fdb_time_t)0;
    }
    return (fdb_time_t)epoch;
}

static r1_error health_initialize(
    void *context, const char *name, const char *path, size_t record_bytes) {
    (void)context;
    return fdb_tsdb_init(
               &health_tsdb, name, path, health_get_time, record_bytes,
               NULL) == FDB_NO_ERR
        ? R1_OK : R1_ERROR_STATE;
}

static void health_ensure_mutex(void *context) {
    (void)context;
    if (health_mutex == NULL) {
        health_mutex = osMutexNew(NULL);
    }
}

static void health_time_listener(
    const uint8_t *payload, size_t length, void *context) {
    (void)payload;
    (void)length;
    (void)context;
    /* The recovered listener bodies behind the health time subscriptions are
     * not part of the admitted closure, so no health action is invented
     * here; deliveries are only counted so the binding stays observable. */
    time_listener_deliveries += 1u;
}

static void health_subscribe_time(void *context, uint8_t event_index) {
    (void)context;
    /* The startup controller calls this op with channels 1 then 0 (recovered
     * order).  Those channels are the private event-bus slots: slot 1 is the
     * local-hour boundary and slot 0 the material wall-clock/timezone
     * transition (EVENT-BUS-CORRELATION.md).  Fail explicit: a rejected
     * subscription is recorded instead of being dropped like the stock 0
     * return. */
    if (r1_event_bus_subscribe(
            &event_bus, event_index, health_time_listener, NULL) != R1_OK) {
        databases_record_error((uint32_t)NRF_ERROR_INTERNAL);
    }
}

static void health_set_clock(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes) {
    (void)context;
    openr1_clock_adopt_phone_time(timestamp, utc_offset_minutes);
}

static void health_mark_clock_valid(void *context) {
    (void)context;
    /* openr1_clock_adopt_phone_time validates the UTC offset and marks the
     * clock synchronized atomically; r1_clock keeps no separate validity
     * flag, so the recovered conditional mark-valid step has no distinct
     * state to set. */
}

static void health_current_clock(
    void *context, uint32_t *timestamp, int16_t *utc_offset_minutes) {
    (void)context;
    uint32_t epoch = 0u;
    int16_t offset = 0;
    /* Fail closed like health_get_time: an unsynchronized clock reports
     * 0/0 rather than a fabricated time. */
    if (openr1_clock_epoch(&epoch)) {
        (void)openr1_clock_utc_offset(&offset);
    }
    *timestamp = epoch;
    *utc_offset_minutes = offset;
}

static uint32_t health_local_day_start(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes) {
    (void)context;
    /* Toolchain-gmtime route admitted by
     * docs/boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md: shift to local
     * time, break it down, clear hour/minute/second, and shift the local
     * midnight back to UTC.  No code from the blocked time/calendar family;
     * the validating inverse converter stays unreproduced because the
     * subtract-back below needs no calendar-to-epoch conversion. */
    const int64_t local =
        (int64_t)timestamp + (int64_t)utc_offset_minutes * INT64_C(60);
    if (local <= 0) {
        return 0u;
    }
    const time_t moment = (time_t)(uint32_t)local;
    struct tm broken;
    if (gmtime_r(&moment, &broken) == NULL) {
        return 0u;
    }
    const uint32_t within_day = (uint32_t)broken.tm_hour * UINT32_C(3600) +
        (uint32_t)broken.tm_min * 60u + (uint32_t)broken.tm_sec;
    const uint32_t local_start = (uint32_t)local - within_day;
    const int64_t utc_start =
        (int64_t)local_start - (int64_t)utc_offset_minutes * INT64_C(60);
    return utc_start <= 0 ? 0u : (uint32_t)utc_start;
}

static void *health_allocate(void *context, size_t bytes) {
    (void)context;
    return pvPortMalloc(bytes);
}

static void health_release(void *context, void *allocation) {
    (void)context;
    vPortFree(allocation);
}

typedef struct {
    uint8_t *workspace;
    size_t workspace_bytes;
} health_recovery;

static bool health_recover_record(fdb_tsl_t record, void *opaque) {
    /* Bounded recovery pass: each record in the recovered
     * [local_day_start, now] interval is read into the zeroed 128-byte
     * workspace the controller supplied.  Decoding bodies into the RAM
     * caches remains a separate health-storage consumer; nothing is
     * fabricated here. */
    health_recovery *recovery = opaque;
    struct fdb_blob blob;
    const size_t read = fdb_blob_read(
        (fdb_db_t)&health_tsdb,
        fdb_tsl_to_blob(
            record, fdb_blob_make(
                &blob, recovery->workspace, recovery->workspace_bytes)));
    if (read > 0u) {
        recovery_records_visited += 1u;
    }
    return false;
}

static void health_recover(
    void *context, uint32_t from_timestamp, uint32_t to_timestamp,
    uint8_t *workspace, size_t workspace_bytes) {
    (void)context;
    health_recovery recovery = {
        .workspace = workspace,
        .workspace_bytes = workspace_bytes,
    };
    fdb_tsl_iter_by_time(
        &health_tsdb, (fdb_time_t)from_timestamp, (fdb_time_t)to_timestamp,
        health_recover_record, &recovery);
}

static const r1_health_db_startup_ops health_startup_ops = {
    .context = NULL,
    .control = health_control,
    .initialize = health_initialize,
    .ensure_mutex = health_ensure_mutex,
    .subscribe_time = health_subscribe_time,
    .set_clock = health_set_clock,
    .mark_clock_valid = health_mark_clock_valid,
    .current_clock = health_current_clock,
    .local_day_start = health_local_day_start,
    .allocate = health_allocate,
    .release = health_release,
    .recover = health_recover,
};

static void health_database_startup(void) {
    if (r1_health_db_startup(
            health_schema_bytes, &health_startup_ops, &health_crash_record,
            &health_activity, &health_heart_rate, &health_heart_rate_accumulator,
            &health_spo2, &health_hrv,
            &health_startup_result) != R1_OK ||
        health_startup_result.action != R1_HEALTH_DB_STARTUP_COMPLETED) {
        databases_record_error((uint32_t)NRF_ERROR_INTERNAL);
        return;
    }
    health_ready = true;
}

static void sleep_database_bind(r1_flash *flash) {
    /* Recovered bind at stock 0x0005B0F8: fal_partition_find("sleep.db")
     * (the evidence-pinned string at 0x0005B18C) plus the device lookup,
     * then the journal is bound over the partition base. */
    const struct fal_partition *partition = fal_partition_find("sleep.db");
    if (partition == NULL || partition->offset < 0 ||
        partition->len < R1_SLEEP_DB_BYTES) {
        databases_record_error((uint32_t)NRF_ERROR_NOT_FOUND);
        return;
    }
    if (r1_sleep_db_initialize(
            &sleep_db, *flash, (uint32_t)partition->offset) != R1_OK) {
        databases_record_error((uint32_t)NRF_ERROR_INTERNAL);
        return;
    }
    sleep_ready = true;
}

static void databases_apply_reg1_persist(void) {
    const bool enabled = reg1_persist_enabled;
    reg1_persist_pending = false;
    uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
    size_t length = 0u;
    if (r1_kv_store_get(
            &kv_store, R1_KV_DEV_INFO, dev_info, sizeof dev_info,
            &length) != R1_OK ||
        r1_system_settings_store_reg1(dev_info, length, enabled) != R1_OK ||
        r1_kv_store_set(
            &kv_store, R1_KV_DEV_INFO, dev_info, length) != R1_OK ||
        r1_kv_store_commit(&kv_store) != R1_OK) {
        databases_record_error((uint32_t)NRF_ERROR_INTERNAL);
        return;
    }
    reg1_enabled = enabled;
}

static void databases_worker(void *context) {
    (void)context;
    r1_flash *flash = openr1_storage_flash();
    if (flash == NULL) {
        databases_record_error((uint32_t)NRF_ERROR_INVALID_STATE);
        return;
    }
    /* Recovered order from the stock startup task at 0x000926DC: the health
     * database startup (0x00070030) runs before the sleep.db bind
     * (0x0008DD8C -> 0x0005B0F8).  A failed health startup does not delete
     * or degrade the sleep journal bind. */
    health_database_startup();
    sleep_database_bind(flash);
    for (;;) {
        (void)osThreadFlagsWait(
            OPENR1_DATABASES_PERSIST_REG1_FLAG |
                OPENR1_DATABASES_NV_RECOVERY_FLAG |
                OPENR1_DATABASES_REMOVE_RING_FLAG,
            osFlagsWaitAny, osWaitForever);
        if (reg1_persist_pending) {
            databases_apply_reg1_persist();
        }
        openr1_nv_recovery_request request;
        while (nv_recovery_queue != NULL &&
               osMessageQueueGet(
                   nv_recovery_queue, &request, NULL, 0u) == osOK) {
            r1_nv_recovery_result result;
            const r1_error error = r1_nv_recovery_store_merge_commit(
                &kv_store, request.body, sizeof request.body,
                request.expected_crc, &result);
            if (error != R1_OK) {
                databases_record_error((uint32_t)NRF_ERROR_INTERNAL);
            } else if (result.changed_records != 0u) {
                /* All calibration/identity consumers restart from the new
                 * committed generation. */
                NVIC_SystemReset();
            }
        }
        if (remove_ring_pending) {
            const r1_error error =
                r1_remove_ring_metadata_commit(&kv_store);
            if (error != R1_OK) {
                databases_record_error((uint32_t)NRF_ERROR_INTERNAL);
            }
            remove_ring_pending = false;
        }
    }
}

ret_code_t openr1_databases_initialize(void) {
    static const osThreadAttr_t attributes = {
        .name = "storage",
        .cb_mem = &databases_control_block,
        .cb_size = sizeof databases_control_block,
        .stack_mem = databases_stack,
        .stack_size = sizeof databases_stack,
        .priority = osPriorityLow,
    };

    if (kv_ready) {
        return NRF_SUCCESS;
    }
    /* Restore the bus power-on state (zero-filled BSS in stock) before the
     * storage worker subscribes the health time-listener slots. */
    r1_event_bus_reset(&event_bus);
    /* Bind the per-window queue sink and consumer thread.  Fail-explicit:
     * a bind failure is recorded and the sink stays unbound, so publish
     * keeps returning R1_ERROR_UNSUPPORTED; the databases below are
     * independent of the bus and still initialize. */
    {
        const ret_code_t bus_error = openr1_event_bus_bind(&event_bus);
        if (bus_error != NRF_SUCCESS) {
            databases_record_error(bus_error);
        }
    }
    r1_flash *flash = openr1_storage_flash();
    if (flash == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    /* kv.bin occupies the first two pages of device_flash; the portable
     * initializer only reads flash, so it may run on this (SoftDevice event)
     * thread, mirroring the stock device-init chain placement. */
    const struct fal_partition *kv_partition = fal_partition_find("kv.bin");
    if (kv_partition == NULL || kv_partition->offset != 0 ||
        kv_partition->len < R1_KV_PARTITION_BYTES) {
        return NRF_ERROR_INVALID_ADDR;
    }
    if (r1_kv_store_initialize(&kv_store, *flash) != R1_OK) {
        return NRF_ERROR_INTERNAL;
    }
    kv_ready = true;

    /* Load the persisted normalized REG1 flag (kv dev_info byte 24 bit 1).
     * Read-only, so it may run on this SoftDevice event thread. */
    {
        uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
        size_t dev_info_length = 0u;
        if (r1_kv_store_get(
                &kv_store, R1_KV_DEV_INFO, dev_info, sizeof dev_info,
                &dev_info_length) != R1_OK) {
            kv_ready = false;
            return NRF_ERROR_INTERNAL;
        }
        reg1_enabled =
            r1_system_settings_reg1_enabled(dev_info, dev_info_length);
    }

    health_ensure_mutex(NULL);
    if (health_mutex == NULL) {
        kv_ready = false;
        return NRF_ERROR_NO_MEM;
    }
    nv_recovery_queue = osMessageQueueNew(
        OPENR1_DATABASES_NV_RECOVERY_QUEUE_DEPTH,
        sizeof(openr1_nv_recovery_request), NULL);
    if (nv_recovery_queue == NULL) {
        kv_ready = false;
        return NRF_ERROR_NO_MEM;
    }
    databases_worker_thread = osThreadNew(databases_worker, NULL, &attributes);
    if (databases_worker_thread == NULL) {
        kv_ready = false;
        return NRF_ERROR_NO_MEM;
    }
    return NRF_SUCCESS;
}

bool openr1_databases_kv_ready(void) {
    return kv_ready;
}

bool openr1_databases_reg1_enabled(void) {
    return reg1_enabled;
}

ret_code_t openr1_databases_persist_reg1(bool enabled) {
    if (!kv_ready || databases_worker_thread == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    reg1_persist_enabled = enabled;
    reg1_persist_pending = true;
    const uint32_t flags = osThreadFlagsSet(
        databases_worker_thread, OPENR1_DATABASES_PERSIST_REG1_FLAG);
    if ((flags & (uint32_t)osFlagsError) != 0u) {
        reg1_persist_pending = false;
        return NRF_ERROR_INVALID_STATE;
    }
    return NRF_SUCCESS;
}

ret_code_t openr1_databases_queue_nv_recovery(
    const uint8_t body[R1_NV_RECOVERY_BODY_BYTES], uint16_t expected_crc) {
    if (body == NULL) {
        return NRF_ERROR_NULL;
    }
    if (!kv_ready || databases_worker_thread == NULL ||
        nv_recovery_queue == NULL || expected_crc == 0u) {
        return NRF_ERROR_INVALID_STATE;
    }
    openr1_nv_recovery_request request = {
        .expected_crc = expected_crc,
    };
    memcpy(request.body, body, sizeof request.body);
    if (osMessageQueuePut(nv_recovery_queue, &request, 0u, 0u) != osOK) {
        return NRF_ERROR_NO_MEM;
    }
    const uint32_t flags = osThreadFlagsSet(
        databases_worker_thread, OPENR1_DATABASES_NV_RECOVERY_FLAG);
    return (flags & (uint32_t)osFlagsError) == 0u
        ? NRF_SUCCESS : NRF_ERROR_INVALID_STATE;
}

ret_code_t openr1_databases_queue_remove_ring(void) {
    if (!kv_ready || databases_worker_thread == NULL ||
        remove_ring_pending) {
        return NRF_ERROR_INVALID_STATE;
    }
    remove_ring_pending = true;
    const uint32_t flags = osThreadFlagsSet(
        databases_worker_thread, OPENR1_DATABASES_REMOVE_RING_FLAG);
    if ((flags & (uint32_t)osFlagsError) != 0u) {
        remove_ring_pending = false;
        return NRF_ERROR_INVALID_STATE;
    }
    return NRF_SUCCESS;
}

bool openr1_databases_health_ready(void) {
    return health_ready;
}

bool openr1_databases_sleep_ready(void) {
    return sleep_ready;
}

uint32_t openr1_databases_last_error(void) {
    return databases_error;
}

const r1_health_db_startup_result *openr1_databases_health_startup(void) {
    return &health_startup_result;
}

r1_kv_store *openr1_databases_kv_store(void) {
    return kv_ready ? &kv_store : NULL;
}

/* The platform private event bus.  Always valid storage; publishes return
 * R1_ERROR_UNSUPPORTED until openr1_event_bus_bind succeeded during
 * openr1_databases_initialize. */
r1_event_bus *openr1_databases_event_bus(void) {
    return &event_bus;
}

r1_sleep_db *openr1_databases_sleep_db(void) {
    return sleep_ready ? &sleep_db : NULL;
}

void *openr1_databases_health_handle(void) {
    return health_ready ? r1_health_db_provider_handle(&health_tsdb) : NULL;
}
