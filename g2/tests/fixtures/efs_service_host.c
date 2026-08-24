#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t transfer_storage[0x78] __attribute__((aligned(4)));
static uint8_t android_storage[0x2137];
static uint8_t *android_pointer;
static uint8_t export_storage[0x1000];
static uint8_t verify_storage[0x1000];
static uint8_t whitelist_path[] = "user/notify_whitelist.json";

static int8_t test_send(uint8_t, uint8_t, const uint8_t *, uint16_t);
static int8_t test_send_raw(uint8_t, uint8_t, const uint8_t *, uint16_t);
static uint32_t test_mode(uint32_t);
static uint32_t test_open(const uint8_t *, uint32_t);
static int32_t test_close(uint32_t);
static uint32_t test_read(void *, uint32_t, uint32_t, uint32_t);
static uint32_t test_write(const void *, uint32_t, uint32_t, uint32_t);
static int32_t test_seek(uint32_t, int32_t, uint32_t);
static int32_t test_size(uint32_t);
static int32_t test_remove(const uint8_t *);
static void test_crc(const uint8_t *, uint32_t, uint32_t *);
static uint8_t *test_android_buffer(void);
static void test_android_consume(const uint8_t *);
static void test_whitelist_reload(uint32_t);
static uint8_t test_path_valid(const uint8_t *);
static int32_t test_trace_prepare(void);
static void test_export_mode(uint8_t);
static void test_activity_begin(void);
static void test_activity_end(uint32_t);
static void test_register(uint32_t,
    int (*)(uint8_t, const uint8_t *, uint16_t), uint8_t);

#define OPEN_CFW_EFS_SERVICE_TRANSFER \
    (*(open_cfw_efs_transfer *)(void *)transfer_storage)
#define OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER android_pointer
#define OPEN_CFW_EFS_SERVICE_EXPORT_BUFFER export_storage
#define OPEN_CFW_EFS_SERVICE_IMPORT_VERIFY_BUFFER verify_storage
static uint8_t export_active;
#define OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE export_active
#define OPEN_CFW_EFS_SERVICE_WHITELIST_PATH whitelist_path
#define OPEN_CFW_EFS_SERVICE_SEND(response, command, payload, length) \
    test_send((response), (command), (payload), (length))
#define OPEN_CFW_EFS_SERVICE_SEND_RAW(response, command, payload, length) \
    test_send_raw((response), (command), (payload), (length))
#define OPEN_CFW_EFS_SERVICE_FILE_MODE(selector) test_mode((selector))
#define OPEN_CFW_EFS_SERVICE_FILE_OPEN(path, mode) test_open((path), (mode))
#define OPEN_CFW_EFS_SERVICE_FILE_CLOSE(handle) test_close((handle))
#define OPEN_CFW_EFS_SERVICE_FILE_READ(data, item_size, count, handle) \
    test_read((data), (item_size), (count), (handle))
#define OPEN_CFW_EFS_SERVICE_FILE_WRITE(data, item_size, count, handle) \
    test_write((data), (item_size), (count), (handle))
#define OPEN_CFW_EFS_SERVICE_FILE_SEEK(handle, offset, origin) \
    test_seek((handle), (offset), (origin))
#define OPEN_CFW_EFS_SERVICE_FILE_SIZE(handle) test_size((handle))
#define OPEN_CFW_EFS_SERVICE_FILE_REMOVE(path) test_remove((path))
#define OPEN_CFW_EFS_SERVICE_CRC32C(data, length, crc) \
    test_crc((data), (length), (crc))
#define OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER_PROVIDER() test_android_buffer()
#define OPEN_CFW_EFS_SERVICE_ANDROID_CONSUME(data) test_android_consume((data))
#define OPEN_CFW_EFS_SERVICE_WHITELIST_RELOAD(reason) \
    test_whitelist_reload((reason))
#define OPEN_CFW_EFS_SERVICE_EXPORT_PATH_VALID(path) test_path_valid((path))
#define OPEN_CFW_EFS_SERVICE_LOGGER_PATH_VALID(path) test_path_valid((path))
#define OPEN_CFW_EFS_SERVICE_TRACE_PATH_VALID(path) test_path_valid((path))
#define OPEN_CFW_EFS_SERVICE_TRACE_PREPARE() test_trace_prepare()
#define OPEN_CFW_EFS_SERVICE_EXPORT_MODE(enabled) test_export_mode((enabled))
#define OPEN_CFW_EFS_SERVICE_ACTIVITY_BEGIN() test_activity_begin()
#define OPEN_CFW_EFS_SERVICE_ACTIVITY_END(milliseconds) \
    test_activity_end((milliseconds))
#define OPEN_CFW_EFS_SERVICE_REGISTER(service, callback, enabled) \
    test_register((service), (callback), (enabled))
#define OPEN_CFW_EFS_SERVICE_DISPATCH_CALLBACK EFS_FrameDispatch

#include "../../components/apollo_main/core_overlay/efs_service.c"

static uint8_t file_data[0x3000];
static uint32_t file_length;
static uint32_t file_position;
static uint8_t file_exists;
static uint8_t file_open;
static uint8_t fail_open;
static uint8_t fail_io;
static uint8_t removed;
static uint8_t last_path[80];

typedef struct {
    uint8_t response;
    uint8_t command;
    uint16_t length;
    uint8_t data[0x1000];
} sent_packet;

static sent_packet sent[16];
static unsigned sent_count;
static sent_packet raw_sent[8];
static unsigned raw_count;
static unsigned close_count;
static unsigned reload_count;
static unsigned consume_count;
static unsigned activity_begin_count;
static unsigned activity_end_count;
static uint32_t activity_end_delay;
static uint8_t export_mode;
static unsigned register_count;
static uint32_t registered_service;
static int (*registered_callback)(uint8_t, const uint8_t *, uint16_t);
static uint8_t registered_enabled;

static int8_t test_send(uint8_t response, uint8_t command,
    const uint8_t *payload, uint16_t length)
{
    assert(sent_count < 16U && length <= sizeof(sent[0].data));
    sent[sent_count].response = response;
    sent[sent_count].command = command;
    sent[sent_count].length = length;
    memcpy(sent[sent_count].data, payload, length);
    ++sent_count;
    return 0;
}

static int8_t test_send_raw(uint8_t response, uint8_t command,
    const uint8_t *payload, uint16_t length)
{
    assert(raw_count < 8U && length <= sizeof(raw_sent[0].data));
    raw_sent[raw_count].response = response;
    raw_sent[raw_count].command = command;
    raw_sent[raw_count].length = length;
    memcpy(raw_sent[raw_count].data, payload, length);
    ++raw_count;
    return 0;
}

static uint32_t test_mode(uint32_t selector) { return selector; }

static uint32_t test_open(const uint8_t *path, uint32_t mode)
{
    (void)mode;
    if (fail_open != 0U) return 0U;
    memset(last_path, 0, sizeof(last_path));
    memcpy(last_path, path, strnlen((const char *)path, sizeof(last_path) - 1U));
    file_open = 1U;
    file_position = 0U;
    file_exists = 1U;
    return 1U;
}

static int32_t test_close(uint32_t handle)
{
    assert(handle == 1U);
    ++close_count;
    file_open = 0U;
    return 0;
}

static uint32_t test_read(
    void *data, uint32_t item_size, uint32_t count, uint32_t handle)
{
    uint32_t amount;
    assert(item_size == 1U && handle == 1U && file_open != 0U);
    if (fail_io != 0U) return 0U;
    amount = count;
    if (file_position + amount > file_length)
        amount = file_length - file_position;
    memcpy(data, file_data + file_position, amount);
    file_position += amount;
    return amount;
}

static uint32_t test_write(const void *data, uint32_t item_size,
    uint32_t count, uint32_t handle)
{
    assert(item_size == 1U && handle == 1U && file_open != 0U);
    if (fail_io != 0U || file_position + count > sizeof(file_data)) return 0U;
    memcpy(file_data + file_position, data, count);
    file_position += count;
    if (file_position > file_length) file_length = file_position;
    return count;
}

static int32_t test_seek(uint32_t handle, int32_t offset, uint32_t origin)
{
    assert(handle == 1U && origin == 0U && offset >= 0);
    file_position = (uint32_t)offset;
    return 0;
}

static int32_t test_size(uint32_t handle)
{
    assert(handle == 1U && file_open != 0U);
    return (int32_t)file_length;
}

static int32_t test_remove(const uint8_t *path)
{
    (void)path;
    removed = 1U;
    file_exists = 0U;
    file_length = file_position = 0U;
    return 0;
}

static void test_crc(const uint8_t *data, uint32_t length, uint32_t *crc)
{
    uint32_t index;
    for (index = 0U; index < length; ++index)
        *crc = (*crc << 5) ^ (*crc >> 27) ^ data[index];
}

static uint8_t *test_android_buffer(void) { return android_storage; }
static void test_android_consume(const uint8_t *data)
{
    assert(data == android_storage);
    ++consume_count;
}
static void test_whitelist_reload(uint32_t reason)
{
    assert(reason == 2U);
    ++reload_count;
}
static uint8_t test_path_valid(const uint8_t *path)
{
    return (uint8_t)(path != 0 && path[0] == 'u');
}
static int32_t test_trace_prepare(void) { return 0; }
static void test_export_mode(uint8_t enabled) { export_mode = enabled; }
static void test_activity_begin(void) { ++activity_begin_count; }
static void test_activity_end(uint32_t milliseconds)
{
    ++activity_end_count;
    activity_end_delay = milliseconds;
}
static void test_register(uint32_t service,
    int (*callback)(uint8_t, const uint8_t *, uint16_t), uint8_t enabled)
{
    ++register_count;
    registered_service = service;
    registered_callback = callback;
    registered_enabled = enabled;
}

static void store32(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

static uint32_t crc_of(const uint8_t *data, uint32_t length)
{
    uint32_t crc = 0U;
    test_crc(data, length, &crc);
    return crc;
}

static void reset_all(void)
{
    memset(transfer_storage, 0, sizeof(transfer_storage));
    memset(android_storage, 0, sizeof(android_storage));
    memset(export_storage, 0, sizeof(export_storage));
    memset(verify_storage, 0, sizeof(verify_storage));
    memset(file_data, 0, sizeof(file_data));
    memset(sent, 0, sizeof(sent));
    memset(raw_sent, 0, sizeof(raw_sent));
    memset(last_path, 0, sizeof(last_path));
    android_pointer = 0;
    export_active = export_mode = 0U;
    file_length = file_position = 0U;
    file_exists = file_open = fail_open = fail_io = removed = 0U;
    sent_count = raw_count = close_count = reload_count = consume_count = 0U;
    activity_begin_count = activity_end_count = register_count = 0U;
    activity_end_delay = registered_service = 0U;
    registered_callback = 0;
    registered_enabled = 0U;
}

int main(void)
{
    uint8_t metadata[93];
    uint8_t activation[1] = {1U};
    uint8_t complete[1] = {2U};
    uint8_t data[32];
    uint8_t export_request[85];
    uint8_t next[1] = {1U};
    uint32_t expected_crc;
    uint32_t size;
    uint32_t crc;
    uint32_t handle;
    unsigned index;

    reset_all();
    _evenEfsReplyToAPP(0xc4U, 2U, 6U, 0U);
    assert(sent_count == 1U && sent[0].command == 0xc4U);
    assert(sent[0].length == 2U && sent[0].data[0] == 2U &&
        sent[0].data[1] == 6U);
    assert(EFS_NotifyStatus4(0xc5U) == 0x401U);
    assert(EFS_NotifyStatus2(0xc5U) == 0x201U);
    assert(EFS_NotifyStatus5(0xc5U) == 0x501U);
    assert(sent_count == 4U);

    reset_all();
    EFS_ServiceInit();
    assert(register_count == 1U && registered_service == 0x400U);
    assert(registered_callback == EFS_FrameDispatch && registered_enabled == 1U);
    assert(EFS_FrameDispatch(0xc4U, 0, 0U) == 11);

    reset_all();
    for (index = 0U; index < sizeof(data); ++index) data[index] = (uint8_t)index;
    expected_crc = crc_of(data, sizeof(data));
    memset(metadata, 0, sizeof(metadata));
    metadata[0] = 0U;
    store32(metadata + 1U, OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST);
    store32(metadata + 5U, sizeof(data));
    store32(metadata + 9U, expected_crc);
    memcpy(metadata + 13U, "ignored", 8U);
    assert(EFS_FrameDispatch(0xc4U, metadata, sizeof(metadata)) == 0);
    assert(sent_count == 1U && sent[0].data[1] == 0U);
    assert(strcmp((const char *)last_path,
        (const char *)whitelist_path) == 0);
    assert(EFS_FrameDispatch(0xc4U, activation, 1U) == 0);
    assert(EFS_TransferActive() == 1U);
    assert(EFS_FrameDispatch(0xc5U, data, sizeof(data)) == 0);
    assert(sent_count == 2U && sent[1].data[1] == 0U);
    assert(file_length == sizeof(data) && memcmp(file_data, data, sizeof(data)) == 0);
    assert(EFS_FrameDispatch(0xc4U, complete, 1U) == 0);
    assert(sent_count == 3U && sent[2].data[0] == 2U && sent[2].data[1] == 0U);
    assert(reload_count == 1U && EFS_TransferActive() == 0U);

    reset_all();
    memset(metadata, 0, sizeof(metadata));
    store32(metadata + 1U, OPEN_CFW_EFS_SERVICE_TYPE_ANDROID);
    store32(metadata + 5U, 4U);
    memcpy(data, "json", 4U);
    store32(metadata + 9U, crc_of(data, 4U));
    assert(EFS_FrameDispatch(0xc4U, metadata, sizeof(metadata)) == 0);
    assert(android_pointer == android_storage);
    assert(EFS_FrameDispatch(0xc4U, activation, 1U) == 0);
    assert(EFS_FrameDispatch(0xc5U, data, 4U) == 0);
    assert(EFS_FrameDispatch(0xc4U, complete, 1U) == 0);
    assert(consume_count == 1U && memcmp(android_storage, "json", 4U) == 0);

    reset_all();
    for (index = 0U; index < 5000U; ++index) file_data[index] = (uint8_t)index;
    file_length = 5000U;
    file_exists = 1U;
    expected_crc = crc_of(file_data, file_length);
    memset(export_request, 0, sizeof(export_request));
    export_request[0] = 0U;
    store32(export_request + 1U, OPEN_CFW_EFS_SERVICE_TYPE_OTHER);
    memcpy(export_request + 5U, "user/export.bin", 16U);
    assert(EFS_FrameDispatch(0xc6U, export_request, sizeof(export_request)) == 0);
    assert(sent_count == 1U && sent[0].command == 0xc6U && sent[0].length == 10U);
    assert(open_cfw_efs_service_load32(sent[0].data + 2U) == 5000U);
    assert(open_cfw_efs_service_load32(sent[0].data + 6U) == expected_crc);
    assert(raw_count == 1U && raw_sent[0].command == 0xc7U &&
        raw_sent[0].length == 4096U);
    assert(export_active == 1U && export_mode == 1U);
    assert(EFS_FrameDispatch(0xc7U, next, 1U) == 0);
    assert(raw_count == 2U && raw_sent[1].length == 904U);
    assert(export_active == 0U && export_mode == 0U);
    assert(activity_end_delay == 2000U);

    reset_all();
    file_length = 3U;
    memcpy(file_data, "abc", 3U);
    file_exists = 1U;
    handle = 0U;
    size = crc = 0U;
    assert(_fileCaculateCRC(&handle, (const uint8_t *)"user/a", &size, &crc) == 1U);
    assert(handle == 0U && size == 3U && crc == crc_of(file_data, 3U));

    reset_all();
    OPEN_CFW_EFS_SERVICE_TRANSFER.is_start = 1U;
    OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE = 1U;
    OPEN_CFW_EFS_SERVICE_TRANSFER.handle = 1U;
    OPEN_CFW_EFS_SERVICE_TRANSFER.open = 1U;
    file_open = 1U;
    EFS_CancelExport(0, 0, 0U, 0U);
    assert(sent_count == 1U && sent[0].data[0] == 3U && sent[0].data[1] == 8U);
    assert(export_active == 0U && EFS_TransferActive() == 0U);

    return 0;
}
