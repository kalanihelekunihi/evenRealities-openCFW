#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "flashdb.h"
#include "openr1/r1_fal_port.h"
#include "openr1/r1_storage.h"

#define TEST_FLASH_BYTES UINT32_C(0x24000)
#define CHECK(expression) do { if (!(expression)) abort(); } while (0)

static fdb_time_t now = 1000;

static uint32_t read_u32(const uint8_t *input) {
    return (uint32_t)input[0] | ((uint32_t)input[1] << 8u) |
        ((uint32_t)input[2] << 16u) | ((uint32_t)input[3] << 24u);
}

static fdb_time_t get_time(void) {
    const fdb_time_t result = now;
    now += 1;
    return result;
}

typedef struct {
    fdb_tsdb_t database;
    size_t count;
    uint8_t expected[128u];
} query_context;

typedef struct {
    size_t count;
    fdb_time_t expected_time;
} reverse_query_context;

static bool query_record(fdb_tsl_t record, void *opaque) {
    query_context *context = opaque;
    uint8_t actual[128u];
    struct fdb_blob blob;
    CHECK(fdb_blob_read((fdb_db_t)context->database,
                        fdb_tsl_to_blob(record,
                                        fdb_blob_make(&blob, actual, sizeof actual))) ==
          sizeof actual);
    for (size_t index = 0u; index < sizeof actual; ++index) {
        CHECK(actual[index] == context->expected[index]);
    }
    context->count += 1u;
    return false;
}

static bool query_record_reverse(fdb_tsl_t record, void *opaque) {
    reverse_query_context *context = opaque;
    CHECK(record->time == context->expected_time);
    context->expected_time -= 1;
    context->count += 1u;
    return false;
}

int main(void) {
    static uint8_t bytes[TEST_FLASH_BYTES];
    r1_memory_flash memory;
    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    r1_flash flash = r1_memory_flash_interface(&memory);
    CHECK(r1_fal_bind(&flash) == R1_OK);
    CHECK(fal_init() == R1_STORAGE_PARTITION_COUNT);

    struct fdb_tsdb database = {0};
    CHECK(fdb_tsdb_init(&database, "health", "health.db", get_time, 128u, NULL) ==
          FDB_NO_ERR);
    CHECK(bytes[UINT32_C(0x02000) + 12u] == 'T');
    CHECK(bytes[UINT32_C(0x02000) + 13u] == 'S');
    CHECK(bytes[UINT32_C(0x02000) + 14u] == 'L');
    CHECK(bytes[UINT32_C(0x02000) + 15u] == '0');

    uint8_t payload[128u];
    for (size_t index = 0u; index < sizeof payload; ++index) {
        payload[index] = (uint8_t)(index * 13u + 5u);
    }
    struct fdb_blob blob;
    CHECK(fdb_tsl_append(&database, fdb_blob_make(&blob, payload, sizeof payload)) ==
          FDB_NO_ERR);
    CHECK(read_u32(bytes + UINT32_C(0x02000) + 80u + 24u) == 128u);
    CHECK(read_u32(bytes + UINT32_C(0x02000) + 80u + 28u) == UINT32_C(0x0f80));
    for (size_t index = 0u; index < sizeof payload; ++index) {
        CHECK(bytes[UINT32_C(0x02000) + UINT32_C(0x0f80) + index] == payload[index]);
    }
    query_context context = {&database, 0u, {0u}};
    for (size_t index = 0u; index < sizeof payload; ++index) {
        context.expected[index] = payload[index];
    }
    fdb_tsl_iter(&database, query_record, &context);
    CHECK(context.count == 1u);
    CHECK(fdb_tsl_query_count(&database, 0, 2000, FDB_TSL_WRITE) == 1u);

    for (size_t index = 1u; index < 26u; ++index) {
        CHECK(fdb_tsl_append(&database, fdb_blob_make(&blob, payload, sizeof payload)) ==
              FDB_NO_ERR);
    }
    CHECK(fdb_tsl_query_count(&database, 0, 2000, FDB_TSL_WRITE) == 26u);
    CHECK(bytes[UINT32_C(0x03000) + 12u] == 'T');
    CHECK(bytes[UINT32_C(0x03000) + 13u] == 'S');
    CHECK(bytes[UINT32_C(0x03000) + 14u] == 'L');
    CHECK(bytes[UINT32_C(0x03000) + 15u] == '0');
    reverse_query_context reverse = {0u, 1025};
    fdb_tsl_iter_by_time(&database, 1025, 1000, query_record_reverse, &reverse);
    CHECK(reverse.count == 26u);
    CHECK(reverse.expected_time == 999);
    CHECK(fdb_tsdb_deinit(&database) == FDB_NO_ERR);
    puts("openR1: upstream FlashDB/FAL storage test passed");
    return 0;
}
