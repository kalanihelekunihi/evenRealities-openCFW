#include "openr1/r1_sleep_db.h"

#include "openr1/r1_crc.h"

static uint16_t read_u16(const uint8_t *input) {
    return (uint16_t)((uint16_t)input[0] | ((uint16_t)input[1] << 8u));
}

static uint32_t read_u32(const uint8_t *input) {
    return (uint32_t)input[0] | ((uint32_t)input[1] << 8u)
        | ((uint32_t)input[2] << 16u) | ((uint32_t)input[3] << 24u);
}

static void write_u16(uint8_t *output, uint16_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
}

static void write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static void fill(uint8_t *output, uint8_t value, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        output[index] = value;
    }
}

static bool all_erased(const uint8_t *bytes, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        if (bytes[index] != UINT8_MAX) {
            return false;
        }
    }
    return true;
}

static r1_error db_read(const r1_sleep_db *database, uint32_t relative,
                        uint8_t *output, size_t length) {
    return r1_flash_read(&database->flash, database->base + relative, output, length);
}

static r1_error db_program(const r1_sleep_db *database, uint32_t relative,
                           const uint8_t *input, size_t length) {
    return r1_flash_program(&database->flash, database->base + relative, input, length);
}

static r1_error db_range_erased(const r1_sleep_db *database, uint32_t relative,
                                size_t length, bool *erased) {
    uint8_t chunk[64u];
    if (erased == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *erased = true;
    while (length > 0u) {
        const size_t take = length < sizeof chunk ? length : sizeof chunk;
        const r1_error error = db_read(database, relative, chunk, take);
        if (error != R1_OK) {
            return error;
        }
        if (!all_erased(chunk, take)) {
            *erased = false;
            return R1_OK;
        }
        relative += (uint32_t)take;
        length -= take;
    }
    return R1_OK;
}

static r1_error discard_torn_sector(r1_sleep_db *database, size_t sector) {
    const r1_error error = r1_flash_erase(
        &database->flash,
        database->base + (uint32_t)sector * R1_FLASH_PAGE_BYTES,
        R1_FLASH_PAGE_BYTES);
    return error == R1_OK ? R1_ERROR_CAPACITY : error;
}

r1_error r1_sleep_db_initialize(r1_sleep_db *database, r1_flash flash, uint32_t base) {
    if (database == NULL || flash.read == NULL || flash.program == NULL || flash.erase == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (base > flash.size || R1_SLEEP_DB_BYTES > flash.size - base) {
        return R1_ERROR_LENGTH;
    }
    database->flash = flash;
    database->base = base;
    return R1_OK;
}

static r1_error read_sector_header(const r1_sleep_db *database, size_t sector,
                                   uint8_t header[R1_SLEEP_DB_SECTOR_HEADER_BYTES]) {
    return db_read(database, (uint32_t)sector * R1_FLASH_PAGE_BYTES,
                   header, R1_SLEEP_DB_SECTOR_HEADER_BYTES);
}

static bool sector_writable(const uint8_t *header) {
    const uint32_t word0 = read_u32(header);
    const uint32_t word1 = read_u32(header + 4u);
    return all_erased(header, R1_SLEEP_DB_SECTOR_HEADER_BYTES) ||
        (word0 == R1_SLEEP_DB_CLOSE_WORD0 &&
         word1 != R1_SLEEP_DB_CLOSE_WORD1);
}

static r1_error find_writable(const r1_sleep_db *database, size_t *sector) {
    uint8_t header[R1_SLEEP_DB_SECTOR_HEADER_BYTES];
    for (size_t index = 0u; index < R1_SLEEP_DB_SECTORS; ++index) {
        r1_error error = read_sector_header(database, index, header);
        if (error != R1_OK) {
            return error;
        }
        if (sector_writable(header)) {
            *sector = index;
            return R1_OK;
        }
    }
    return R1_ERROR_CAPACITY;
}

static uint32_t next_close_sequence(const r1_sleep_db *database) {
    uint32_t minimum = UINT32_MAX;
    uint8_t header[R1_SLEEP_DB_SECTOR_HEADER_BYTES];
    for (size_t index = 0u; index < R1_SLEEP_DB_SECTORS; ++index) {
        if (read_sector_header(database, index, header) != R1_OK) {
            continue;
        }
        const uint32_t sequence = read_u32(header + 8u);
        if (sequence != UINT32_MAX && sequence < minimum) {
            minimum = sequence;
        }
    }
    return minimum == UINT32_MAX ? 1u : minimum + 1u;
}

static r1_error close_sector(const r1_sleep_db *database, size_t sector) {
    uint8_t header[R1_SLEEP_DB_SECTOR_HEADER_BYTES];
    write_u32(header, R1_SLEEP_DB_CLOSE_WORD0);
    write_u32(header + 4u, R1_SLEEP_DB_CLOSE_WORD1);
    write_u32(header + 8u, next_close_sequence(database));
    write_u32(header + 12u, 0u);
    return db_program(database, (uint32_t)sector * R1_FLASH_PAGE_BYTES,
                      header, sizeof header);
}

static r1_error rollover(r1_sleep_db *database, size_t *sector) {
    uint32_t minimum = UINT32_MAX;
    size_t selected = 0u;
    uint8_t header[R1_SLEEP_DB_SECTOR_HEADER_BYTES];
    for (size_t index = 0u; index < R1_SLEEP_DB_SECTORS; ++index) {
        r1_error error = read_sector_header(database, index, header);
        if (error != R1_OK) {
            return error;
        }
        const uint32_t sequence = read_u32(header + 8u);
        if (sequence < minimum) {
            minimum = sequence;
            selected = index;
        }
    }
    r1_error error = r1_flash_erase(&database->flash,
                                    database->base + (uint32_t)selected * R1_FLASH_PAGE_BYTES,
                                    R1_FLASH_PAGE_BYTES);
    if (error == R1_OK) {
        *sector = selected;
    }
    return error;
}

static r1_error write_record(r1_sleep_db *database, size_t sector,
                             const uint8_t *body, size_t length,
                             uint32_t *written_header_offset) {
    const size_t aligned = (length + 3u) & ~(size_t)3u;
    uint8_t header[R1_SLEEP_DB_RECORD_HEADER_BYTES];
    uint8_t sector_header[R1_SLEEP_DB_SECTOR_HEADER_BYTES];
    uint16_t body_offset = R1_SLEEP_DB_BODY_START;
    size_t vacant = R1_SLEEP_DB_RECORDS_PER_SECTOR;
    const uint32_t sector_base = (uint32_t)sector * R1_FLASH_PAGE_BYTES;
    r1_error error = db_read(
        database, sector_base, sector_header, sizeof sector_header);
    if (error != R1_OK) {
        return error;
    }
    const bool blank_sector_header = all_erased(
        sector_header, sizeof sector_header);
    for (size_t slot = 0u; slot < R1_SLEEP_DB_RECORDS_PER_SECTOR; ++slot) {
        const uint32_t offset = sector_base + R1_SLEEP_DB_SECTOR_HEADER_BYTES
            + (uint32_t)slot * R1_SLEEP_DB_RECORD_HEADER_BYTES;
        error = db_read(database, offset, header, sizeof header);
        if (error != R1_OK) {
            return error;
        }
        const uint16_t state = read_u16(header + 4u);
        const bool erased = all_erased(header, sizeof header);
        const bool legacy = state == UINT16_MAX && !erased;
        const bool reserved = state == R1_SLEEP_DB_RECORD_RESERVED;
        const bool committed = state == R1_SLEEP_DB_RECORD_COMMITTED;
        if (erased) {
            const uint32_t tail_start = slot == 0u
                ? sector_base + R1_SLEEP_DB_SECTOR_HEADER_BYTES
                : offset + R1_SLEEP_DB_RECORD_HEADER_BYTES;
            const uint32_t tail_limit = slot == 0u
                ? sector_base + R1_FLASH_PAGE_BYTES
                : sector_base + R1_SLEEP_DB_BODY_START;
            bool tail_erased = true;
            if (blank_sector_header && tail_start < tail_limit) {
                error = db_range_erased(
                    database, tail_start, tail_limit - tail_start,
                    &tail_erased);
                if (error != R1_OK) {
                    return error;
                }
            }
            if (!tail_erased) {
                return discard_torn_sector(database, sector);
            }
            vacant = slot;
            break;
        }
        if (!legacy && !reserved && !committed) {
            if (blank_sector_header) {
                return discard_torn_sector(database, sector);
            }
            const r1_error close_error = close_sector(database, sector);
            return close_error == R1_OK ? R1_ERROR_CAPACITY : close_error;
        }
        const uint16_t previous_offset = read_u16(header + 2u);
        const uint16_t previous_length = read_u16(header);
        if (previous_offset < R1_SLEEP_DB_BODY_START ||
            previous_length == 0u || (previous_length & 3u) != 0u ||
            (uint32_t)previous_offset + previous_length > R1_FLASH_PAGE_BYTES) {
            if (blank_sector_header) {
                return discard_torn_sector(database, sector);
            }
            const r1_error close_error = close_sector(database, sector);
            return close_error == R1_OK ? R1_ERROR_CAPACITY : close_error;
        }
        body_offset = (uint16_t)(previous_offset + previous_length);
    }
    if (vacant == R1_SLEEP_DB_RECORDS_PER_SECTOR) {
        const r1_error close_error = close_sector(database, sector);
        return close_error == R1_OK ? R1_ERROR_CAPACITY : close_error;
    }
    if ((size_t)body_offset + aligned > R1_FLASH_PAGE_BYTES) {
        const r1_error close_error = close_sector(database, sector);
        return close_error == R1_OK ? R1_ERROR_CAPACITY : close_error;
    }
    const uint32_t header_offset = sector_base + R1_SLEEP_DB_SECTOR_HEADER_BYTES
        + (uint32_t)vacant * R1_SLEEP_DB_RECORD_HEADER_BYTES;
    fill(header, UINT8_MAX, sizeof header);
    write_u16(header, (uint16_t)aligned);
    write_u16(header + 2u, body_offset);
    write_u16(header + 4u, R1_SLEEP_DB_RECORD_RESERVED);
    write_u16(header + 6u, read_u16(body + 10u));
    error = db_program(database, header_offset, header, 8u);
    if (error != R1_OK) {
        return error;
    }

    uint8_t aligned_body[R1_SLEEP_DB_APPEND_MAX];
    fill(aligned_body, 0u, aligned);
    for (size_t index = 0u; index < length; ++index) {
        aligned_body[index] = body[index];
    }
    error = db_program(database, sector_base + body_offset,
                       aligned_body, aligned);
    if (error != R1_OK) {
        return error;
    }
    fill(header, UINT8_MAX, sizeof header);
    write_u32(header + 8u, read_u32(body + 12u));
    write_u32(header + 12u, read_u32(body + 16u));
    write_u16(header + 18u, r1_crc16_modbus(aligned_body, aligned));
    error = db_program(database, header_offset + 8u, header + 8u, 12u);
    if (error != R1_OK) {
        return error;
    }
    write_u16(header + 4u, R1_SLEEP_DB_RECORD_COMMITTED);
    write_u16(header + 6u, read_u16(body + 10u));
    error = db_program(database, header_offset + 4u, header + 4u, 4u);
    if (error != R1_OK) {
        return error;
    }
    if (written_header_offset != NULL) {
        *written_header_offset = header_offset;
    }
    return vacant == R1_SLEEP_DB_RECORDS_PER_SECTOR - 1u
        ? close_sector(database, sector) : R1_OK;
}

r1_error r1_sleep_db_append_tracked(r1_sleep_db *database,
                                    const uint8_t *body, size_t length,
                                    uint32_t *header_offset) {
    if (database == NULL || body == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length < 20u || length > R1_SLEEP_DB_APPEND_MAX) {
        return R1_ERROR_LENGTH;
    }
    for (size_t attempt = 0u; attempt < 2u; ++attempt) {
        size_t sector = 0u;
        r1_error error = find_writable(database, &sector);
        if (error == R1_ERROR_CAPACITY) {
            error = rollover(database, &sector);
        }
        if (error != R1_OK) {
            return error;
        }
        error = write_record(database, sector, body, length, header_offset);
        if (error == R1_OK) {
            return R1_OK;
        }
    }
    return R1_ERROR_STATE;
}

r1_error r1_sleep_db_append(r1_sleep_db *database, const uint8_t *body, size_t length) {
    return r1_sleep_db_append_tracked(database, body, length, NULL);
}

static r1_error decode_record(const r1_sleep_db *database, size_t sector, size_t slot,
                              r1_sleep_db_record *record, uint8_t *header) {
    const uint32_t offset = (uint32_t)sector * R1_FLASH_PAGE_BYTES
        + R1_SLEEP_DB_SECTOR_HEADER_BYTES
        + (uint32_t)slot * R1_SLEEP_DB_RECORD_HEADER_BYTES;
    r1_error error = db_read(database, offset, header, R1_SLEEP_DB_RECORD_HEADER_BYTES);
    if (error != R1_OK) {
        return error;
    }
    record->header_offset = offset;
    record->aligned_length = read_u16(header);
    record->body_offset = read_u16(header + 2u);
    record->utc_offset_minutes = (int16_t)read_u16(header + 6u);
    record->start_timestamp = read_u32(header + 8u);
    record->end_timestamp = read_u32(header + 12u);
    record->crc16 = read_u16(header + 18u);
    record->allocated = !all_erased(header, R1_SLEEP_DB_RECORD_HEADER_BYTES);
    const uint16_t state = read_u16(header + 4u);
    const bool geometry_valid = record->aligned_length > 0u &&
        (record->aligned_length & 3u) == 0u &&
        record->body_offset >= R1_SLEEP_DB_BODY_START &&
        (uint32_t)record->body_offset + record->aligned_length <=
            R1_FLASH_PAGE_BYTES;
    record->committed = record->allocated &&
        geometry_valid &&
        (state == R1_SLEEP_DB_RECORD_COMMITTED ||
         (state == UINT16_MAX &&
          record->start_timestamp != UINT32_MAX &&
          record->end_timestamp != UINT32_MAX));
    record->synchronized = read_u32(header + 20u) == R1_SLEEP_DB_SYNC_MARKER;
    return R1_OK;
}

r1_error r1_sleep_db_iterate(r1_sleep_db *database, bool skip_synchronized,
                             r1_sleep_db_iterator callback, void *context,
                             size_t *visited) {
    if (database == NULL || callback == NULL || visited == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *visited = 0u;
    uint8_t header[R1_SLEEP_DB_RECORD_HEADER_BYTES];
    uint8_t body[R1_SLEEP_DB_SYNC_READ_MAX];
    for (size_t sector = 0u; sector < R1_SLEEP_DB_SECTORS; ++sector) {
        for (size_t slot = 0u; slot < R1_SLEEP_DB_RECORDS_PER_SECTOR; ++slot) {
            r1_sleep_db_record record;
            r1_error error = decode_record(database, sector, slot, &record, header);
            if (error != R1_OK) {
                return error;
            }
            if (!record.allocated) {
                break;
            }
            if (!record.committed) {
                continue;
            }
            if (record.aligned_length > R1_SLEEP_DB_SYNC_READ_MAX) {
                continue;
            }
            if (record.body_offset < R1_SLEEP_DB_BODY_START ||
                (uint32_t)record.body_offset + record.aligned_length > R1_FLASH_PAGE_BYTES) {
                return R1_ERROR_LENGTH;
            }
            error = db_read(database,
                            (uint32_t)sector * R1_FLASH_PAGE_BYTES + record.body_offset,
                            body, record.aligned_length);
            if (error != R1_OK) {
                return error;
            }
            if (r1_crc16_modbus(body, record.aligned_length) != record.crc16) {
                return R1_ERROR_CHECKSUM;
            }
            if (skip_synchronized && record.synchronized) {
                continue;
            }
            *visited += 1u;
            if (!callback(context, &record, body, record.aligned_length)) {
                return R1_OK;
            }
        }
    }
    return R1_OK;
}

r1_error r1_sleep_db_mark_synchronized(r1_sleep_db *database, uint32_t header_offset,
                                       uint32_t expected_start, uint32_t expected_end) {
    const uint32_t sector_relative = header_offset % R1_FLASH_PAGE_BYTES;
    if (database == NULL || header_offset >= R1_SLEEP_DB_BYTES ||
        sector_relative < R1_SLEEP_DB_SECTOR_HEADER_BYTES ||
        sector_relative >= R1_SLEEP_DB_BODY_START ||
        (sector_relative - R1_SLEEP_DB_SECTOR_HEADER_BYTES) %
            R1_SLEEP_DB_RECORD_HEADER_BYTES != 0u) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t header[R1_SLEEP_DB_RECORD_HEADER_BYTES];
    r1_error error = db_read(database, header_offset, header, sizeof header);
    if (error != R1_OK) {
        return error;
    }
    if (read_u32(header + 8u) != expected_start || read_u32(header + 12u) != expected_end) {
        return R1_ERROR_STATE;
    }
    const uint16_t state = read_u16(header + 4u);
    if (state != UINT16_MAX && state != R1_SLEEP_DB_RECORD_COMMITTED) {
        return R1_ERROR_STATE;
    }
    uint8_t marker[4u];
    write_u32(marker, R1_SLEEP_DB_SYNC_MARKER);
    return db_program(database, header_offset + 20u, marker, sizeof marker);
}

r1_error r1_sleep_db_count(r1_sleep_db *database, size_t *count) {
    if (database == NULL || count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *count = 0u;
    uint8_t header[R1_SLEEP_DB_RECORD_HEADER_BYTES];
    for (size_t sector = 0u; sector < R1_SLEEP_DB_SECTORS; ++sector) {
        for (size_t slot = 0u; slot < R1_SLEEP_DB_RECORDS_PER_SECTOR; ++slot) {
            r1_sleep_db_record record;
            const r1_error error = decode_record(database, sector, slot, &record, header);
            if (error != R1_OK) {
                return error;
            }
            if (!record.allocated) {
                break;
            }
            if (record.committed) {
                *count += 1u;
            }
        }
    }
    return R1_OK;
}

r1_error r1_sleep_db_erase_all(r1_sleep_db *database) {
    if (database == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    for (size_t sector = 0u; sector < R1_SLEEP_DB_SECTORS; ++sector) {
        const r1_error error = r1_flash_erase(
            &database->flash, database->base + (uint32_t)sector * R1_FLASH_PAGE_BYTES,
            R1_FLASH_PAGE_BYTES);
        if (error != R1_OK) {
            return error;
        }
    }
    return R1_OK;
}
