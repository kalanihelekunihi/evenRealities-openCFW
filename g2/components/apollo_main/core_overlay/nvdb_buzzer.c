/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral reconstruction of the five-function G2
 * service_nvdb_buzzer.c object.  The persistent record is twelve bytes:
 * version at +0, frequency at +4, duty at +8, and CRC-16/CCITT-FALSE at
 * +10.  The two reserved regions are deliberately retained in the checksum.
 *
 * This candidate is not production-routed.  Its seams keep the fixed SRAM
 * record, FlashDB wrappers, existing CRC leaf, and optional diagnostics
 * explicit for host qualification and later placement work.
 */

#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t reserved_1[3];
    uint32_t frequency_hz;
    uint8_t duty_percent;
    uint8_t reserved_9;
    uint16_t crc16;
} open_cfw_nvdb_buzzer_record;

_Static_assert(sizeof(open_cfw_nvdb_buzzer_record) == 12,
    "stock buzzer record must remain twelve bytes");

#ifndef OPEN_CFW_NVDB_BUZZER_RECORD_ADDRESS
#define OPEN_CFW_NVDB_BUZZER_RECORD_ADDRESS 0x200038D8u
#endif
#ifndef OPEN_CFW_NVDB_BUZZER_KEY
#define OPEN_CFW_NVDB_BUZZER_KEY ((const char *)0x0078BFFCu)
#endif

#ifndef OPEN_CFW_NVDB_BUZZER_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data,
    uint32_t length,
    const uint16_t *seed
);
#define OPEN_CFW_NVDB_BUZZER_CRC16(data, length, seed) \
    open_cfw_crc16_ccitt((data), (length), (seed))
#endif

#ifndef OPEN_CFW_NVDB_BUZZER_READ
int open_cfw_nvdb_buzzer_db_read(const char *key, void *value, uint16_t length);
#define OPEN_CFW_NVDB_BUZZER_READ(key, value, length) \
    open_cfw_nvdb_buzzer_db_read((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_BUZZER_WRITE
int open_cfw_nvdb_buzzer_db_write(
    const char *key,
    const void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_BUZZER_WRITE(key, value, length) \
    open_cfw_nvdb_buzzer_db_write((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_BUZZER_DIAGNOSTIC
#define OPEN_CFW_NVDB_BUZZER_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_NVDB_BUZZER_RECORD \
    ((volatile open_cfw_nvdb_buzzer_record *)(uintptr_t) \
        OPEN_CFW_NVDB_BUZZER_RECORD_ADDRESS)

static uint16_t open_cfw_nvdb_buzzer_crc(
    const volatile open_cfw_nvdb_buzzer_record *record
)
{
    return OPEN_CFW_NVDB_BUZZER_CRC16(
        (const uint8_t *)(uintptr_t)record,
        10u,
        (const uint16_t *)0
    );
}

void open_cfw_nvdb_buzzer_update(uint32_t frequency_hz, uint8_t duty_percent);

__attribute__((used, noinline))
int open_cfw_nvdb_buzzer_default_crc_initialize(void)
{
    volatile open_cfw_nvdb_buzzer_record *record = OPEN_CFW_NVDB_BUZZER_RECORD;

    record->crc16 = open_cfw_nvdb_buzzer_crc(record);
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_buzzer_load_and_migrate(void)
{
    open_cfw_nvdb_buzzer_record stored;
    volatile open_cfw_nvdb_buzzer_record *record = OPEN_CFW_NVDB_BUZZER_RECORD;
    int result;

    OPEN_CFW_NVDB_BUZZER_DIAGNOSTIC();
    result = OPEN_CFW_NVDB_BUZZER_READ(
        OPEN_CFW_NVDB_BUZZER_KEY,
        &stored,
        (uint16_t)sizeof(stored)
    );
    if (result < 1 ||
        (stored.crc16 != record->crc16 && stored.version < 2u)) {
        open_cfw_nvdb_buzzer_update(
            record->frequency_hz,
            record->duty_percent
        );
    }
    return 0;
}

__attribute__((used, noinline))
uint32_t open_cfw_nvdb_buzzer_frequency_get(void)
{
    return OPEN_CFW_NVDB_BUZZER_RECORD->frequency_hz;
}

__attribute__((used, noinline))
uint8_t open_cfw_nvdb_buzzer_duty_get(void)
{
    return OPEN_CFW_NVDB_BUZZER_RECORD->duty_percent;
}

__attribute__((used, noinline))
void open_cfw_nvdb_buzzer_update(uint32_t frequency_hz, uint8_t duty_percent)
{
    volatile open_cfw_nvdb_buzzer_record *record = OPEN_CFW_NVDB_BUZZER_RECORD;

    record->frequency_hz = frequency_hz;
    record->duty_percent = duty_percent;
    record->version = 2u;
    record->crc16 = open_cfw_nvdb_buzzer_crc(record);
    (void)OPEN_CFW_NVDB_BUZZER_WRITE(
        OPEN_CFW_NVDB_BUZZER_KEY,
        (const void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
}
