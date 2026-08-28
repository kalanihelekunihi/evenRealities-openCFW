/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room behavioral reconstruction of the three-function G2 NVDB
 * advertising-magic helper immediately preceding service_nvdb_mac.c.
 */

#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t magic;
    uint16_t crc16;
} open_cfw_nvdb_adv_magic_record;

_Static_assert(sizeof(open_cfw_nvdb_adv_magic_record) == 4,
    "stock advertising-magic record must remain four bytes");

#ifndef OPEN_CFW_NVDB_ADV_MAGIC_RECORD_ADDRESS
#define OPEN_CFW_NVDB_ADV_MAGIC_RECORD_ADDRESS 0x200038D4u
#endif
#ifndef OPEN_CFW_NVDB_ADV_MAGIC_KEY
#define OPEN_CFW_NVDB_ADV_MAGIC_KEY ((const char *)0x0078BFE4u)
#endif

#ifndef OPEN_CFW_NVDB_ADV_MAGIC_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data,
    uint32_t length,
    const uint16_t *seed
);
#define OPEN_CFW_NVDB_ADV_MAGIC_CRC16(data, length, seed) \
    open_cfw_crc16_ccitt((data), (length), (seed))
#endif

#ifndef OPEN_CFW_NVDB_ADV_MAGIC_READ
int open_cfw_nvdb_adv_magic_db_read(
    const char *key,
    void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_ADV_MAGIC_READ(key, value, length) \
    open_cfw_nvdb_adv_magic_db_read((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_ADV_MAGIC_WRITE
int open_cfw_nvdb_adv_magic_db_write(
    const char *key,
    const void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_ADV_MAGIC_WRITE(key, value, length) \
    open_cfw_nvdb_adv_magic_db_write((key), (value), (length))
#endif

#define OPEN_CFW_NVDB_ADV_MAGIC_RECORD \
    ((volatile open_cfw_nvdb_adv_magic_record *)(uintptr_t) \
        OPEN_CFW_NVDB_ADV_MAGIC_RECORD_ADDRESS)

static uint16_t open_cfw_nvdb_adv_magic_crc(
    const volatile open_cfw_nvdb_adv_magic_record *record
)
{
    return OPEN_CFW_NVDB_ADV_MAGIC_CRC16(
        (const uint8_t *)(uintptr_t)record,
        2u,
        (const uint16_t *)0
    );
}

void open_cfw_nvdb_adv_magic_update(uint8_t magic);

__attribute__((used, noinline))
int open_cfw_nvdb_adv_magic_default_crc_initialize(void)
{
    volatile open_cfw_nvdb_adv_magic_record *record =
        OPEN_CFW_NVDB_ADV_MAGIC_RECORD;

    record->crc16 = open_cfw_nvdb_adv_magic_crc(record);
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_adv_magic_load_and_migrate(void)
{
    open_cfw_nvdb_adv_magic_record stored;
    volatile open_cfw_nvdb_adv_magic_record *record =
        OPEN_CFW_NVDB_ADV_MAGIC_RECORD;
    int result;

    result = OPEN_CFW_NVDB_ADV_MAGIC_READ(
        OPEN_CFW_NVDB_ADV_MAGIC_KEY,
        &stored,
        (uint16_t)sizeof(stored)
    );
    if (result < 1 ||
        (stored.crc16 != record->crc16 && stored.version == 0u)) {
        open_cfw_nvdb_adv_magic_update(record->magic);
    }
    return 0;
}

__attribute__((used, noinline))
void open_cfw_nvdb_adv_magic_update(uint8_t magic)
{
    volatile open_cfw_nvdb_adv_magic_record *record =
        OPEN_CFW_NVDB_ADV_MAGIC_RECORD;

    record->magic = magic;
    record->version = 1u;
    record->crc16 = open_cfw_nvdb_adv_magic_crc(record);
    (void)OPEN_CFW_NVDB_ADV_MAGIC_WRITE(
        OPEN_CFW_NVDB_ADV_MAGIC_KEY,
        (const void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
}

#undef OPEN_CFW_NVDB_ADV_MAGIC_RECORD
