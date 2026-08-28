#include <stdint.h>

uint32_t open_cfw_hwfifo_host_status_values[64];
uint32_t open_cfw_hwfifo_host_read_values[64];
uint32_t open_cfw_hwfifo_host_status_length, open_cfw_hwfifo_host_read_length;
uint32_t open_cfw_hwfifo_host_status_position, open_cfw_hwfifo_host_read_position;
uint32_t open_cfw_hwfifo_host_write_values[64], open_cfw_hwfifo_host_write_count;
uint32_t open_cfw_hwfifo_host_last_index;

uint32_t open_cfw_hwfifo_host_status(uint32_t index) { uint32_t position = open_cfw_hwfifo_host_status_position++; open_cfw_hwfifo_host_last_index = index; return open_cfw_hwfifo_host_status_values[position < open_cfw_hwfifo_host_status_length ? position : open_cfw_hwfifo_host_status_length]; }
uint32_t open_cfw_hwfifo_host_read(uint32_t index) { uint32_t position = open_cfw_hwfifo_host_read_position++; open_cfw_hwfifo_host_last_index = index; return open_cfw_hwfifo_host_read_values[position < open_cfw_hwfifo_host_read_length ? position : open_cfw_hwfifo_host_read_length]; }
void open_cfw_hwfifo_host_write(uint32_t index, uint32_t value) { open_cfw_hwfifo_host_last_index = index; open_cfw_hwfifo_host_write_values[open_cfw_hwfifo_host_write_count++] = value; }

#include "../../components/bootloader/core_overlay/runtime_hw_fifo_4232c8.c"
#include "../../components/bootloader/core_overlay/runtime_hw_fifo_drain_423342.c"

uint32_t open_cfw_hwfifod_host_read(open_cfw_hwfifod_instance *instance, uint8_t *output, uint32_t capacity, uint32_t *count)
{
    return open_cfw_bootloader_hw_fifo_read_4232c8((open_cfw_hwfifo_instance *)instance, output, capacity, count);
}
