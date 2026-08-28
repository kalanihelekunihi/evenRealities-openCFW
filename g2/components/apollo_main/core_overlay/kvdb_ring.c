/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the stock service_kvdb_ring.c object. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t mac[6];
    uint8_t name[14];
    uint8_t reserved;
    uint16_t crc16;
} open_cfw_kvdb_ring_record;

_Static_assert(sizeof(open_cfw_kvdb_ring_record) == 24,
    "stock ring record must remain twenty-four bytes");
_Static_assert(offsetof(open_cfw_kvdb_ring_record, mac) == 1,
    "stock ring MAC must remain at offset one");
_Static_assert(offsetof(open_cfw_kvdb_ring_record, name) == 7,
    "stock ring name must remain at offset seven");
_Static_assert(offsetof(open_cfw_kvdb_ring_record, reserved) == 21,
    "stock ring reserved byte must remain at offset twenty-one");
_Static_assert(offsetof(open_cfw_kvdb_ring_record, crc16) == 22,
    "stock ring CRC must remain at offset twenty-two");

#ifndef OPEN_CFW_KVDB_RING_RECORD_ADDRESS
#define OPEN_CFW_KVDB_RING_RECORD_ADDRESS 0x200037c8u
#endif
#ifndef OPEN_CFW_KVDB_RING_KEY
#define OPEN_CFW_KVDB_RING_KEY "kvRing"
#endif
#ifndef OPEN_CFW_KVDB_RING_CRC16
uint16_t open_cfw_kvdb_ring_crc16(
    const uint8_t *data, uint32_t length, const uint16_t *seed
);
#define OPEN_CFW_KVDB_RING_CRC16(data, length, seed) \
    open_cfw_kvdb_ring_crc16((data), (length), (seed))
#endif
#ifndef OPEN_CFW_KVDB_RING_READ
int open_cfw_kvdb_ring_db_read(
    const char *key, void *value, uint16_t length
);
#define OPEN_CFW_KVDB_RING_READ(key, value, length) \
    open_cfw_kvdb_ring_db_read((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_RING_WRITE
int open_cfw_kvdb_ring_db_write(
    const char *key, const void *value, uint16_t length
);
#define OPEN_CFW_KVDB_RING_WRITE(key, value, length) \
    open_cfw_kvdb_ring_db_write((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_RING_DIAGNOSTIC
#define OPEN_CFW_KVDB_RING_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_KVDB_RING_RECORD \
    ((volatile open_cfw_kvdb_ring_record *)(uintptr_t) \
        OPEN_CFW_KVDB_RING_RECORD_ADDRESS)

void open_cfw_kvdb_write_ring(const uint8_t *mac, const char *name);

int open_cfw_kvdb_ring_default_initialize(void)
{
    volatile open_cfw_kvdb_ring_record *record = OPEN_CFW_KVDB_RING_RECORD;

    record->crc16 = OPEN_CFW_KVDB_RING_CRC16(
        (const uint8_t *)(uintptr_t)record, 22u, NULL
    );
    return 0;
}

int open_cfw_kvdb_ring_load_and_migrate(void)
{
    open_cfw_kvdb_ring_record stored;
    volatile open_cfw_kvdb_ring_record *record = OPEN_CFW_KVDB_RING_RECORD;
    int result = OPEN_CFW_KVDB_RING_READ(
        OPEN_CFW_KVDB_RING_KEY, &stored, sizeof(stored)
    );

    OPEN_CFW_KVDB_RING_DIAGNOSTIC();
    if (result >= 1) {
        if (stored.crc16 != record->crc16 && stored.version == 0u) {
            open_cfw_kvdb_write_ring(
                (const uint8_t *)(uintptr_t)record->mac,
                (const char *)(uintptr_t)record->name
            );
        }
    } else {
        open_cfw_kvdb_write_ring(
            (const uint8_t *)(uintptr_t)record->mac,
            (const char *)(uintptr_t)record->name
        );
    }
    return 0;
}

void open_cfw_kvdb_write_ring(const uint8_t *mac, const char *name)
{
    volatile open_cfw_kvdb_ring_record *record = OPEN_CFW_KVDB_RING_RECORD;
    uint32_t index;
    uint8_t terminated = 0u;

    if (mac == NULL) {
        for (index = 0; index < sizeof(record->mac); ++index) {
            record->mac[index] = 0xffu;
        }
    } else {
        for (index = 0; index < sizeof(record->mac); ++index) {
            record->mac[index] = mac[index];
        }
    }

    if (name == NULL) {
        for (index = 0; index < sizeof(record->name); ++index) {
            record->name[index] = 0xffu;
        }
    } else {
        for (index = 0; index < sizeof(record->name); ++index) {
            uint8_t value = 0u;
            if (terminated == 0u) {
                value = (uint8_t)name[index];
                if (value == 0u) {
                    terminated = 1u;
                }
            }
            record->name[index] = value;
        }
        record->name[13] = 0u;
    }

    record->version = 1u;
    record->crc16 = OPEN_CFW_KVDB_RING_CRC16(
        (const uint8_t *)(uintptr_t)record, 22u, NULL
    );
    OPEN_CFW_KVDB_RING_DIAGNOSTIC();
    (void)OPEN_CFW_KVDB_RING_WRITE(
        OPEN_CFW_KVDB_RING_KEY,
        (const void *)(uintptr_t)record,
        sizeof(*record)
    );
}
