#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "service_touch_dfu_host.h"

uint32_t open_cfw_touch_crc32c(const uint8_t *data, uint32_t size);

uintptr_t touch_dfu_ops_words[4];
uintptr_t touch_dfu_file_handle;
uint8_t *touch_dfu_firmware_buffer;
uint32_t touch_dfu_firmware_size;
uint32_t touch_dfu_current_version_cache;

static uint8_t package_data[2048];
static uint8_t transmitted[32768];
static uint32_t package_size;
static uint32_t file_position;
static uint32_t transmitted_size;
static uint32_t close_count;
static uint32_t reset_count;
static uint32_t switch_count;
static uint32_t delay_total;
static uint32_t running_version;
static int fail_allocate;
static int fail_switch;
static int fail_version;
static int auto_reply;
static uint8_t last_command;

static void put16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static void put32(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

static uint16_t checksum16(const uint8_t *data, uint32_t size)
{
    uint16_t sum = 0u;
    uint32_t index;
    for (index = 0u; index < size; ++index) sum = (uint16_t)(sum + data[index]);
    return (uint16_t)(0u - sum);
}

static int32_t host_raw_write(const void *pointer, uint16_t size)
{
    const uint8_t *data = (const uint8_t *)pointer;
    if (pointer == NULL || transmitted_size + size > sizeof(transmitted)) return -1;
    if (size >= 2u) last_command = data[1];
    memcpy(transmitted + transmitted_size, data, size);
    transmitted_size += size;
    return 0;
}

static int32_t host_raw_read(void *pointer, uint16_t size)
{
    uint8_t *reply = (uint8_t *)pointer;
    uint16_t checksum;
    if (!auto_reply || pointer == NULL || size < 15u) return -1;
    memset(reply, 0, size);
    reply[0] = 1u;
    reply[1] = last_command;
    put16(reply + 2, 0u);
    checksum = checksum16(reply, 4u);
    put16(reply + 4, checksum);
    reply[6] = 0x17u;
    return 0;
}

void host_touch_reset(void)
{
    free(touch_dfu_firmware_buffer);
    touch_dfu_file_handle = 0u;
    touch_dfu_firmware_buffer = NULL;
    touch_dfu_firmware_size = 0u;
    touch_dfu_current_version_cache = 0u;
    package_size = 0u;
    file_position = 0u;
    transmitted_size = 0u;
    close_count = 0u;
    reset_count = 0u;
    switch_count = 0u;
    delay_total = 0u;
    running_version = 0x01020304u;
    fail_allocate = 0;
    fail_switch = 0;
    fail_version = 0;
    auto_reply = 1;
    last_command = 0u;
    touch_dfu_ops_words[0] = 0u;
    touch_dfu_ops_words[1] = 0u;
    touch_dfu_ops_words[2] = (uintptr_t)&host_raw_write;
    touch_dfu_ops_words[3] = (uintptr_t)&host_raw_read;
}

void host_touch_make_package(int corrupt_crc, int omit_touch)
{
    uint32_t payload_offset = 32u;
    uint32_t payload_size = 132u;
    uint32_t index;
    memset(package_data, 0, sizeof(package_data));
    put32(package_data, 0x4b505746u);
    put32(package_data + 4, 0x01020304u);
    put32(package_data + 8, 1u);
    put32(package_data + 12, 0u);
    put32(package_data + 16, omit_touch ? 2u : 3u);
    put32(package_data + 20, payload_size);
    put32(package_data + 24, payload_offset);
    for (index = 0u; index < payload_size - 4u; ++index)
        package_data[payload_offset + index] = (uint8_t)(index + 1u);
    put32(package_data + payload_offset + payload_size - 4u, 0xa1b2c3d4u);
    put32(package_data + 28,
        open_cfw_touch_crc32c(package_data + payload_offset, payload_size) +
        (uint32_t)corrupt_crc);
    package_size = payload_offset + payload_size;
}

void host_touch_set_failures(int allocate, int switch_dfu, int version)
{
    fail_allocate = allocate;
    fail_switch = switch_dfu;
    fail_version = version;
}

void host_touch_set_auto_reply(int enabled) { auto_reply = enabled; }
void host_touch_set_running_version(uint32_t version) { running_version = version; }
void host_touch_clear_tx(void) { transmitted_size = 0u; }
uint32_t host_touch_tx_size(void) { return transmitted_size; }
uint32_t host_touch_close_count(void) { return close_count; }
uint32_t host_touch_reset_count(void) { return reset_count; }
uint32_t host_touch_switch_count(void) { return switch_count; }
uint32_t host_touch_delay_total(void) { return delay_total; }
uint32_t host_touch_copy_tx(uint8_t *destination, uint32_t capacity)
{
    uint32_t count = transmitted_size;
    if (count > capacity) count = capacity;
    memcpy(destination, transmitted, count);
    return count;
}

uintptr_t host_touch_file_open(const char *path, const char *mode)
{
    file_position = 0u;
    return path != NULL && mode != NULL && strcmp(path, "/firmware/touch.bin") == 0 &&
        strcmp(mode, "rb") == 0 && package_size != 0u ? 1u : 0u;
}

uint32_t host_touch_file_read(void *data, uint32_t element_size,
    uint32_t element_count, uintptr_t file)
{
    uint32_t wanted;
    uint32_t count;
    if (file != 1u || element_size == 0u) return 0u;
    wanted = element_size * element_count;
    count = package_size - file_position;
    if (count > wanted) count = wanted;
    memcpy(data, package_data + file_position, count);
    file_position += count;
    return count / element_size;
}

int32_t host_touch_file_seek(uintptr_t file, int32_t offset, uint32_t origin)
{
    if (file != 1u || origin != 0u || offset < 0 ||
        (uint32_t)offset > package_size) return -1;
    file_position = (uint32_t)offset;
    return 0;
}

void host_touch_file_close(uintptr_t file) { (void)file; ++close_count; }
void *host_touch_allocate(uint32_t size) { return fail_allocate ? NULL : malloc(size); }
void host_touch_free(void *pointer) { free(pointer); }
void host_touch_delay(uint32_t ticks) { delay_total += ticks; }
void host_touch_reset_controller(void) { ++reset_count; }
int32_t host_touch_switch_to_dfu(void) { ++switch_count; return fail_switch ? -1 : 0; }
int32_t host_touch_read_current_version(uint32_t *version)
{
    if (fail_version || version == NULL) return -1;
    *version = running_version;
    return 0;
}
