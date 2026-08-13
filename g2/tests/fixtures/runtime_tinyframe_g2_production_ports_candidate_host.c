#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

#include "../../components/shared/tinyframe/runtime_tinyframe_g2_adapter_candidate.h"

static struct open_cfw_tinyframe_g2_ports host_ports;
static uint32_t host_peer;
static uint32_t host_malloc_size;
static uintptr_t host_free_pointer;
static uintptr_t host_write_buffer;
static uint32_t host_write_length;
static uint32_t host_write_timeout;

void open_cfw_tinyframe_g2_configure(
    const struct open_cfw_tinyframe_g2_ports *ports
) { host_ports = *ports; }

TinyFrame *open_cfw_tinyframe_g2_init(TF_Peer peer_bit)
{
    host_peer = (uint32_t)peer_bit;
    return (TinyFrame *)(uintptr_t)0x12345678U;
}

void *open_cfw_freertos_heap4_malloc(uint32_t size)
{
    host_malloc_size = size;
    return (void *)(uintptr_t)0x20001000U;
}

void open_cfw_freertos_heap4_free(void *allocation)
{
    host_free_pointer = (uintptr_t)allocation;
}

int32_t open_cfw_retained_sync_transport_write(
    const uint8_t *buffer, uint32_t length, uint32_t timeout
)
{
    host_write_buffer = (uintptr_t)buffer;
    host_write_length = length;
    host_write_timeout = timeout;
    return -1;
}

#include "../../components/shared/tinyframe/runtime_tinyframe_g2_production_ports_candidate.c"

void open_cfw_tinyframe_g2_production_host_reset(void)
{
    host_peer = host_malloc_size = host_write_length = host_write_timeout = 0;
    host_free_pointer = host_write_buffer = 0;
}

uintptr_t open_cfw_tinyframe_g2_production_host_init(uint32_t peer)
{
    return (uintptr_t)open_cfw_tinyframe_g2_init_production((TF_Peer)peer);
}

static void open_cfw_tinyframe_g2_production_host_vlog(
    const char *format,
    ...
)
{
    va_list arguments;
    va_start(arguments, format);
    host_ports.vlog(format, arguments, host_ports.context);
    va_end(arguments);
}

void open_cfw_tinyframe_g2_production_host_exercise(void)
{
    (void)host_ports.allocate(0x7160U, host_ports.context);
    host_ports.release((void *)(uintptr_t)0x20001000U, host_ports.context);
    host_ports.write((const uint8_t *)(uintptr_t)0x20002000U, 0x123U, 100U,
                     host_ports.context);
    open_cfw_tinyframe_g2_production_host_vlog("ignored");
}

uintptr_t open_cfw_tinyframe_g2_production_host_get(uint32_t index)
{
    const uintptr_t values[] = {
        host_peer, host_malloc_size, host_free_pointer, host_write_buffer,
        host_write_length, host_write_timeout,
        (uintptr_t)host_ports.allocate, (uintptr_t)host_ports.release,
        (uintptr_t)host_ports.write, (uintptr_t)host_ports.vlog
    };
    return index < sizeof(values) / sizeof(values[0]) ? values[index] : 0;
}
