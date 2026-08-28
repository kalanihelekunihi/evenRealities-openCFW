#define OPEN_CFW_MSPI_DRIVER_INIT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_driver_init_420476.c"

typedef struct {
    open_cfw_driver_init_u32 operation;
    open_cfw_driver_init_u32 value;
} open_cfw_driver_init_host_record;

static open_cfw_driver_init_host_record records[16];
static open_cfw_driver_init_u32 record_count;
static open_cfw_driver_init_u32 statuses[10];
static open_cfw_driver_init_u32 identifier;
static open_cfw_driver_init_u32 logs[4][4];
static open_cfw_driver_init_u32 log_count;

void open_cfw_driver_init_fixture_reset(void)
{
    open_cfw_driver_init_u32 index;
    record_count = 0U;
    log_count = 0U;
    identifier = 0x002539C2U;
    for (index = 0U; index < 10U; ++index) {
        statuses[index] = 0U;
    }
}

void open_cfw_driver_init_fixture_status(
    open_cfw_driver_init_u32 operation, open_cfw_driver_init_u32 status)
{
    statuses[operation] = status;
}

void open_cfw_driver_init_fixture_identifier(open_cfw_driver_init_u32 value)
{
    identifier = value;
}

open_cfw_driver_init_u32 open_cfw_driver_init_host_call(
    open_cfw_driver_init_u32 operation, open_cfw_driver_init_u32 value,
    void *pointer)
{
    records[record_count].operation = operation;
    records[record_count].value = value;
    ++record_count;
    if (operation == 5U && statuses[operation] == 0U) {
        *(open_cfw_driver_init_u32 *)pointer = identifier;
    }
    return statuses[operation];
}

void open_cfw_driver_init_host_log(
    open_cfw_driver_init_u32 level, open_cfw_driver_init_u32 line,
    open_cfw_driver_init_u32 format, open_cfw_driver_init_u32 value)
{
    logs[log_count][0] = level;
    logs[log_count][1] = line;
    logs[log_count][2] = format;
    logs[log_count][3] = value;
    ++log_count;
}

open_cfw_driver_init_u32 open_cfw_driver_init_fixture_record_count(void)
{
    return record_count;
}

open_cfw_driver_init_u32 open_cfw_driver_init_fixture_record(
    open_cfw_driver_init_u32 index, open_cfw_driver_init_u32 field)
{
    return field == 0U ? records[index].operation : records[index].value;
}

open_cfw_driver_init_u32 open_cfw_driver_init_fixture_log_count(void)
{
    return log_count;
}

open_cfw_driver_init_u32 open_cfw_driver_init_fixture_log(
    open_cfw_driver_init_u32 index, open_cfw_driver_init_u32 field)
{
    return logs[index][field];
}
