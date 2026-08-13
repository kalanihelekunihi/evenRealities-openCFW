/* Clean-room reconstruction of the stock service_kvdb_time.c object. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t reserved0[3];
    uint32_t timestamp;
    int8_t timezone;
    uint8_t reserved1;
    uint16_t crc16;
} open_cfw_kvdb_time_record;

_Static_assert(sizeof(open_cfw_kvdb_time_record) == 12,
    "stock time record must remain twelve bytes");
_Static_assert(offsetof(open_cfw_kvdb_time_record, timestamp) == 4,
    "stock timestamp must remain at offset four");
_Static_assert(offsetof(open_cfw_kvdb_time_record, timezone) == 8,
    "stock timezone must remain at offset eight");
_Static_assert(offsetof(open_cfw_kvdb_time_record, crc16) == 10,
    "stock time CRC must remain at offset ten");

#ifndef OPEN_CFW_KVDB_TIME_RECORD_ADDRESS
#define OPEN_CFW_KVDB_TIME_RECORD_ADDRESS 0x2000380cu
#endif
#ifndef OPEN_CFW_KVDB_TIME_KEY
#define OPEN_CFW_KVDB_TIME_KEY "kvTime"
#endif
#ifndef OPEN_CFW_KVDB_TIME_CRC16
uint16_t open_cfw_kvdb_time_crc16(
    const uint8_t *data, uint32_t length, const uint16_t *seed
);
#define OPEN_CFW_KVDB_TIME_CRC16(data, length, seed) \
    open_cfw_kvdb_time_crc16((data), (length), (seed))
#endif
#ifndef OPEN_CFW_KVDB_TIME_READ
int open_cfw_kvdb_time_db_read(const char *key, void *value, uint16_t length);
#define OPEN_CFW_KVDB_TIME_READ(key, value, length) \
    open_cfw_kvdb_time_db_read((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_TIME_WRITE
int open_cfw_kvdb_time_db_write(
    const char *key, const void *value, uint16_t length
);
#define OPEN_CFW_KVDB_TIME_WRITE(key, value, length) \
    open_cfw_kvdb_time_db_write((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_TIME_DIAGNOSTIC
#define OPEN_CFW_KVDB_TIME_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_KVDB_TIME_RECORD \
    ((volatile open_cfw_kvdb_time_record *)(uintptr_t) \
        OPEN_CFW_KVDB_TIME_RECORD_ADDRESS)

void open_cfw_kvdb_write_time(uint32_t timestamp, int8_t timezone);

int open_cfw_kvdb_time_default_initialize(void)
{
    volatile open_cfw_kvdb_time_record *record = OPEN_CFW_KVDB_TIME_RECORD;

    record->crc16 = OPEN_CFW_KVDB_TIME_CRC16(
        (const uint8_t *)(uintptr_t)record, 10u, NULL
    );
    return 0;
}

int open_cfw_kvdb_time_load_and_migrate(void)
{
    open_cfw_kvdb_time_record stored;
    volatile open_cfw_kvdb_time_record *record = OPEN_CFW_KVDB_TIME_RECORD;
    int result = OPEN_CFW_KVDB_TIME_READ(
        OPEN_CFW_KVDB_TIME_KEY, &stored, sizeof(stored)
    );

    OPEN_CFW_KVDB_TIME_DIAGNOSTIC();
    if (result >= 1) {
        if (stored.crc16 != record->crc16 && stored.version < 3u) {
            open_cfw_kvdb_write_time(record->timestamp, record->timezone);
        }
    } else {
        open_cfw_kvdb_write_time(record->timestamp, record->timezone);
    }
    return 0;
}

void open_cfw_kvdb_write_time(uint32_t timestamp, int8_t timezone)
{
    volatile open_cfw_kvdb_time_record *record = OPEN_CFW_KVDB_TIME_RECORD;

    record->timezone = timezone;
    record->timestamp = timestamp;
    record->version = 3u;
    record->crc16 = OPEN_CFW_KVDB_TIME_CRC16(
        (const uint8_t *)(uintptr_t)record, 10u, NULL
    );
    OPEN_CFW_KVDB_TIME_DIAGNOSTIC();
    (void)OPEN_CFW_KVDB_TIME_WRITE(
        OPEN_CFW_KVDB_TIME_KEY,
        (const void *)(uintptr_t)record,
        sizeof(*record)
    );
}
