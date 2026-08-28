#define OPEN_CFW_MSPI_WRITE_TRANSFER_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_write_transfer_42069e.c"

static open_cfw_write_transfer_u32 handle_enabled;
static open_cfw_write_transfer_u32 hal_status;
static open_cfw_write_transfer_u32 hal_calls;
static open_cfw_write_transfer_u32 log_calls;
static open_cfw_write_transfer_u32 captured[14];

void open_cfw_write_transfer_fixture_reset(void)
{
    open_cfw_write_transfer_u32 index;
    handle_enabled = 1U;
    hal_status = 0U;
    hal_calls = 0U;
    log_calls = 0U;
    for (index = 0U; index < 14U; ++index) {
        captured[index] = 0U;
    }
}

void open_cfw_write_transfer_fixture_config(
    open_cfw_write_transfer_u32 enabled, open_cfw_write_transfer_u32 status)
{
    handle_enabled = enabled;
    hal_status = status;
}

void *open_cfw_write_transfer_host_handle(void)
{
    return handle_enabled != 0U ?
        (void *)(open_cfw_write_transfer_word)0x1234U : (void *)0;
}

open_cfw_write_transfer_u32 open_cfw_write_transfer_host_hal(
    void *handle, const open_cfw_write_transfer_descriptor *descriptor,
    open_cfw_write_transfer_u32 timeout)
{
    ++hal_calls;
    captured[0] = (open_cfw_write_transfer_u32)
        (open_cfw_write_transfer_word)handle;
    captured[1] = descriptor->length;
    captured[2] = descriptor->reserved_04;
    captured[3] = descriptor->reserved_05;
    captured[4] = descriptor->write_mode;
    captured[5] = descriptor->address_present;
    captured[6] = descriptor->address;
    captured[7] = descriptor->instruction_present;
    captured[8] = descriptor->reserved_13;
    captured[9] = descriptor->instruction;
    captured[10] = descriptor->direction;
    captured[11] = descriptor->reserved_17 |
        descriptor->reserved_18 | descriptor->reserved_19;
    captured[12] = descriptor->buffer;
    captured[13] = timeout;
    return hal_status;
}

void open_cfw_write_transfer_host_log(
    open_cfw_write_transfer_u32 instruction,
    open_cfw_write_transfer_u32 address,
    open_cfw_write_transfer_u32 length,
    open_cfw_write_transfer_u32 status)
{
    ++log_calls;
    captured[9] = instruction;
    captured[6] = address;
    captured[1] = length;
    captured[11] = status;
}

open_cfw_write_transfer_u32 open_cfw_write_transfer_fixture_value(
    open_cfw_write_transfer_u32 field)
{
    if (field == 14U) return hal_calls;
    if (field == 15U) return log_calls;
    return captured[field];
}
