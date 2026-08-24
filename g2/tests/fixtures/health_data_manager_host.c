#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t open_cfw_test_health_manager_storage[1488];
static unsigned int open_cfw_test_lock_calls;
static unsigned int open_cfw_test_unlock_calls;

static unsigned int open_cfw_test_health_manager_lock(void);
static void open_cfw_test_health_manager_unlock(void);

#define OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE \
    (*(open_cfw_health_data_manager_storage_t *)(void *)open_cfw_test_health_manager_storage)
#define OPEN_CFW_HEALTH_DATA_MANAGER_LOCK() open_cfw_test_health_manager_lock()
#define OPEN_CFW_HEALTH_DATA_MANAGER_UNLOCK() open_cfw_test_health_manager_unlock()

#include "../../components/apollo_main/core_overlay/health_data_manager.c"

static unsigned int open_cfw_test_health_manager_lock(void)
{
    ++open_cfw_test_lock_calls;
    return 1U;
}

static void open_cfw_test_health_manager_unlock(void)
{
    ++open_cfw_test_unlock_calls;
}

static open_cfw_health_record_t make_record(uint8_t type, uint32_t goal, uint8_t trend)
{
    open_cfw_health_record_t record;

    memset(&record, 0xA5, sizeof(record));
    record.type = type;
    record.goal = goal;
    record.value = 12.5f;
    record.average = 9.25f;
    record.duration = 77U;
    record.tail[0] = trend;
    return record;
}

int main(void)
{
    open_cfw_health_record_t record;
    open_cfw_health_record_t converted;
    uint8_t batch[4U + 3U * sizeof(open_cfw_health_record_t)];
    open_cfw_health_pb_highlight_t highlight;
    open_cfw_health_highlight_t converted_highlight;
    uint8_t highlight_batch[2U + 7U * sizeof(open_cfw_health_pb_highlight_t)];
    uint16_t count;
    unsigned int index;

    memset(open_cfw_test_health_manager_storage, 0xA5, sizeof(open_cfw_test_health_manager_storage));
    assert(open_cfw_health_data_manager_init() == 0U);
    for (index = 0U; index < sizeof(open_cfw_test_health_manager_storage); ++index) {
        assert(open_cfw_test_health_manager_storage[index] == 0U);
    }
    assert(open_cfw_health_data_type_index(2U) == 0U);
    assert(open_cfw_health_data_type_index(9U) == 7U);
    assert(open_cfw_health_data_type_index(1U) == UINT32_MAX);
    assert(open_cfw_health_data_slot_for_type(2U) == &OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.records[0]);
    assert(open_cfw_health_data_slot_for_type(10U) == NULL);
    assert(strcmp(open_cfw_health_data_type_name(0U), "UNKNOWN") == 0);
    assert(strcmp(open_cfw_health_data_type_name(1U), "ALL") == 0);
    assert(strcmp(open_cfw_health_data_type_name(8U), "HRV") == 0);
    assert(strcmp(open_cfw_health_data_type_name(9U), "PRODUCTIVITY") == 0);

    record = make_record(2U, 1234U, 6U);
    assert(open_cfw_health_data_convert_from_pb(NULL, &converted) == 1U);
    assert(open_cfw_health_data_convert_from_pb(&record, &converted) == 0U);
    assert(converted.type == 2U && converted.goal == 1234U);
    assert(converted.value == 12.5f && converted.average == 9.25f);
    assert(converted.duration == 77U && converted.trend == 6U);
    assert(converted.reserved[0] == 0U && converted.tail[0] == 0U);

    open_cfw_test_lock_calls = open_cfw_test_unlock_calls = 0U;
    assert(open_cfw_health_data_save_single(NULL) == 1U);
    record.type = 1U;
    assert(open_cfw_health_data_save_single(&record) == 3U);
    record.type = 10U;
    assert(open_cfw_health_data_save_single(&record) == 3U);
    record = make_record(4U, 88U, 2U);
    assert(open_cfw_health_data_save_single(&record) == 0U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.records[2].goal == 88U);
    assert(open_cfw_test_lock_calls == 1U && open_cfw_test_unlock_calls == 1U);

    memset(batch, 0, sizeof(batch));
    count = 3U;
    memcpy(batch + 2U, &count, sizeof(count));
    record = make_record(2U, 10U, 1U);
    memcpy(batch + 4U, &record, sizeof(record));
    record = make_record(1U, 20U, 2U);
    memcpy(batch + 4U + sizeof(record), &record, sizeof(record));
    record = make_record(9U, 30U, 3U);
    memcpy(batch + 4U + 2U * sizeof(record), &record, sizeof(record));
    assert(open_cfw_health_data_save_multiple(batch) == 0U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.records[0].goal == 10U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.records[7].goal == 30U);

    memset(&highlight, 0xA5, sizeof(highlight));
    highlight.type = 5U;
    highlight.text_length = 300U;
    for (index = 0U; index < sizeof(highlight.text); ++index) {
        highlight.text[index] = (uint8_t)('a' + index % 26U);
    }
    assert(open_cfw_health_data_convert_highlight_from_pb(&highlight, &converted_highlight) == 0U);
    assert(converted_highlight.type == 5U);
    assert(converted_highlight.text[254] == highlight.text[254]);
    assert(converted_highlight.text[255] == 0U);
    assert(open_cfw_health_data_save_single_highlight(&highlight) == 0U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count == 1U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[0].type == 5U);

    memset(highlight_batch, 0, sizeof(highlight_batch));
    count = 7U;
    memcpy(highlight_batch, &count, sizeof(count));
    for (index = 0U; index < 7U; ++index) {
        open_cfw_health_pb_highlight_t *item =
            (open_cfw_health_pb_highlight_t *)(void *)(
                highlight_batch + 2U + index * sizeof(open_cfw_health_pb_highlight_t)
            );
        item->type = index == 1U ? 1U : (uint8_t)(2U + index);
        item->text_length = 3U;
        memcpy(item->text, "abc", 3U);
    }
    assert(open_cfw_health_data_save_multiple_highlights(highlight_batch) == 0U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlight_count == 5U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[0].type == 2U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[1].type == 4U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[4].type == 7U);
    assert(OPEN_CFW_HEALTH_DATA_MANAGER_STORAGE.highlights[4].text[3] == 0U);
    return 0;
}
