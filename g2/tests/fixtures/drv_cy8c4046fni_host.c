#include <stdint.h>
#include <string.h>

typedef int32_t (*register_write_fn)(uint8_t, const void *, uint16_t);
typedef int32_t (*register_read_fn)(uint8_t, void *, uint16_t);
typedef int32_t (*raw_write_fn)(const void *, uint16_t);
typedef int32_t (*raw_read_fn)(void *, uint16_t);
typedef struct {
    register_write_fn register_write;
    register_read_fn register_read;
    raw_write_fn raw_write;
    raw_read_fn raw_read;
} test_ops;

uint8_t open_cfw_test_cy8c_ops_storage[4u * sizeof(void *)];
uint8_t open_cfw_test_cy8c_baseline_scratch[4];
uint32_t open_cfw_test_cy8c_stock_ops_words[4];
uint8_t open_cfw_test_cy8c_register_data[256][32];
uint8_t open_cfw_test_cy8c_register_size[256];
int32_t open_cfw_test_cy8c_register_status[256];
uint8_t open_cfw_test_cy8c_raw_read_data[32];
uint8_t open_cfw_test_cy8c_raw_read_size;
int32_t open_cfw_test_cy8c_raw_read_status;
uint32_t open_cfw_test_cy8c_last_command;
uint32_t open_cfw_test_cy8c_last_size;
uint8_t open_cfw_test_cy8c_last_data[32];
uint32_t open_cfw_test_cy8c_board_count;
uint32_t open_cfw_test_cy8c_board_records[8][2];
uint32_t open_cfw_test_cy8c_delay_count;
uint32_t open_cfw_test_cy8c_delay_records[8];
uint32_t open_cfw_test_cy8c_hal_kind;
uint32_t open_cfw_test_cy8c_hal_bus;
uint32_t open_cfw_test_cy8c_hal_address;

static int32_t test_register_write(
    uint8_t command, const void *data, uint16_t size
)
{
    open_cfw_test_cy8c_last_command = command;
    open_cfw_test_cy8c_last_size = size;
    if (data != 0 && size <= sizeof(open_cfw_test_cy8c_last_data)) {
        memcpy(open_cfw_test_cy8c_last_data, data, size);
    }
    return open_cfw_test_cy8c_register_status[command];
}

static int32_t test_register_read(uint8_t command, void *data, uint16_t size)
{
    open_cfw_test_cy8c_last_command = command;
    open_cfw_test_cy8c_last_size = size;
    if (data != 0 && size <= sizeof(open_cfw_test_cy8c_register_data[command])) {
        memcpy(data, open_cfw_test_cy8c_register_data[command], size);
    }
    return open_cfw_test_cy8c_register_status[command];
}

static int32_t test_raw_write(const void *data, uint16_t size)
{
    open_cfw_test_cy8c_last_command = 0x100u;
    open_cfw_test_cy8c_last_size = size;
    if (data != 0 && size <= sizeof(open_cfw_test_cy8c_last_data)) {
        memcpy(open_cfw_test_cy8c_last_data, data, size);
    }
    return 0;
}

static int32_t test_raw_read(void *data, uint16_t size)
{
    open_cfw_test_cy8c_last_command = 0x101u;
    open_cfw_test_cy8c_last_size = size;
    if (data != 0 && size <= sizeof(open_cfw_test_cy8c_raw_read_data)) {
        memcpy(data, open_cfw_test_cy8c_raw_read_data, size);
    }
    return open_cfw_test_cy8c_raw_read_status;
}

void open_cfw_test_cy8c_install_default_ops(void *ops)
{
    test_ops *table = (test_ops *)ops;
    table->register_write = test_register_write;
    table->register_read = test_register_read;
    table->raw_write = test_raw_write;
    table->raw_read = test_raw_read;
}

void open_cfw_test_cy8c_reset(void)
{
    memset(open_cfw_test_cy8c_ops_storage, 0, sizeof(open_cfw_test_cy8c_ops_storage));
    memset(open_cfw_test_cy8c_baseline_scratch, 0, sizeof(open_cfw_test_cy8c_baseline_scratch));
    memset(open_cfw_test_cy8c_register_data, 0, sizeof(open_cfw_test_cy8c_register_data));
    memset(open_cfw_test_cy8c_register_size, 0, sizeof(open_cfw_test_cy8c_register_size));
    memset(open_cfw_test_cy8c_register_status, 0, sizeof(open_cfw_test_cy8c_register_status));
    memset(open_cfw_test_cy8c_raw_read_data, 0, sizeof(open_cfw_test_cy8c_raw_read_data));
    memset(open_cfw_test_cy8c_last_data, 0, sizeof(open_cfw_test_cy8c_last_data));
    memset(open_cfw_test_cy8c_board_records, 0, sizeof(open_cfw_test_cy8c_board_records));
    memset(open_cfw_test_cy8c_delay_records, 0, sizeof(open_cfw_test_cy8c_delay_records));
    open_cfw_test_cy8c_raw_read_status = 0;
    open_cfw_test_cy8c_last_command = 0;
    open_cfw_test_cy8c_last_size = 0;
    open_cfw_test_cy8c_board_count = 0;
    open_cfw_test_cy8c_delay_count = 0;
    open_cfw_test_cy8c_hal_kind = 0;
    open_cfw_test_cy8c_hal_bus = 0;
    open_cfw_test_cy8c_hal_address = 0;
    open_cfw_test_cy8c_install_default_ops(open_cfw_test_cy8c_ops_storage);
}

static int32_t capture_hal(
    uint32_t kind, uint32_t bus, uint32_t address, const void *command,
    const void *data, uint16_t size
)
{
    open_cfw_test_cy8c_hal_kind = kind;
    open_cfw_test_cy8c_hal_bus = bus;
    open_cfw_test_cy8c_hal_address = address;
    open_cfw_test_cy8c_last_command = command == 0 ? 0u : *(const uint8_t *)command;
    open_cfw_test_cy8c_last_size = size;
    if (data != 0 && size <= sizeof(open_cfw_test_cy8c_last_data)) {
        memcpy(open_cfw_test_cy8c_last_data, data, size);
    }
    return 0;
}

int32_t open_cfw_test_cy8c_hal_register_write(
    uint32_t bus, uint32_t address, const void *command,
    uint32_t command_size, const void *data, uint16_t data_size
)
{
    (void)command_size;
    return capture_hal(1u, bus, address, command, data, data_size);
}

int32_t open_cfw_test_cy8c_hal_register_read(
    uint32_t bus, uint32_t address, const void *command,
    uint32_t command_size, void *data, uint16_t data_size
)
{
    (void)command_size;
    return capture_hal(2u, bus, address, command, data, data_size);
}

int32_t open_cfw_test_cy8c_hal_raw_write(
    uint32_t bus, uint32_t address, const void *data, uint16_t size
)
{
    return capture_hal(3u, bus, address, 0, data, size);
}

int32_t open_cfw_test_cy8c_hal_raw_read(
    uint32_t bus, uint32_t address, void *data, uint16_t size
)
{
    return capture_hal(4u, bus, address, 0, data, size);
}

void open_cfw_test_cy8c_board_control(uint32_t selector, uint32_t enabled)
{
    uint32_t index = open_cfw_test_cy8c_board_count++;
    if (index < 8u) {
        open_cfw_test_cy8c_board_records[index][0] = selector;
        open_cfw_test_cy8c_board_records[index][1] = enabled;
    }
}

void open_cfw_test_cy8c_delay(uint32_t milliseconds)
{
    uint32_t index = open_cfw_test_cy8c_delay_count++;
    if (index < 8u) {
        open_cfw_test_cy8c_delay_records[index] = milliseconds;
    }
}
