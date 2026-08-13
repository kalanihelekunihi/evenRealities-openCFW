#include "runtime_tinyframe_g2_adapter_candidate.h"

#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { CAPTURE_SIZE = 131072 };

static TinyFrame *active_tf;
static void *allocation_base;
static size_t allocation_size;
static uint8_t capture[CAPTURE_SIZE];
static size_t capture_length;
static uint32_t write_timeout;
static unsigned write_calls;
static unsigned listener_calls;
static unsigned timeout_calls;
static int callback_pointer_matches;
static unsigned log_calls;
static char last_log[256];

static void *host_allocate(size_t size, void *context)
{
    (void)context;
    allocation_base = malloc(size);
    allocation_size = size;
    return allocation_base;
}

static void host_release(void *pointer, void *context)
{
    (void)context;
    free(pointer);
    allocation_base = (void *)0;
    allocation_size = 0U;
}

static void host_write(
    const uint8_t *buffer,
    uint32_t length,
    uint32_t timeout,
    void *context
)
{
    size_t available = CAPTURE_SIZE - capture_length;
    size_t amount = length < available ? (size_t)length : available;
    (void)context;
    memcpy(capture + capture_length, buffer, amount);
    capture_length += amount;
    write_timeout = timeout;
    write_calls++;
}

static void host_vlog(const char *format, va_list arguments, void *context)
{
    (void)context;
    (void)vsnprintf(last_log, sizeof(last_log), format, arguments);
    log_calls++;
}

static TF_Result host_listener(TinyFrame *tf, TF_Msg *msg)
{
    (void)msg;
    listener_calls++;
    callback_pointer_matches = tf == active_tf;
    return TF_STAY;
}

static TF_Result host_query_listener(TinyFrame *tf, TF_Msg *msg)
{
    (void)tf;
    (void)msg;
    return TF_CLOSE;
}

static TF_Result host_timeout(TinyFrame *tf)
{
    timeout_calls++;
    callback_pointer_matches = tf == active_tf;
    return TF_CLOSE;
}

void tinyframe_host_reset_capture(void)
{
    capture_length = 0U;
    write_timeout = 0U;
    write_calls = 0U;
    log_calls = 0U;
    last_log[0] = '\0';
}

int tinyframe_host_start(unsigned peer_bit)
{
    struct open_cfw_tinyframe_g2_ports ports;
    memset(&ports, 0, sizeof(ports));
    ports.allocate = host_allocate;
    ports.release = host_release;
    ports.write = host_write;
    ports.vlog = host_vlog;
    open_cfw_tinyframe_g2_configure(&ports);
    active_tf = open_cfw_tinyframe_g2_init(
        peer_bit == 0U ? TF_SLAVE : TF_MASTER
    );
    return active_tf != (TinyFrame *)0;
}

void tinyframe_host_stop(void)
{
    open_cfw_tinyframe_g2_deinit(active_tf);
    active_tf = (TinyFrame *)0;
}

int tinyframe_host_send(uint16_t type, const uint8_t *data, uint16_t length)
{
    TF_Msg msg;
    TF_ClearMsg(&msg);
    msg.type = type;
    msg.data = data;
    msg.len = length;
    return TF_Send(active_tf, &msg);
}

int tinyframe_host_add_listener(uint16_t type)
{
    listener_calls = 0U;
    callback_pointer_matches = 0;
    return TF_AddTypeListener(active_tf, type, host_listener);
}

void tinyframe_host_accept(const uint8_t *data, uint32_t length)
{
    TF_Accept(active_tf, data, length);
}

int tinyframe_host_query_timeout(uint16_t type, uint16_t ticks)
{
    TF_Msg msg;
    TF_ClearMsg(&msg);
    msg.type = type;
    timeout_calls = 0U;
    callback_pointer_matches = 0;
    return TF_Query(
        active_tf,
        &msg,
        host_query_listener,
        host_timeout,
        ticks
    );
}

void tinyframe_host_tick(void)
{
    TF_Tick(active_tf);
}

const uint8_t *tinyframe_host_capture(void) { return capture; }
size_t tinyframe_host_capture_length(void) { return capture_length; }
uint32_t tinyframe_host_write_timeout(void) { return write_timeout; }
unsigned tinyframe_host_write_calls(void) { return write_calls; }
unsigned tinyframe_host_listener_calls(void) { return listener_calls; }
unsigned tinyframe_host_timeout_calls(void) { return timeout_calls; }
int tinyframe_host_callback_pointer_matches(void) { return callback_pointer_matches; }
unsigned tinyframe_host_log_calls(void) { return log_calls; }
const char *tinyframe_host_last_log(void) { return last_log; }
uintptr_t tinyframe_host_core_delta(void)
{
    return (uintptr_t)(void *)active_tf - (uintptr_t)allocation_base;
}
size_t tinyframe_host_allocation_size(void) { return allocation_size; }
size_t tinyframe_host_expected_core_delta(void)
{
    return open_cfw_tinyframe_g2_core_offset();
}
size_t tinyframe_host_expected_allocation_size(void)
{
    return open_cfw_tinyframe_g2_storage_size();
}
uint32_t tinyframe_host_prefix(void)
{
    return open_cfw_tinyframe_g2_prefix(active_tf);
}
uint32_t tinyframe_host_suffix(void)
{
    return open_cfw_tinyframe_g2_suffix(active_tf);
}
