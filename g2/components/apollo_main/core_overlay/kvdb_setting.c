/*
 * Clean-room behavioral reconstruction of service_kvdb_setting.c in the
 * official G2 image. This candidate is intentionally not production-routed.
 * Payload fields remain opaque; the complete persistence ABI is preserved.
 */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t payload[23];
    uint16_t crc16;
    uint8_t reserved[2];
} open_cfw_kvdb_setting_record;

_Static_assert(sizeof(open_cfw_kvdb_setting_record) == 28,
    "stock setting record must remain 28 bytes");
_Static_assert(offsetof(open_cfw_kvdb_setting_record, crc16) == 24,
    "stock setting CRC must remain at offset 24");

#ifndef OPEN_CFW_KVDB_SETTING_RECORD_ADDRESS
#define OPEN_CFW_KVDB_SETTING_RECORD_ADDRESS 0x200037e0u
#endif
#ifndef OPEN_CFW_KVDB_SETTING_KEY
#define OPEN_CFW_KVDB_SETTING_KEY "kvSetting"
#endif

#ifndef OPEN_CFW_KVDB_SETTING_CRC16
uint16_t open_cfw_kvdb_setting_crc16(
    const uint8_t *data,
    uint32_t length,
    const uint16_t *seed
);
#define OPEN_CFW_KVDB_SETTING_CRC16(data, length, seed) \
    open_cfw_kvdb_setting_crc16((data), (length), (seed))
#endif

#ifndef OPEN_CFW_KVDB_SETTING_READ
int open_cfw_kvdb_setting_db_read(
    const char *key,
    void *value,
    uint16_t length
);
#define OPEN_CFW_KVDB_SETTING_READ(key, value, length) \
    open_cfw_kvdb_setting_db_read((key), (value), (length))
#endif

#ifndef OPEN_CFW_KVDB_SETTING_WRITE
int open_cfw_kvdb_setting_db_write(
    const char *key,
    const void *value,
    uint16_t length
);
#define OPEN_CFW_KVDB_SETTING_WRITE(key, value, length) \
    open_cfw_kvdb_setting_db_write((key), (value), (length))
#endif

#ifndef OPEN_CFW_KVDB_SETTING_DIAGNOSTIC
#define OPEN_CFW_KVDB_SETTING_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_KVDB_SETTING_RECORD \
    ((volatile open_cfw_kvdb_setting_record *)(uintptr_t) \
        OPEN_CFW_KVDB_SETTING_RECORD_ADDRESS)

int open_cfw_kvdb_write_setting(const void *value);

int open_cfw_kvdb_setting_default_initialize(void)
{
    volatile open_cfw_kvdb_setting_record *record = OPEN_CFW_KVDB_SETTING_RECORD;

    record->crc16 = OPEN_CFW_KVDB_SETTING_CRC16(
        (const uint8_t *)(uintptr_t)record,
        24u,
        NULL
    );
    return 0;
}

int open_cfw_kvdb_setting_load_and_migrate(void)
{
    open_cfw_kvdb_setting_record stored;
    volatile open_cfw_kvdb_setting_record *record = OPEN_CFW_KVDB_SETTING_RECORD;
    int result = OPEN_CFW_KVDB_SETTING_READ(
        OPEN_CFW_KVDB_SETTING_KEY,
        &stored,
        sizeof(stored)
    );

    OPEN_CFW_KVDB_SETTING_DIAGNOSTIC();
    if (result >= 1) {
        if (stored.crc16 != record->crc16 && stored.version < 4u) {
            (void)open_cfw_kvdb_write_setting((const void *)(uintptr_t)record);
        }
    } else {
        (void)open_cfw_kvdb_write_setting((const void *)(uintptr_t)record);
    }
    return 0;
}

int open_cfw_kvdb_write_setting(const void *value)
{
    const uint8_t *source = (const uint8_t *)value;
    volatile open_cfw_kvdb_setting_record *record = OPEN_CFW_KVDB_SETTING_RECORD;
    uint8_t *destination = (uint8_t *)(uintptr_t)record;
    uint32_t index;
    int result;

    for (index = 0; index < sizeof(*record); ++index) {
        destination[index] = source[index];
    }
    record->version = 4u;
    record->crc16 = OPEN_CFW_KVDB_SETTING_CRC16(
        (const uint8_t *)(uintptr_t)record,
        24u,
        NULL
    );
    result = OPEN_CFW_KVDB_SETTING_WRITE(
        OPEN_CFW_KVDB_SETTING_KEY,
        (const void *)(uintptr_t)record,
        sizeof(*record)
    );
    if (result != 0) {
        OPEN_CFW_KVDB_SETTING_DIAGNOSTIC();
    }
    return 0;
}
