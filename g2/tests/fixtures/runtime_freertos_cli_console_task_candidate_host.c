/*
 * SPDX-License-Identifier: MIT
 *
 * Native host seam for the production-excluded G2 CLI console-task candidate.
 */

#include <stdint.h>
#include <string.h>

#include "runtime_freertos_cli_console_task_candidate.h"

enum {
    HOST_EVENT_DISPLAY_BYTE = 1U,
    HOST_EVENT_DISPLAY_STRING = 2U,
    HOST_EVENT_PROCESS = 3U,
    HOST_EVENT_REGISTER = 4U,
    HOST_EVENT_RECEIVE = 5U,
    HOST_EVENT_LIMIT = 512U,
    HOST_PROCESS_STEP_LIMIT = 16U
};

struct host_event {
    uint32_t type;
    uint32_t value;
    char text[129];
};

static struct open_cfw_freertos_cli_console_state host_state;
static struct host_event host_events[HOST_EVENT_LIMIT];
static uint32_t host_event_used;
static char host_process_output[HOST_PROCESS_STEP_LIMIT][129];
static int32_t host_process_result[HOST_PROCESS_STEP_LIMIT];
static uint32_t host_process_step_count;
static uint32_t host_process_cursor;
static uint32_t host_receive_result;
static uint8_t host_receive_value;
static uint32_t host_receive_writes;
static void *host_observed_receive_handle;
static uint32_t host_observed_receive_length;
static int32_t host_observed_receive_timeout;

void *volatile open_cfw_retained_freertos_cli_console_receive_handle =
    (void *)(uintptr_t)0x200748BCU;
open_cfw_freertos_cli_console_u8
    open_cfw_retained_freertos_cli_console_output[128];
open_cfw_freertos_cli_console_u8
    open_cfw_retained_freertos_cli_console_input[128];

static void host_copy_text(char destination[129], const char *source)
{
    uint32_t index = 0U;

    while (index < 127U && source[index] != '\0') {
        destination[index] = source[index];
        index++;
    }
    destination[index] = '\0';
}

static void host_record(uint32_t type, uint32_t value, const char *text)
{
    struct host_event *event;

    if (host_event_used >= HOST_EVENT_LIMIT) {
        return;
    }
    event = &host_events[host_event_used];
    host_event_used++;
    event->type = type;
    event->value = value;
    event->text[0] = '\0';
    if (text != (const char *)0) {
        host_copy_text(event->text, text);
    }
}

void open_cfw_retained_freertos_cli_console_display_string(const char *text)
{
    host_record(HOST_EVENT_DISPLAY_STRING, 0U, text);
}

void open_cfw_retained_freertos_cli_console_display_byte(
    open_cfw_freertos_cli_console_u8 value
)
{
    host_record(HOST_EVENT_DISPLAY_BYTE, value, (const char *)0);
}

open_cfw_freertos_cli_console_s32
open_cfw_retained_freertos_cli_process_command(
    const char *input,
    char *output,
    open_cfw_freertos_cli_console_u32 output_length
)
{
    uint32_t step = host_process_cursor;
    int32_t result = 0;

    host_record(HOST_EVENT_PROCESS, output_length, input);
    if (step < host_process_step_count) {
        host_copy_text(output, host_process_output[step]);
        result = host_process_result[step];
    } else {
        output[0] = '\0';
    }
    host_process_cursor++;
    return result;
}

open_cfw_freertos_cli_console_u32
open_cfw_retained_freertos_cli_console_receive(
    void *handle,
    void *destination,
    open_cfw_freertos_cli_console_u32 length,
    open_cfw_freertos_cli_console_s32 timeout
)
{
    host_observed_receive_handle = handle;
    host_observed_receive_length = length;
    host_observed_receive_timeout = timeout;
    host_record(HOST_EVENT_RECEIVE, host_receive_result, (const char *)0);
    if (host_receive_writes != 0U) {
        *(uint8_t *)destination = host_receive_value;
    }
    return host_receive_result;
}

#define HOST_DEFINE_REGISTER_GROUP(suffix, address)                         \
    void open_cfw_retained_freertos_cli_register_group_##suffix(void)      \
    {                                                                       \
        host_record(HOST_EVENT_REGISTER, (address), (const char *)0);       \
    }

HOST_DEFINE_REGISTER_GROUP(57e626, 0x0057E626U)
HOST_DEFINE_REGISTER_GROUP(57e810, 0x0057E810U)
HOST_DEFINE_REGISTER_GROUP(57ff40, 0x0057FF40U)
HOST_DEFINE_REGISTER_GROUP(580392, 0x00580392U)
HOST_DEFINE_REGISTER_GROUP(5807c0, 0x005807C0U)
HOST_DEFINE_REGISTER_GROUP(580c04, 0x00580C04U)
HOST_DEFINE_REGISTER_GROUP(580fec, 0x00580FECU)
HOST_DEFINE_REGISTER_GROUP(5810d8, 0x005810D8U)
HOST_DEFINE_REGISTER_GROUP(581136, 0x00581136U)
HOST_DEFINE_REGISTER_GROUP(581644, 0x00581644U)
HOST_DEFINE_REGISTER_GROUP(58183a, 0x0058183AU)
HOST_DEFINE_REGISTER_GROUP(581960, 0x00581960U)
HOST_DEFINE_REGISTER_GROUP(581d60, 0x00581D60U)
HOST_DEFINE_REGISTER_GROUP(5827d0, 0x005827D0U)
HOST_DEFINE_REGISTER_GROUP(5836b8, 0x005836B8U)
HOST_DEFINE_REGISTER_GROUP(583cec, 0x00583CECU)
HOST_DEFINE_REGISTER_GROUP(583f74, 0x00583F74U)
HOST_DEFINE_REGISTER_GROUP(5840f4, 0x005840F4U)
HOST_DEFINE_REGISTER_GROUP(5841ee, 0x005841EEU)
HOST_DEFINE_REGISTER_GROUP(584320, 0x00584320U)
HOST_DEFINE_REGISTER_GROUP(584430, 0x00584430U)
HOST_DEFINE_REGISTER_GROUP(584702, 0x00584702U)

#undef HOST_DEFINE_REGISTER_GROUP

void open_cfw_freertos_cli_console_host_reset(void)
{
    memset(host_events, 0, sizeof(host_events));
    memset(host_process_output, 0, sizeof(host_process_output));
    memset(host_process_result, 0, sizeof(host_process_result));
    memset(
        open_cfw_retained_freertos_cli_console_input,
        0xA5,
        sizeof(open_cfw_retained_freertos_cli_console_input)
    );
    memset(
        open_cfw_retained_freertos_cli_console_output,
        0x5A,
        sizeof(open_cfw_retained_freertos_cli_console_output)
    );
    host_event_used = 0U;
    host_process_step_count = 0U;
    host_process_cursor = 0U;
    host_receive_result = 0U;
    host_receive_value = 0U;
    host_receive_writes = 0U;
    host_observed_receive_handle = (void *)0;
    host_observed_receive_length = 0U;
    host_observed_receive_timeout = 0;
    open_cfw_freertos_cli_console_state_initialize(
        &host_state,
        open_cfw_retained_freertos_cli_console_input,
        open_cfw_retained_freertos_cli_console_output
    );
}

void open_cfw_freertos_cli_console_host_consume(uint8_t value)
{
    open_cfw_freertos_cli_console_consume_byte_candidate(&host_state, value);
}

uint32_t open_cfw_freertos_cli_console_host_poll(void)
{
    return open_cfw_freertos_cli_console_poll_once_candidate(&host_state);
}

void open_cfw_freertos_cli_console_host_register(void)
{
    open_cfw_freertos_cli_console_register_groups_candidate();
}

void open_cfw_freertos_cli_console_host_set_process_count(uint32_t count)
{
    if (count > HOST_PROCESS_STEP_LIMIT) {
        count = HOST_PROCESS_STEP_LIMIT;
    }
    host_process_step_count = count;
    host_process_cursor = 0U;
}

void open_cfw_freertos_cli_console_host_set_process_step(
    uint32_t index,
    const char *output,
    int32_t result
)
{
    if (index >= HOST_PROCESS_STEP_LIMIT) {
        return;
    }
    memset(host_process_output[index], 0, sizeof(host_process_output[index]));
    host_copy_text(host_process_output[index], output);
    host_process_result[index] = result;
}

void open_cfw_freertos_cli_console_host_set_receive(
    uint32_t result,
    uint8_t value,
    uint32_t writes
)
{
    host_receive_result = result;
    host_receive_value = value;
    host_receive_writes = writes;
}

uint32_t open_cfw_freertos_cli_console_host_length(void)
{
    return host_state.length;
}

const uint8_t *open_cfw_freertos_cli_console_host_input(void)
{
    return host_state.input;
}

const uint8_t *open_cfw_freertos_cli_console_host_output(void)
{
    return host_state.output;
}

uint32_t open_cfw_freertos_cli_console_host_event_count(void)
{
    return host_event_used;
}

uint32_t open_cfw_freertos_cli_console_host_event_type(uint32_t index)
{
    return index < host_event_used ? host_events[index].type : 0U;
}

uint32_t open_cfw_freertos_cli_console_host_event_value(uint32_t index)
{
    return index < host_event_used ? host_events[index].value : 0U;
}

const char *open_cfw_freertos_cli_console_host_event_text(uint32_t index)
{
    return index < host_event_used ? host_events[index].text : (const char *)0;
}

uint32_t open_cfw_freertos_cli_console_host_process_calls(void)
{
    return host_process_cursor;
}

uintptr_t open_cfw_freertos_cli_console_host_receive_handle(void)
{
    return (uintptr_t)host_observed_receive_handle;
}

uint32_t open_cfw_freertos_cli_console_host_receive_length(void)
{
    return host_observed_receive_length;
}

int32_t open_cfw_freertos_cli_console_host_receive_timeout(void)
{
    return host_observed_receive_timeout;
}
