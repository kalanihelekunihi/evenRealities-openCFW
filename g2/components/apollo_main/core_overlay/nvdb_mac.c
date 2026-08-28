/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room behavioral reconstruction of the three-function G2
 * service_nvdb_mac.c object.  The persistent record is ten bytes: schema
 * version at +0, six-byte BLE address at +1, one reserved byte at +7, and a
 * CRC-16/CCITT-FALSE at +8.
 *
 * The stock default builder derives the address from Apollo510 CHIPID1 then
 * CHIPID0.  It uses canonical reflected CRC-32 for the first four address
 * bytes, CCITT-FALSE for the final two, and forces the most-significant address
 * octet into the static-random range.  Provider seams are explicit because
 * this candidate is qualified but not production-routed.
 */

#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t address[6];
    uint8_t reserved;
    uint16_t crc16;
} open_cfw_nvdb_mac_record;

_Static_assert(sizeof(open_cfw_nvdb_mac_record) == 10,
    "stock MAC record must remain ten bytes");

#ifndef OPEN_CFW_NVDB_MAC_RECORD_ADDRESS
#define OPEN_CFW_NVDB_MAC_RECORD_ADDRESS 0x200038E4u
#endif
#ifndef OPEN_CFW_NVDB_MAC_KEY
#define OPEN_CFW_NVDB_MAC_KEY ((const char *)0x0078E62Cu)
#endif

#ifndef OPEN_CFW_NVDB_MAC_DEVICE_IDS_GET
void open_cfw_nvdb_mac_device_ids_get(uint32_t *chip_id0, uint32_t *chip_id1);
#define OPEN_CFW_NVDB_MAC_DEVICE_IDS_GET(chip_id0, chip_id1) \
    open_cfw_nvdb_mac_device_ids_get((chip_id0), (chip_id1))
#endif

#ifndef OPEN_CFW_NVDB_MAC_CRC32
uint32_t open_cfw_nvdb_mac_crc32(
    const uint8_t *data,
    uint32_t length,
    const uint32_t *seed
);
#define OPEN_CFW_NVDB_MAC_CRC32(data, length, seed) \
    open_cfw_nvdb_mac_crc32((data), (length), (seed))
#endif

#ifndef OPEN_CFW_NVDB_MAC_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data,
    uint32_t length,
    const uint16_t *seed
);
#define OPEN_CFW_NVDB_MAC_CRC16(data, length, seed) \
    open_cfw_crc16_ccitt((data), (length), (seed))
#endif

#ifndef OPEN_CFW_NVDB_MAC_READ
int open_cfw_nvdb_mac_db_read(const char *key, void *value, uint16_t length);
#define OPEN_CFW_NVDB_MAC_READ(key, value, length) \
    open_cfw_nvdb_mac_db_read((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_MAC_WRITE
int open_cfw_nvdb_mac_db_write(
    const char *key,
    const void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_MAC_WRITE(key, value, length) \
    open_cfw_nvdb_mac_db_write((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_MAC_DIAGNOSTIC
#define OPEN_CFW_NVDB_MAC_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_NVDB_MAC_RECORD \
    ((volatile open_cfw_nvdb_mac_record *)(uintptr_t) \
        OPEN_CFW_NVDB_MAC_RECORD_ADDRESS)

static void open_cfw_nvdb_mac_copy(
    volatile uint8_t *destination,
    const uint8_t *source,
    uint32_t length
)
{
    uint32_t index;

    for (index = 0; index < length; ++index) {
        destination[index] = source[index];
    }
}

static uint16_t open_cfw_nvdb_mac_record_crc(
    const volatile open_cfw_nvdb_mac_record *record
)
{
    return OPEN_CFW_NVDB_MAC_CRC16(
        (const uint8_t *)(uintptr_t)record,
        8u,
        (const uint16_t *)0
    );
}

void open_cfw_nvdb_mac_update(const uint8_t address[6]);

__attribute__((used, noinline))
int open_cfw_nvdb_mac_default_initialize(void)
{
    volatile open_cfw_nvdb_mac_record *record = OPEN_CFW_NVDB_MAC_RECORD;
    uint32_t chip_id[2] = {0u, 0u};
    uint32_t serial[2];
    uint32_t fingerprint;
    uint16_t suffix;

    OPEN_CFW_NVDB_MAC_DEVICE_IDS_GET(&chip_id[0], &chip_id[1]);
    serial[0] = chip_id[1];
    serial[1] = chip_id[0];

    fingerprint = OPEN_CFW_NVDB_MAC_CRC32(
        (const uint8_t *)serial,
        8u,
        (const uint32_t *)0
    );
    open_cfw_nvdb_mac_copy(
        &record->address[0],
        (const uint8_t *)&fingerprint,
        4u
    );

    suffix = OPEN_CFW_NVDB_MAC_CRC16(
        (const uint8_t *)serial,
        8u,
        (const uint16_t *)0
    );
    record->address[4] = (uint8_t)(suffix >> 8u);
    record->address[5] = (uint8_t)suffix;
    record->address[5] = (uint8_t)(record->address[5] & 0xFCu);
    record->address[5] = (uint8_t)(record->address[5] | 0xC0u);
    record->crc16 = open_cfw_nvdb_mac_record_crc(record);
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_mac_load_and_migrate(void)
{
    open_cfw_nvdb_mac_record stored;
    volatile open_cfw_nvdb_mac_record *record = OPEN_CFW_NVDB_MAC_RECORD;
    int result;

    OPEN_CFW_NVDB_MAC_DIAGNOSTIC();
    result = OPEN_CFW_NVDB_MAC_READ(
        OPEN_CFW_NVDB_MAC_KEY,
        &stored,
        (uint16_t)sizeof(stored)
    );
    if (result < 1 ||
        (stored.crc16 != record->crc16 && stored.version == 0u)) {
        open_cfw_nvdb_mac_update(
            (const uint8_t *)(uintptr_t)&record->address[0]
        );
    }
    return 0;
}

__attribute__((used, noinline))
void open_cfw_nvdb_mac_update(const uint8_t address[6])
{
    volatile open_cfw_nvdb_mac_record *record = OPEN_CFW_NVDB_MAC_RECORD;

    open_cfw_nvdb_mac_copy(&record->address[0], address, 6u);
    record->version = 1u;
    record->crc16 = open_cfw_nvdb_mac_record_crc(record);
    (void)OPEN_CFW_NVDB_MAC_WRITE(
        OPEN_CFW_NVDB_MAC_KEY,
        (const void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
}

#undef OPEN_CFW_NVDB_MAC_RECORD
