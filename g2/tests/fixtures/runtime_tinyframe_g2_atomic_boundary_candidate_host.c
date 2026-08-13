#include <stddef.h>
#include <stdint.h>

#include "../../components/shared/tinyframe/runtime_tinyframe_g2_adapter_candidate.h"

static union {
    uint64_t alignment;
    uint8_t bytes[0x10000];
} host_storage;
static uint8_t host_capture[0x500];
static uint32_t host_capture_length;
static uint32_t host_allocation_size;
static uint32_t host_write_timeout;
static TinyFrame *host_frame;

void *open_cfw_freertos_heap4_malloc(uint32_t size)
{
    host_allocation_size = size;
    return size <= sizeof(host_storage.bytes) ? host_storage.bytes : (void *)0;
}

void open_cfw_freertos_heap4_free(void *allocation)
{
    (void)allocation;
}

static int32_t host_sync_write(
    const uint8_t *buffer,
    uint32_t length,
    uint32_t timeout
)
{
    uint32_t index;
    host_write_timeout = timeout;
    for (index = 0; index < length && host_capture_length < sizeof(host_capture); ++index) {
        host_capture[host_capture_length++] = buffer[index];
    }
    return -1;
}

#define OPEN_CFW_TINYFRAME_G2_SYNC_WRITE(buffer, length, timeout) \
    host_sync_write((buffer), (length), (timeout))
#include "../../components/shared/tinyframe/runtime_tinyframe_g2_atomic_boundary_candidate.c"

int open_cfw_tinyframe_g2_atomic_host_start(uint32_t peer)
{
    host_capture_length = host_allocation_size = host_write_timeout = 0;
    host_frame = TF_Init((TF_Peer)peer);
    return host_frame != (TinyFrame *)0;
}

int open_cfw_tinyframe_g2_atomic_host_send(
    uint16_t type,
    const uint8_t *payload,
    uint16_t length
)
{
    TF_Msg message = {0};
    message.type = type;
    message.data = payload;
    message.len = length;
    return TF_Send(host_frame, &message);
}

uintptr_t open_cfw_tinyframe_g2_atomic_host_get(uint32_t index)
{
    const uint8_t *core = (const uint8_t *)host_frame;
    const struct open_cfw_tinyframe_g2_atomic_allocation *allocation =
        (const struct open_cfw_tinyframe_g2_atomic_allocation *)(const void *)(
            core - offsetof(struct open_cfw_tinyframe_g2_atomic_allocation, core)
        );
    const uint32_t prefix = allocation->prefix_magic;
    const uint32_t suffix = allocation->suffix_magic;
    const uintptr_t values[] = {
        host_capture_length,
        host_allocation_size,
        host_write_timeout,
        prefix,
        suffix,
        sizeof(*allocation)
    };
    return index < sizeof(values) / sizeof(values[0]) ? values[index] : 0;
}

const uint8_t *open_cfw_tinyframe_g2_atomic_host_capture(void)
{
    return host_capture;
}
