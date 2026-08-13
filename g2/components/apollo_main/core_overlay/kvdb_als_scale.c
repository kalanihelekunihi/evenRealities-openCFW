/* Clean-room reconstruction of the stock service_kvdb_als_scale.c object. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t payload[7];
    uint16_t crc16;
    uint8_t reserved[2];
} open_cfw_kvdb_als_scale_record;

_Static_assert(sizeof(open_cfw_kvdb_als_scale_record) == 12,
    "stock ALS-scale record must remain 12 bytes");
_Static_assert(offsetof(open_cfw_kvdb_als_scale_record, crc16) == 8,
    "stock ALS-scale CRC must remain at offset eight");

#ifndef OPEN_CFW_KVDB_ALS_SCALE_RECORD_ADDRESS
#define OPEN_CFW_KVDB_ALS_SCALE_RECORD_ADDRESS 0x200037bcu
#endif
#ifndef OPEN_CFW_KVDB_ALS_SCALE_KEY
#define OPEN_CFW_KVDB_ALS_SCALE_KEY "kvAlsScale"
#endif
#ifndef OPEN_CFW_KVDB_ALS_SCALE_CRC16
uint16_t open_cfw_kvdb_als_scale_crc16(
    const uint8_t *data, uint32_t length, const uint16_t *seed
);
#define OPEN_CFW_KVDB_ALS_SCALE_CRC16(data, length, seed) \
    open_cfw_kvdb_als_scale_crc16((data), (length), (seed))
#endif
#ifndef OPEN_CFW_KVDB_ALS_SCALE_READ
int open_cfw_kvdb_als_scale_db_read(const char *key, void *value, uint16_t length);
#define OPEN_CFW_KVDB_ALS_SCALE_READ(key, value, length) \
    open_cfw_kvdb_als_scale_db_read((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_ALS_SCALE_WRITE
int open_cfw_kvdb_als_scale_db_write(
    const char *key, const void *value, uint16_t length
);
#define OPEN_CFW_KVDB_ALS_SCALE_WRITE(key, value, length) \
    open_cfw_kvdb_als_scale_db_write((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_ALS_SCALE_DIAGNOSTIC
#define OPEN_CFW_KVDB_ALS_SCALE_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_KVDB_ALS_SCALE_RECORD \
    ((volatile open_cfw_kvdb_als_scale_record *)(uintptr_t) \
        OPEN_CFW_KVDB_ALS_SCALE_RECORD_ADDRESS)

int open_cfw_kvdb_write_als_scale(const void *value);

int open_cfw_kvdb_als_scale_default_initialize(void)
{
    volatile open_cfw_kvdb_als_scale_record *record =
        OPEN_CFW_KVDB_ALS_SCALE_RECORD;
    record->crc16 = OPEN_CFW_KVDB_ALS_SCALE_CRC16(
        (const uint8_t *)(uintptr_t)record, 8u, NULL
    );
    return 0;
}

int open_cfw_kvdb_als_scale_load_and_migrate(void)
{
    open_cfw_kvdb_als_scale_record stored;
    volatile open_cfw_kvdb_als_scale_record *record =
        OPEN_CFW_KVDB_ALS_SCALE_RECORD;
    int result = OPEN_CFW_KVDB_ALS_SCALE_READ(
        OPEN_CFW_KVDB_ALS_SCALE_KEY, &stored, sizeof(stored)
    );

    OPEN_CFW_KVDB_ALS_SCALE_DIAGNOSTIC();
    if (result >= 1) {
        if (stored.crc16 != record->crc16 && stored.version < 1u) {
            (void)open_cfw_kvdb_write_als_scale((const void *)(uintptr_t)record);
        }
    } else {
        (void)open_cfw_kvdb_write_als_scale((const void *)(uintptr_t)record);
    }
    return 0;
}

int open_cfw_kvdb_write_als_scale(const void *value)
{
    const uint8_t *source = (const uint8_t *)value;
    volatile open_cfw_kvdb_als_scale_record *record =
        OPEN_CFW_KVDB_ALS_SCALE_RECORD;
    uint8_t *destination = (uint8_t *)(uintptr_t)record;
    uint32_t index;
    int result;

    for (index = 0; index < sizeof(*record); ++index) {
        destination[index] = source[index];
    }
    record->version = 1u;
    record->crc16 = OPEN_CFW_KVDB_ALS_SCALE_CRC16(
        (const uint8_t *)(uintptr_t)record, 8u, NULL
    );
    result = OPEN_CFW_KVDB_ALS_SCALE_WRITE(
        OPEN_CFW_KVDB_ALS_SCALE_KEY,
        (const void *)(uintptr_t)record,
        sizeof(*record)
    );
    if (result != 0) {
        OPEN_CFW_KVDB_ALS_SCALE_DIAGNOSTIC();
    }
    return 0;
}
