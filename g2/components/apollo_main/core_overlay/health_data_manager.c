/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 health-data storage policy recovered
 * from the authenticated 2.2.6.10 application.  Diagnostics are deliberately
 * omitted; validation, conversion, locking, replacement, and bounded
 * highlight aggregation are the functional state transitions.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_HEALTH_DATA_TYPE_MIN 2U
#define OPEN_CFW_HEALTH_DATA_TYPE_MAX 9U
#define OPEN_CFW_HEALTH_DATA_TYPE_COUNT 8U
#define OPEN_CFW_HEALTH_HIGHLIGHT_CAPACITY 5U
#define OPEN_CFW_HEALTH_HIGHLIGHT_TEXT_CAPACITY 256U

typedef struct {
    uint8_t type;
    uint8_t reserved[3];
    uint32_t goal;
    float value;
    float average;
    uint32_t duration;
    uint8_t trend;
    uint8_t tail[3];
} open_cfw_health_record_t;

typedef struct {
    uint8_t type;
    uint8_t reserved;
    uint16_t text_length;
    uint8_t text[258];
} open_cfw_health_pb_highlight_t;

typedef struct {
    uint8_t type;
    uint8_t text[OPEN_CFW_HEALTH_HIGHLIGHT_TEXT_CAPACITY];
} open_cfw_health_highlight_t;

typedef struct {
    uint32_t reserved;
    open_cfw_health_record_t records[OPEN_CFW_HEALTH_DATA_TYPE_COUNT];
    uint32_t highlight_count;
    open_cfw_health_highlight_t highlights[OPEN_CFW_HEALTH_HIGHLIGHT_CAPACITY];
    uint8_t tail[3];
} open_cfw_health_data_manager_storage_t;

_Static_assert(sizeof(open_cfw_health_record_t) == 24U, "health record ABI");
_Static_assert(sizeof(open_cfw_health_pb_highlight_t) == 262U, "PB highlight ABI");
_Static_assert(sizeof(open_cfw_health_highlight_t) == 257U, "highlight ABI");
_Static_assert(
    offsetof(open_cfw_health_data_manager_storage_t, records) == 4U,
    "health record offset"
);
_Static_assert(
    offsetof(open_cfw_health_data_manager_storage_t, highlight_count) == 196U,
    "health highlight count offset"
);
_Static_assert(
    offsetof(open_cfw_health_data_manager_storage_t, highlights) == 200U,
    "health highlight offset"
);
_Static_assert(sizeof(open_cfw_health_data_manager_storage_t) == 1488U, "health store ABI");

#ifndef OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE
#define OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE \
    (*(open_cfw_health_data_manager_storage_t *)(uintptr_t)0x200F41B4U)
#endif

#ifndef OPEN_CFW_HEALTH_DATA_MANAGER_LOCK
unsigned int open_cfw_health_lock_storage(void);
#define OPEN_CFW_HEALTH_DATA_MANAGER_LOCK() open_cfw_health_lock_storage()
#endif

#ifndef OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK
void open_cfw_health_unlock_storage(void);
#define OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK() open_cfw_health_unlock_storage()
#endif

uint32_t open_cfw_health_data_type_index(uint8_t type);
open_cfw_health_record_t *open_cfw_health_data_slot_for_type(uint8_t type);
const char *open_cfw_health_data_type_name(uint8_t type);
uint32_t open_cfw_health_data_manager_init(void);
uint32_t open_cfw_health_data_convert_from_pb(
    const open_cfw_health_record_t *source,
    open_cfw_health_record_t *destination
);
uint32_t open_cfw_health_data_save_single(const open_cfw_health_record_t *source);
uint32_t open_cfw_health_data_save_multiple(const void *batch);
uint32_t open_cfw_health_data_convert_highlight_from_pb(
    const open_cfw_health_pb_highlight_t *source,
    open_cfw_health_highlight_t *destination
);
uint32_t open_cfw_health_data_save_single_highlight(
    const open_cfw_health_pb_highlight_t *source
);
uint32_t open_cfw_health_data_save_multiple_highlights(const void *batch);

static __attribute__((unused)) void open_cfw_health_zero(void *destination, size_t size)
{
    volatile uint8_t *bytes = (volatile uint8_t *)destination;
    size_t index;

    for (index = 0U; index < size; ++index) {
        bytes[index] = 0U;
    }
}

static __attribute__((unused)) void open_cfw_health_copy(
    uint8_t *destination,
    const uint8_t *source,
    size_t size
)
{
    size_t index;

    for (index = 0U; index < size; ++index) {
        destination[index] = source[index];
    }
}

#if !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_type_index(uint8_t type)
{
    if (type < OPEN_CFW_HEALTH_DATA_TYPE_MIN || type > OPEN_CFW_HEALTH_DATA_TYPE_MAX) {
        return UINT32_MAX;
    }
    return (uint32_t)type - OPEN_CFW_HEALTH_DATA_TYPE_MIN;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
open_cfw_health_record_t *open_cfw_health_data_slot_for_type(uint8_t type)
{
    uint32_t index = open_cfw_health_data_type_index(type);

    if (index >= OPEN_CFW_HEALTH_DATA_TYPE_COUNT) {
        return NULL;
    }
    return &OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.records[index];
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
const char *open_cfw_health_data_type_name(uint8_t type)
{
#if defined(OPEN_CFW_HEALTH_DM_USE_RETAINED_NAMES)
    switch (type) {
    case 1U: return (const char *)(uintptr_t)0x005598C8U;
    case 2U: return (const char *)(uintptr_t)0x0078D71CU;
    case 3U: return (const char *)(uintptr_t)0x0078AB20U;
    case 4U: return (const char *)(uintptr_t)0x0078D724U;
    case 5U: return (const char *)(uintptr_t)0x0078AB2CU;
    case 6U: return (const char *)(uintptr_t)0x007860A0U;
    case 7U: return (const char *)(uintptr_t)0x0078AB38U;
    case 8U: return (const char *)(uintptr_t)0x005598C4U;
    case 9U: return (const char *)(uintptr_t)0x007860B0U;
    default: return (const char *)(uintptr_t)0x0078D72CU;
    }
#else
    static const char *const names[10] = {
        "UNKNOWN", "ALL", "STEPS", "CALORIES", "SLEEP",
        "HEART_RATE", "BLOOD_OXYGEN", "TEMPERATURE", "HRV", "PRODUCTIVITY"
    };

    return type < 10U ? names[type] : names[0];
#endif
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_manager_init(void)
{
    open_cfw_health_zero(
        &OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE,
        sizeof(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE)
    );
    return 0U;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_convert_from_pb(
    const open_cfw_health_record_t *source,
    open_cfw_health_record_t *destination
)
{
    if (source == NULL || destination == NULL) {
        return 1U;
    }
    open_cfw_health_zero(destination, sizeof(*destination));
    destination->type = source->type;
    destination->goal = source->goal;
    destination->value = source->value;
    destination->average = source->average;
    destination->duration = source->duration;
    destination->trend = source->tail[0];
    return 0U;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_save_single(const open_cfw_health_record_t *source)
{
    open_cfw_health_record_t *destination;
    uint32_t result;

    if (source == NULL) {
        return 1U;
    }
    if (source->type < OPEN_CFW_HEALTH_DATA_TYPE_MIN) {
        return 3U;
    }
    destination = open_cfw_health_data_slot_for_type(source->type);
    if (destination == NULL) {
        return 3U;
    }
    (void)OPEN_CFW_HEALTH_DATA_MANAGER_LOCK();
    result = open_cfw_health_data_convert_from_pb(source, destination);
    OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK();
    return result;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_save_multiple(const void *batch)
{
    const uint8_t *bytes = (const uint8_t *)batch;
    uint16_t count;
    uint16_t index;

    if (bytes == NULL) {
        return 1U;
    }
    count = (uint16_t)bytes[2] | ((uint16_t)bytes[3] << 8);
    if (count == 0U) {
        return 0U;
    }
    (void)OPEN_CFW_HEALTH_DATA_MANAGER_LOCK();
    for (index = 0U; index < count; ++index) {
        const open_cfw_health_record_t *source =
            (const open_cfw_health_record_t *)(const void *)(bytes + 4U + 24U * index);
        open_cfw_health_record_t *destination;

        if (source->type < OPEN_CFW_HEALTH_DATA_TYPE_MIN) {
            continue;
        }
        destination = open_cfw_health_data_slot_for_type(source->type);
        if (destination != NULL) {
            (void)open_cfw_health_data_convert_from_pb(source, destination);
        }
    }
    OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK();
    return 0U;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_convert_highlight_from_pb(
    const open_cfw_health_pb_highlight_t *source,
    open_cfw_health_highlight_t *destination
)
{
    uint16_t length;

    if (source == NULL || destination == NULL) {
        return 1U;
    }
    open_cfw_health_zero(destination, sizeof(*destination));
    destination->type = source->type;
    length = source->text_length;
    if (length >= OPEN_CFW_HEALTH_HIGHLIGHT_TEXT_CAPACITY) {
        length = OPEN_CFW_HEALTH_HIGHLIGHT_TEXT_CAPACITY - 1U;
    }
    open_cfw_health_copy(destination->text, source->text, length);
    destination->text[length] = 0U;
    return 0U;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_save_single_highlight(
    const open_cfw_health_pb_highlight_t *source
)
{
    uint32_t result;

    if (source == NULL) {
        return 1U;
    }
    if (source->type < OPEN_CFW_HEALTH_DATA_TYPE_MIN) {
        return 3U;
    }
    (void)OPEN_CFW_HEALTH_DATA_MANAGER_LOCK();
    open_cfw_health_zero(
        OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights,
        sizeof(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights)
    );
    OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count = 1U;
    result = open_cfw_health_data_convert_highlight_from_pb(
        source,
        &OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[0]
    );
    if (result != 0U) {
        OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count = 0U;
    }
    OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK();
    return result;
}
#endif

#if !defined(OPEN_CFW_HEALTH_DM_INDEX_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SLOT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_NAME_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_data_save_multiple_highlights(const void *batch)
{
    const uint8_t *bytes = (const uint8_t *)batch;
    uint16_t count;
    uint16_t index;

    if (bytes == NULL) {
        return 1U;
    }
    count = (uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8);
    if (count == 0U) {
        return 0U;
    }
    (void)OPEN_CFW_HEALTH_DATA_MANAGER_LOCK();
    open_cfw_health_zero(
        OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights,
        sizeof(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights)
    );
    OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count = 0U;
    for (index = 0U; index < count; ++index) {
        const open_cfw_health_pb_highlight_t *source =
            (const open_cfw_health_pb_highlight_t *)(const void *)(bytes + 2U + 262U * index);
        uint32_t slot;

        if (source->type < OPEN_CFW_HEALTH_DATA_TYPE_MIN) {
            continue;
        }
        slot = OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count;
        if (slot >= OPEN_CFW_HEALTH_HIGHLIGHT_CAPACITY) {
            break;
        }
        if (open_cfw_health_data_convert_highlight_from_pb(
                source,
                &OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[slot]
            ) == 0U) {
            OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count = slot + 1U;
        }
    }
    OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK();
    return 0U;
}
#endif
