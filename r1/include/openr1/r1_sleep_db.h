#ifndef OPENR1_R1_SLEEP_DB_H
#define OPENR1_R1_SLEEP_DB_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_storage.h"

#define R1_SLEEP_DB_BYTES 8192u
#define R1_SLEEP_DB_SECTORS 2u
#define R1_SLEEP_DB_RECORDS_PER_SECTOR 8u
#define R1_SLEEP_DB_SECTOR_HEADER_BYTES 16u
#define R1_SLEEP_DB_RECORD_HEADER_BYTES 24u
#define R1_SLEEP_DB_BODY_START 208u
#define R1_SLEEP_DB_APPEND_MAX 3888u
#define R1_SLEEP_DB_SYNC_READ_MAX 232u
#define R1_SLEEP_DB_CLOSE_WORD0 UINT32_C(0xccffaabb)
#define R1_SLEEP_DB_CLOSE_WORD1 UINT32_C(0x66889977)
#define R1_SLEEP_DB_SYNC_MARKER UINT32_C(0x11223344)
#define R1_SLEEP_DB_RECORD_RESERVED UINT16_C(0xfffe)
#define R1_SLEEP_DB_RECORD_COMMITTED UINT16_C(0xfffc)

typedef struct {
    r1_flash flash;
    uint32_t base;
} r1_sleep_db;

typedef struct {
    uint32_t header_offset;
    uint16_t aligned_length;
    uint16_t body_offset;
    int16_t utc_offset_minutes;
    uint32_t start_timestamp;
    uint32_t end_timestamp;
    uint16_t crc16;
    bool allocated;
    bool committed;
    bool synchronized;
} r1_sleep_db_record;

typedef bool (*r1_sleep_db_iterator)(void *context,
                                     const r1_sleep_db_record *record,
                                     const uint8_t *body, size_t length);

r1_error r1_sleep_db_initialize(r1_sleep_db *database, r1_flash flash, uint32_t base);
r1_error r1_sleep_db_append(r1_sleep_db *database, const uint8_t *body, size_t length);
r1_error r1_sleep_db_append_tracked(r1_sleep_db *database,
                                    const uint8_t *body, size_t length,
                                    uint32_t *header_offset);
r1_error r1_sleep_db_iterate(r1_sleep_db *database, bool skip_synchronized,
                             r1_sleep_db_iterator callback, void *context,
                             size_t *visited);
r1_error r1_sleep_db_mark_synchronized(r1_sleep_db *database, uint32_t header_offset,
                                       uint32_t expected_start, uint32_t expected_end);
r1_error r1_sleep_db_count(r1_sleep_db *database, size_t *count);
r1_error r1_sleep_db_erase_all(r1_sleep_db *database);

#endif
