#define OPEN_CFW_MSPI_WAIT_READY_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_wait_ready_4207a2.c"

static open_cfw_wait_ready_u32 ready_after;
static open_cfw_wait_ready_u32 context_value;
static open_cfw_wait_ready_u32 status_calls;
static open_cfw_wait_ready_u32 context_calls;
static open_cfw_wait_ready_u32 delay5_calls;
static open_cfw_wait_ready_u32 delay1000_calls;
static open_cfw_wait_ready_u32 notify_calls;
static open_cfw_wait_ready_u32 last_notify;

void open_cfw_wait_ready_fixture_reset(void)
{
    ready_after = 0U;
    context_value = 0U;
    status_calls = 0U;
    context_calls = 0U;
    delay5_calls = 0U;
    delay1000_calls = 0U;
    notify_calls = 0U;
    last_notify = 0U;
}

void open_cfw_wait_ready_fixture_config(
    open_cfw_wait_ready_u32 ready_call,
    open_cfw_wait_ready_u32 context)
{
    ready_after = ready_call;
    context_value = context;
}

open_cfw_wait_ready_u32 open_cfw_wait_ready_host_status(void)
{
    ++status_calls;
    return ready_after != 0U && status_calls >= ready_after ? 0U : 1U;
}

open_cfw_wait_ready_u32 open_cfw_wait_ready_host_context(void)
{
    ++context_calls;
    return context_value;
}

void open_cfw_wait_ready_host_delay(open_cfw_wait_ready_u32 duration)
{
    if (duration == 5U) ++delay5_calls;
    if (duration == 1000U) ++delay1000_calls;
}

void open_cfw_wait_ready_host_notify(open_cfw_wait_ready_u32 value)
{
    ++notify_calls;
    last_notify = value;
}

open_cfw_wait_ready_u32 open_cfw_wait_ready_fixture_value(
    open_cfw_wait_ready_u32 field)
{
    switch (field) {
    case 0U: return status_calls;
    case 1U: return context_calls;
    case 2U: return delay5_calls;
    case 3U: return delay1000_calls;
    case 4U: return notify_calls;
    default: return last_notify;
    }
}
