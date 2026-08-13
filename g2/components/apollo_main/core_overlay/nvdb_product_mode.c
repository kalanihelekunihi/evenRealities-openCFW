/* SPDX-License-Identifier: GPL-3.0-only */
/* Clean-room reconstruction of service_nvdb_product_mode.c. */
#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t mode;
    uint16_t crc16;
} open_cfw_nvdb_product_mode_record;

_Static_assert(sizeof(open_cfw_nvdb_product_mode_record) == 4, "stock ABI");
#ifndef OPEN_CFW_NVDB_PRODUCT_MODE_RECORD_ADDRESS
#define OPEN_CFW_NVDB_PRODUCT_MODE_RECORD_ADDRESS 0x200038F0u
#endif
#ifndef OPEN_CFW_NVDB_PRODUCT_MODE_KEY
#define OPEN_CFW_NVDB_PRODUCT_MODE_KEY ((const char *)0x0078C008u)
#endif
#ifndef OPEN_CFW_NVDB_PRODUCT_MODE_CRC16
uint16_t open_cfw_crc16_ccitt(const uint8_t *, uint32_t, const uint16_t *);
#define OPEN_CFW_NVDB_PRODUCT_MODE_CRC16(p,n,s) open_cfw_crc16_ccitt((p),(n),(s))
#endif
#ifndef OPEN_CFW_NVDB_PRODUCT_MODE_READ
int open_cfw_nvdb_product_mode_db_read(const char *, void *, uint16_t);
#define OPEN_CFW_NVDB_PRODUCT_MODE_READ(k,p,n) open_cfw_nvdb_product_mode_db_read((k),(p),(n))
#endif
#ifndef OPEN_CFW_NVDB_PRODUCT_MODE_WRITE
int open_cfw_nvdb_product_mode_db_write(const char *, const void *, uint16_t);
#define OPEN_CFW_NVDB_PRODUCT_MODE_WRITE(k,p,n) open_cfw_nvdb_product_mode_db_write((k),(p),(n))
#endif
#ifndef OPEN_CFW_NVDB_PRODUCT_MODE_DIAGNOSTIC
#define OPEN_CFW_NVDB_PRODUCT_MODE_DIAGNOSTIC(mode) ((void)(mode))
#endif
#define RECORD ((volatile open_cfw_nvdb_product_mode_record *)(uintptr_t)OPEN_CFW_NVDB_PRODUCT_MODE_RECORD_ADDRESS)

static uint16_t record_crc(const volatile open_cfw_nvdb_product_mode_record *record)
{
    return OPEN_CFW_NVDB_PRODUCT_MODE_CRC16((const uint8_t *)(uintptr_t)record, 2u, (const uint16_t *)0);
}

void open_cfw_nvdb_product_mode_update(uint8_t mode);

__attribute__((used, noinline))
int open_cfw_nvdb_product_mode_default_crc_initialize(void)
{
    RECORD->crc16 = record_crc(RECORD);
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_product_mode_load_and_migrate(void)
{
    open_cfw_nvdb_product_mode_record stored;
    int result = OPEN_CFW_NVDB_PRODUCT_MODE_READ(OPEN_CFW_NVDB_PRODUCT_MODE_KEY, &stored, 4u);
    if (result < 1 || (stored.crc16 != RECORD->crc16 && stored.version == 0u)) {
        open_cfw_nvdb_product_mode_update(RECORD->mode);
    }
    return 0;
}

__attribute__((used, noinline))
void open_cfw_nvdb_product_mode_set(uint8_t mode)
{
    OPEN_CFW_NVDB_PRODUCT_MODE_DIAGNOSTIC(mode);
    RECORD->mode = mode;
}

__attribute__((used, noinline))
uint8_t open_cfw_nvdb_product_mode_get(void) { return RECORD->mode; }

__attribute__((used, noinline))
void open_cfw_nvdb_product_mode_update(uint8_t mode)
{
    open_cfw_nvdb_product_mode_set(mode);
    RECORD->version = 1u;
    RECORD->crc16 = record_crc(RECORD);
    (void)OPEN_CFW_NVDB_PRODUCT_MODE_WRITE(OPEN_CFW_NVDB_PRODUCT_MODE_KEY, (const void *)(uintptr_t)RECORD, 4u);
}

__attribute__((used, noinline))
uint8_t open_cfw_nvdb_product_mode_read(void)
{
    (void)OPEN_CFW_NVDB_PRODUCT_MODE_READ(OPEN_CFW_NVDB_PRODUCT_MODE_KEY, (void *)(uintptr_t)RECORD, 4u);
    return RECORD->mode;
}
