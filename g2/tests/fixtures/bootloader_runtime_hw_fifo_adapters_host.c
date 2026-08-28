#include <stdint.h>
#include <string.h>

uint32_t open_cfw_hwfa_host_token, open_cfw_hwfa_host_enter_count, open_cfw_hwfa_host_restore_count, open_cfw_hwfa_host_restored_token;
uint32_t open_cfw_hwfa_host_fifo_read_status, open_cfw_hwfa_host_fifo_read_count;
uint8_t open_cfw_hwfa_host_fifo_read_bytes[32];
uint32_t open_cfw_hwfa_host_consume_result, open_cfw_hwfa_host_consume_count, open_cfw_hwfa_host_consume_length;
uint32_t open_cfw_hwfa_host_status_values[32], open_cfw_hwfa_host_status_position;
uint32_t open_cfw_hwfa_host_descriptor_results[32], open_cfw_hwfa_host_descriptor_position;
uint8_t open_cfw_hwfa_host_descriptor_bytes[32];
uint32_t open_cfw_hwfa_host_fifo_write_status, open_cfw_hwfa_host_fifo_write_count;
uint8_t open_cfw_hwfa_host_fifo_write_bytes[32];

uint32_t open_cfw_hwfa_host_critical_enter(void) { open_cfw_hwfa_host_enter_count++; return open_cfw_hwfa_host_token; }
void open_cfw_hwfa_host_critical_restore(uint32_t token) { open_cfw_hwfa_host_restore_count++; open_cfw_hwfa_host_restored_token = token; }
struct open_cfw_hwfa_instance;
uint32_t open_cfw_hwfa_host_fifo_read(struct open_cfw_hwfa_instance *instance, uint8_t *output, uint32_t capacity, uint32_t *count) { uint32_t size = open_cfw_hwfa_host_fifo_read_count < capacity ? open_cfw_hwfa_host_fifo_read_count : capacity; (void)instance; memcpy(output, open_cfw_hwfa_host_fifo_read_bytes, size); *count = size; return open_cfw_hwfa_host_fifo_read_status; }
uint32_t open_cfw_hwfa_host_fifo_write(struct open_cfw_hwfa_instance *instance, const uint8_t *input, uint32_t size, uint32_t *count) { (void)instance; if (size != 0) open_cfw_hwfa_host_fifo_write_bytes[open_cfw_hwfa_host_fifo_write_count] = input[0]; open_cfw_hwfa_host_fifo_write_count += size; *count = size; return open_cfw_hwfa_host_fifo_write_status; }
uint32_t open_cfw_hwfa_host_consume(uint8_t *descriptor, const uint8_t *input, uint32_t size) { (void)descriptor; (void)input; open_cfw_hwfa_host_consume_count++; open_cfw_hwfa_host_consume_length = size; return open_cfw_hwfa_host_consume_result; }
uint32_t open_cfw_hwfa_host_descriptor_read(uint8_t *descriptor, uint8_t *output, uint32_t size) { uint32_t p = open_cfw_hwfa_host_descriptor_position++; (void)descriptor; (void)size; *output = open_cfw_hwfa_host_descriptor_bytes[p]; return open_cfw_hwfa_host_descriptor_results[p]; }
uint32_t open_cfw_hwfa_host_status(uint32_t index) { (void)index; return open_cfw_hwfa_host_status_values[open_cfw_hwfa_host_status_position++]; }

#include "../../components/bootloader/core_overlay/runtime_hw_fifo_adapters_423350.c"
