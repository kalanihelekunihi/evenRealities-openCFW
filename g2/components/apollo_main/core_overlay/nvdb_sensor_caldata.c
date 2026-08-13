/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral reconstruction of the eight-function G2
 * service_nvdb_sensor_caldata.c object.  The names of the calibration
 * payloads are intentionally conservative: stock proves their sizes and
 * persistence behavior, but not all higher-level sensor meanings.
 */

#include <stdint.h>

typedef struct {
    uint8_t version;
    uint8_t reserved0[3];
    float vector_a[3];
    float vector_b[3];
    float vector_c[4];
    int32_t fixed_transform[4];
    float scale;
    uint8_t opaque_tail[24];
    uint16_t crc16;
    uint16_t reserved1;
} open_cfw_nvdb_sensor_caldata_record;

typedef struct {
    uint8_t version;
    uint8_t reserved0[3];
    float vector_a[3];
    float vector_b[3];
    float matrix[9];
    uint16_t crc16;
    uint16_t reserved1;
} open_cfw_nvdb_sensor_caldata_ag_record;

_Static_assert(sizeof(open_cfw_nvdb_sensor_caldata_record) == 92,
    "stock nvSCald record must remain 92 bytes");
_Static_assert(sizeof(open_cfw_nvdb_sensor_caldata_ag_record) == 68,
    "stock nvSCaldAG record must remain 68 bytes");

#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD_ADDRESS
#define OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD_ADDRESS 0x200038F4u
#endif
#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD_ADDRESS
#define OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD_ADDRESS 0x20003950u
#endif
#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_KEY
#define OPEN_CFW_NVDB_SENSOR_CALDATA_KEY ((const char *)0x0078E634u)
#endif
#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_AG_KEY
#define OPEN_CFW_NVDB_SENSOR_CALDATA_AG_KEY ((const char *)0x0078C020u)
#endif

#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data,
    uint32_t length,
    const uint16_t *seed
);
#define OPEN_CFW_NVDB_SENSOR_CALDATA_CRC16(data, length, seed) \
    open_cfw_crc16_ccitt((data), (length), (seed))
#endif

#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_READ
int open_cfw_nvdb_sensor_caldata_db_read(
    const char *key,
    void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_SENSOR_CALDATA_READ(key, value, length) \
    open_cfw_nvdb_sensor_caldata_db_read((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_WRITE
int open_cfw_nvdb_sensor_caldata_db_write(
    const char *key,
    const void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_SENSOR_CALDATA_WRITE(key, value, length) \
    open_cfw_nvdb_sensor_caldata_db_write((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_PATTERN_CHECK_ENABLED
int open_cfw_nvdb_sensor_caldata_pattern_check_enabled(void);
#define OPEN_CFW_NVDB_SENSOR_CALDATA_PATTERN_CHECK_ENABLED() \
    open_cfw_nvdb_sensor_caldata_pattern_check_enabled()
#endif

#ifndef OPEN_CFW_NVDB_SENSOR_CALDATA_DIAGNOSTIC
#define OPEN_CFW_NVDB_SENSOR_CALDATA_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD \
    ((volatile open_cfw_nvdb_sensor_caldata_record *)(uintptr_t) \
        OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD_ADDRESS)
#define OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD \
    ((volatile open_cfw_nvdb_sensor_caldata_ag_record *)(uintptr_t) \
        OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD_ADDRESS)

static const float open_cfw_nvdb_sensor_caldata_default_matrix[9] = {
    -0.8190199732780457f, -0.36686399579048157f, 0.4239729940891266f,
    0.4478209912776947f, 0.06740760058164597f, 0.8730469942092896f,
    -0.34925299882888794f, 0.9329609870910645f, 0.11602500081062317f,
};

static void open_cfw_nvdb_sensor_caldata_copy(
    volatile void *destination,
    const volatile void *source,
    uint32_t length
)
{
    volatile uint8_t *out = (volatile uint8_t *)destination;
    const volatile uint8_t *in = (const volatile uint8_t *)source;
    uint32_t index;

    for (index = 0; index < length; ++index) {
        out[index] = in[index];
    }
}

static uint16_t open_cfw_nvdb_sensor_caldata_primary_crc(void)
{
    return OPEN_CFW_NVDB_SENSOR_CALDATA_CRC16(
        (const uint8_t *)(uintptr_t)OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD,
        88u,
        (const uint16_t *)0
    );
}

static uint16_t open_cfw_nvdb_sensor_caldata_ag_crc(void)
{
    return OPEN_CFW_NVDB_SENSOR_CALDATA_CRC16(
        (const uint8_t *)(uintptr_t)OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD,
        64u,
        (const uint16_t *)0
    );
}

void open_cfw_nvdb_sensor_caldata_update(
    const float vector_a[3],
    const float vector_b[3],
    const float vector_c[4],
    const int32_t fixed_transform[4],
    float scale,
    const uint8_t opaque_tail[24]
);

__attribute__((used, noinline))
int open_cfw_nvdb_sensor_caldata_default_initialize(void)
{
    OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD->crc16 =
        open_cfw_nvdb_sensor_caldata_primary_crc();
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_sensor_caldata_load_and_migrate(void)
{
    open_cfw_nvdb_sensor_caldata_record stored;
    volatile open_cfw_nvdb_sensor_caldata_record *record =
        OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD;
    int result;

    OPEN_CFW_NVDB_SENSOR_CALDATA_DIAGNOSTIC();
    result = OPEN_CFW_NVDB_SENSOR_CALDATA_READ(
        OPEN_CFW_NVDB_SENSOR_CALDATA_KEY,
        &stored,
        (uint16_t)sizeof(stored)
    );
    if (result < 1 ||
        (stored.crc16 != record->crc16 && stored.version == 0u)) {
        open_cfw_nvdb_sensor_caldata_update(
            (const float *)(uintptr_t)&record->vector_a[0],
            (const float *)(uintptr_t)&record->vector_b[0],
            (const float *)(uintptr_t)&record->vector_c[0],
            (const int32_t *)(uintptr_t)&record->fixed_transform[0],
            record->scale,
            (const uint8_t *)(uintptr_t)&record->opaque_tail[0]
        );
    }
    return 0;
}

__attribute__((used, noinline))
void open_cfw_nvdb_sensor_caldata_update(
    const float vector_a[3],
    const float vector_b[3],
    const float vector_c[4],
    const int32_t fixed_transform[4],
    float scale,
    const uint8_t opaque_tail[24]
)
{
    volatile open_cfw_nvdb_sensor_caldata_record *record =
        OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD;

    record->version = 1u;
    open_cfw_nvdb_sensor_caldata_copy(record->vector_a, vector_a, 12u);
    open_cfw_nvdb_sensor_caldata_copy(record->vector_b, vector_b, 12u);
    open_cfw_nvdb_sensor_caldata_copy(record->vector_c, vector_c, 16u);
    open_cfw_nvdb_sensor_caldata_copy(
        record->fixed_transform,
        fixed_transform,
        16u
    );
    record->scale = scale;
    open_cfw_nvdb_sensor_caldata_copy(
        record->opaque_tail,
        opaque_tail,
        24u
    );
    record->crc16 = open_cfw_nvdb_sensor_caldata_primary_crc();
    (void)OPEN_CFW_NVDB_SENSOR_CALDATA_WRITE(
        OPEN_CFW_NVDB_SENSOR_CALDATA_KEY,
        (const void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
}

__attribute__((used, noinline))
int open_cfw_nvdb_sensor_caldata_ag_default_initialize(void)
{
    OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD->crc16 =
        open_cfw_nvdb_sensor_caldata_ag_crc();
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_sensor_caldata_ag_load_and_migrate(void)
{
    return 0;
}

__attribute__((used, noinline))
void open_cfw_nvdb_sensor_caldata_ag_update(
    const float *vector_a,
    const float *vector_b,
    const float *matrix
)
{
    volatile open_cfw_nvdb_sensor_caldata_ag_record *record =
        OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD;

    record->version = 1u;
    if (vector_a != (const float *)0) {
        open_cfw_nvdb_sensor_caldata_copy(record->vector_a, vector_a, 12u);
    }
    if (vector_b != (const float *)0) {
        open_cfw_nvdb_sensor_caldata_copy(record->vector_b, vector_b, 12u);
    }
    if (matrix != (const float *)0) {
        open_cfw_nvdb_sensor_caldata_copy(record->matrix, matrix, 36u);
    }
    record->crc16 = open_cfw_nvdb_sensor_caldata_ag_crc();
    (void)OPEN_CFW_NVDB_SENSOR_CALDATA_WRITE(
        OPEN_CFW_NVDB_SENSOR_CALDATA_AG_KEY,
        (const void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
}

__attribute__((used, noinline))
int open_cfw_nvdb_sensor_caldata_check(void)
{
    volatile open_cfw_nvdb_sensor_caldata_ag_record *record =
        OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD;
    float x;
    float y;

    if (OPEN_CFW_NVDB_SENSOR_CALDATA_PATTERN_CHECK_ENABLED() != 1) {
        return 0;
    }
    x = record->matrix[0];
    y = record->matrix[5];
    if (x < 0.6000000834465027f || x >= 0.8500000238418579f ||
        y >= -0.699999988079071f || y < -0.9499999284744263f) {
        return 0;
    }

    OPEN_CFW_NVDB_SENSOR_CALDATA_DIAGNOSTIC();
    open_cfw_nvdb_sensor_caldata_copy(
        record->matrix,
        open_cfw_nvdb_sensor_caldata_default_matrix,
        36u
    );
    return 1;
}

__attribute__((used, noinline))
int open_cfw_nvdb_sensor_caldata_ag_read(
    float vector_a[3],
    float vector_b[3],
    float matrix[9]
)
{
    volatile open_cfw_nvdb_sensor_caldata_ag_record *record =
        OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD;
    int result = OPEN_CFW_NVDB_SENSOR_CALDATA_READ(
        OPEN_CFW_NVDB_SENSOR_CALDATA_AG_KEY,
        (void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );

    (void)open_cfw_nvdb_sensor_caldata_check();
    open_cfw_nvdb_sensor_caldata_copy(vector_a, record->vector_a, 12u);
    open_cfw_nvdb_sensor_caldata_copy(vector_b, record->vector_b, 12u);
    open_cfw_nvdb_sensor_caldata_copy(matrix, record->matrix, 36u);
    return result;
}

#undef OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD
#undef OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD
