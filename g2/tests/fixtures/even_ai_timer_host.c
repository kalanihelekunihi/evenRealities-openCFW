/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static void *host_common_timer;
static void *host_heartbeat_timer;
static uint8_t host_workflow[2];
static uint8_t host_service_status[9];
static uint32_t host_tick;
static uint8_t host_role;
static unsigned host_sync_calls;
static unsigned host_control_calls;
static unsigned host_state_calls;
static uint8_t host_sync_payload[3];
static uint8_t host_control_command;
static uint32_t host_state_command;
static uint32_t host_state_value;

static int host_sync(
    uint16_t record_id,
    const void *payload,
    uint32_t payload_bytes,
    void *completion,
    uint32_t channel
)
{
    const uint8_t *bytes = (const uint8_t *)payload;
    (void)completion;
    if (record_id != 7U || payload_bytes != 3U || channel != 5U) {
        abort();
    }
    memcpy(host_sync_payload, bytes, 3U);
    ++host_sync_calls;
    return 0;
}

static void host_send_control(uint8_t command)
{
    host_control_command = command;
    ++host_control_calls;
}

static void host_set_state(uint32_t command, uint32_t value)
{
    host_state_command = command;
    host_state_value = value;
    ++host_state_calls;
}

#define OPEN_CFW_EVEN_AI_COMMON_TIMER \
    (*(open_cfw_even_ai_timer_record *)host_common_timer)
#define OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER \
    (*(open_cfw_even_ai_timer_record *)host_heartbeat_timer)
#define OPEN_CFW_EVEN_AI_WORKFLOW_STATE ((volatile uint8_t *)host_workflow)
#define OPEN_CFW_EVEN_AI_SERVICE_STATUS \
    ((volatile uint8_t *)host_service_status)
#define OPEN_CFW_EVEN_AI_TICK_NOW() (host_tick)
#define OPEN_CFW_EVEN_AI_ROLE() (host_role)
#define OPEN_CFW_EVEN_AI_SYNC(record_id, payload, payload_bytes, completion, channel) \
    host_sync((record_id), (payload), (payload_bytes), (completion), (channel))
#define OPEN_CFW_EVEN_AI_SEND_CONTROL(command) host_send_control((command))
#define OPEN_CFW_EVEN_AI_SET_STATE(command, value) \
    host_set_state((command), (value))
#include "../../components/apollo_main/core_overlay/even_ai_timer.c"

static void require(int condition)
{
    if (!condition) {
        abort();
    }
}

static void reset_observations(void)
{
    host_sync_calls = 0U;
    host_control_calls = 0U;
    host_state_calls = 0U;
    memset(host_sync_payload, 0, sizeof(host_sync_payload));
}

int main(void)
{
    open_cfw_even_ai_timer_record common = {0};
    open_cfw_even_ai_timer_record heartbeat = {0};
    host_common_timer = &common;
    host_heartbeat_timer = &heartbeat;

    host_role = 0U;
    host_tick = 100U;
    open_cfw_even_ai_timer_start_all(123U);
    require(common.armed == 0U && heartbeat.armed == 0U);

    host_role = 1U;
    open_cfw_even_ai_timer_start_all(123U);
    require(common.start_tick == 100U && common.duration_ticks == 123U);
    require(common.state == 1U && common.armed == 1U);
    require(heartbeat.duration_ticks == 10000U && heartbeat.armed == 1U);

    host_tick = 222U;
    require(open_cfw_even_ai_common_timer_mgr_check_timeout() == 0);
    host_tick = 223U;
    require(open_cfw_even_ai_common_timer_mgr_check_timeout() == 1);
    require(common.state == 2U && common.armed == 0U);

    common.start_tick = 0xFFFFFFF0U;
    common.duration_ticks = 32U;
    common.state = 1U;
    common.armed = 1U;
    host_tick = 0x10U;
    require(open_cfw_even_ai_common_timer_mgr_check_timeout() == 1);

    reset_observations();
    host_workflow[0] = 1U;
    host_workflow[1] = 1U;
    common.state = 2U;
    host_tick = 500U;
    open_cfw_even_ai_common_timer_mgr_process_timeout();
    require(common.armed == 1U && common.duration_ticks == 3000U);
    require(host_sync_calls == 1U && host_control_calls == 0U);
    require(host_sync_payload[0] == 7U && host_sync_payload[1] == 7U &&
            host_sync_payload[2] == 4U);

    reset_observations();
    host_workflow[1] = 2U;
    host_service_status[8] = 0U;
    common.state = 2U;
    open_cfw_even_ai_common_timer_mgr_process_timeout();
    require(host_control_calls == 1U && host_control_command == 3U);
    require(host_sync_calls == 1U);

    reset_observations();
    host_workflow[0] = 6U;
    common.state = 2U;
    open_cfw_even_ai_common_timer_mgr_process_timeout();
    require(host_state_calls == 1U && host_state_command == 3U &&
            host_state_value == 0U);

    reset_observations();
    heartbeat.state = 2U;
    heartbeat.armed = 0U;
    open_cfw_even_ai_heartbeat_timer_mgr_process_timeout();
    require(heartbeat.state == 0U && host_state_calls == 1U);

    common.state = 1U;
    common.armed = 1U;
    heartbeat.state = 1U;
    heartbeat.armed = 1U;
    open_cfw_even_ai_timer_deinit_all();
    require(common.state == 0U && common.armed == 0U);
    require(heartbeat.state == 0U && heartbeat.armed == 0U);
    return 0;
}
