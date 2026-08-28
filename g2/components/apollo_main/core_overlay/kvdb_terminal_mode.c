/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the stock service_kvdb_terminal_mode.c object. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t mode;
    uint16_t crc16;
} open_cfw_kvdb_terminal_mode_record;

_Static_assert(sizeof(open_cfw_kvdb_terminal_mode_record) == 4,
    "stock terminal-mode record must remain four bytes");
_Static_assert(offsetof(open_cfw_kvdb_terminal_mode_record, crc16) == 2,
    "stock terminal-mode CRC must remain at offset two");

#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_RECORD_ADDRESS
#define OPEN_CFW_KVDB_TERMINAL_MODE_RECORD_ADDRESS 0x20003808u
#endif
#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_KEY
#define OPEN_CFW_KVDB_TERMINAL_MODE_KEY "kvTerminalMode"
#endif
#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_CRC16
uint16_t open_cfw_kvdb_terminal_mode_crc16(
    const uint8_t *data, uint32_t length, const uint16_t *seed
);
#define OPEN_CFW_KVDB_TERMINAL_MODE_CRC16(data, length, seed) \
    open_cfw_kvdb_terminal_mode_crc16((data), (length), (seed))
#endif
#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_READ
int open_cfw_kvdb_terminal_mode_db_read(
    const char *key, void *value, uint16_t length
);
#define OPEN_CFW_KVDB_TERMINAL_MODE_READ(key, value, length) \
    open_cfw_kvdb_terminal_mode_db_read((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_WRITE
int open_cfw_kvdb_terminal_mode_db_write(
    const char *key, const void *value, uint16_t length
);
#define OPEN_CFW_KVDB_TERMINAL_MODE_WRITE(key, value, length) \
    open_cfw_kvdb_terminal_mode_db_write((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_DIAGNOSTIC
#define OPEN_CFW_KVDB_TERMINAL_MODE_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_KVDB_TERMINAL_MODE_RECORD \
    ((volatile open_cfw_kvdb_terminal_mode_record *)(uintptr_t) \
        OPEN_CFW_KVDB_TERMINAL_MODE_RECORD_ADDRESS)

int open_cfw_kvdb_write_terminal_mode(const void *value);

int open_cfw_kvdb_terminal_mode_default_initialize(void)
{
    volatile open_cfw_kvdb_terminal_mode_record *record =
        OPEN_CFW_KVDB_TERMINAL_MODE_RECORD;

    record->crc16 = OPEN_CFW_KVDB_TERMINAL_MODE_CRC16(
        (const uint8_t *)(uintptr_t)record, 2u, NULL
    );
    return 0;
}

int open_cfw_kvdb_terminal_mode_load_and_migrate(void)
{
    open_cfw_kvdb_terminal_mode_record stored;
    volatile open_cfw_kvdb_terminal_mode_record *record =
        OPEN_CFW_KVDB_TERMINAL_MODE_RECORD;
    int result = OPEN_CFW_KVDB_TERMINAL_MODE_READ(
        OPEN_CFW_KVDB_TERMINAL_MODE_KEY, &stored, sizeof(stored)
    );

    OPEN_CFW_KVDB_TERMINAL_MODE_DIAGNOSTIC();
    if (result >= 1) {
        if (stored.crc16 != record->crc16 && stored.version < 1u) {
            (void)open_cfw_kvdb_write_terminal_mode(
                (const void *)(uintptr_t)record
            );
        }
    } else {
        (void)open_cfw_kvdb_write_terminal_mode(
            (const void *)(uintptr_t)record
        );
    }
    return 0;
}

int open_cfw_kvdb_write_terminal_mode(const void *value)
{
    const open_cfw_kvdb_terminal_mode_record *source =
        (const open_cfw_kvdb_terminal_mode_record *)value;
    volatile open_cfw_kvdb_terminal_mode_record *record =
        OPEN_CFW_KVDB_TERMINAL_MODE_RECORD;
    int result;

    *(volatile uint32_t *)(uintptr_t)record =
        *(const uint32_t *)(const void *)source;
    record->version = 1u;
    record->crc16 = OPEN_CFW_KVDB_TERMINAL_MODE_CRC16(
        (const uint8_t *)(uintptr_t)record, 2u, NULL
    );
    result = OPEN_CFW_KVDB_TERMINAL_MODE_WRITE(
        OPEN_CFW_KVDB_TERMINAL_MODE_KEY,
        (const void *)(uintptr_t)record,
        sizeof(*record)
    );
    if (result != 0) {
        OPEN_CFW_KVDB_TERMINAL_MODE_DIAGNOSTIC();
    }
    return 0;
}
