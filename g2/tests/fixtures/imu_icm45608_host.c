#include "imu_icm45608_host.h"

#include <stdio.h>
#include <string.h>

struct open_cfw_imu_fusion_result;

uint64_t host_imu_device_words[12];
uint64_t host_imu_ring_words[282];
uint64_t host_imu_mode_words[10];
int32_t host_imu_accel_offset[3];
int32_t host_imu_gyro_offset[3];
int32_t host_imu_mag_offset[3];
float host_imu_orientation[9];
int16_t host_imu_orientation_q14[9];
int32_t host_imu_orientation_q30[9];
uint32_t host_imu_accel_interval;
int32_t host_imu_motion_threshold;
uint32_t host_imu_motion_period;
int32_t host_imu_heading_period;
float host_imu_heading;
float host_imu_magnetic[3];
float host_imu_orientation_vector[3];
uint32_t host_imu_raw_handle;
uint32_t host_imu_raw_count;
uint32_t host_imu_raw_started;
uint8_t host_imu_raw_active;
uint32_t host_imu_forward_divisor;
float host_imu_latest_result[9];
uint8_t host_imu_mode;
uint8_t host_imu_aid_enabled;
uint8_t host_imu_compass_ready;
uint8_t host_imu_compass_reported;
uint8_t host_imu_head_up_armed;
uint32_t host_imu_state_zero;
uint32_t host_imu_state_one;
uint32_t host_imu_state_two;
uint32_t host_imu_state_three;
uint8_t host_imu_odr_accel;
uint8_t host_imu_odr_gyro;
uint8_t host_imu_odr_index;
uint8_t host_imu_feature_enable;
uint32_t host_imu_fifo_watermark;
uint16_t host_imu_interrupt_period;

int32_t host_imu_i2c_read_status;
int32_t host_imu_i2c_write_status;
uint8_t host_imu_i2c_read_data[32];
uint8_t host_imu_registers[256];
uint8_t host_imu_i2c_last_register;
uint8_t host_imu_i2c_last_write[16];
uint32_t host_imu_i2c_last_write_size;
uint8_t host_imu_fifo_mirror[2048];
uint32_t host_imu_i2c_bus;
uint32_t host_imu_i2c_address;
uint32_t host_imu_i2c_count;
uint32_t host_imu_power_count;
uint32_t host_imu_power_sensor;
uint32_t host_imu_power_enabled;
uint32_t host_imu_delay_ticks;
uint32_t host_imu_tick;
int32_t host_imu_context_status;
int32_t host_imu_fifo_status;
int32_t host_imu_configure_status;
int32_t host_imu_poll_status;
uint8_t host_imu_poll_packet[41];
uint8_t host_imu_poll_has_packet;
int32_t host_imu_fusion_status;
uint8_t host_imu_fusion_result[84];
uint16_t host_imu_fifo_frame_count;
uint32_t host_imu_configure_count;
uint8_t host_imu_configure_accel_odr;
uint8_t host_imu_configure_gyro_odr;
uint16_t host_imu_configure_watermark;
uint32_t host_imu_configure_period_us;
uint8_t host_imu_configure_fusion_enabled;
uint8_t host_imu_configure_extended_enabled;
int8_t host_imu_configure_mounting_matrix[9];
int32_t host_imu_extended_status;
uint8_t host_imu_extended_events;
uint8_t host_imu_extended_aid_human;
uint8_t host_imu_extended_aid_device;
uint32_t host_imu_extended_read_count;
uint32_t host_imu_event_count;
uint32_t host_imu_event_id;
int32_t host_imu_event_value;
uint32_t host_imu_forward_count;
float host_imu_forward_value[3];
int32_t host_imu_raw_open_status;
int32_t host_imu_raw_write_status;
int32_t host_imu_raw_close_status;
uint32_t host_imu_raw_open_count;
uint32_t host_imu_raw_write_count;
uint32_t host_imu_raw_close_count;
uint32_t host_imu_raw_written_bytes;
char host_imu_raw_last_path[32];
uint8_t host_imu_who_value;
uint8_t host_mag_who_value;
int32_t host_imu_who_status;
int32_t host_mag_who_status;
uint32_t host_imu_aid_changed_count;

struct host_imu_mode {
    uint8_t features;
    uint8_t reserved[3];
    uint32_t period_us;
    uint32_t fifo_watermark;
    uint32_t interrupt_period;
};

void host_imu_reset(void)
{
    struct host_imu_mode *modes = (struct host_imu_mode *)(void *)host_imu_mode_words;
    uint32_t index;
    memset(host_imu_device_words, 0, sizeof(host_imu_device_words));
    memset(host_imu_ring_words, 0, sizeof(host_imu_ring_words));
    memset(host_imu_mode_words, 0, sizeof(host_imu_mode_words));
    for (index = 0u; index < 5u; ++index) {
        modes[index].features = 3u;
        modes[index].period_us = 10000u;
        modes[index].fifo_watermark = 8u;
        modes[index].interrupt_period = 10u;
    }
    memset(host_imu_accel_offset, 0, sizeof(host_imu_accel_offset));
    memset(host_imu_gyro_offset, 0, sizeof(host_imu_gyro_offset));
    memset(host_imu_mag_offset, 0, sizeof(host_imu_mag_offset));
    memset(host_imu_orientation, 0, sizeof(host_imu_orientation));
    memset(host_imu_orientation_q14, 0, sizeof(host_imu_orientation_q14));
    memset(host_imu_orientation_q30, 0, sizeof(host_imu_orientation_q30));
    host_imu_orientation[0] = host_imu_orientation[4] = host_imu_orientation[8] = 1.0f;
    host_imu_orientation_q14[0] = host_imu_orientation_q14[4] =
        host_imu_orientation_q14[8] = 16384;
    host_imu_orientation_q30[0] = host_imu_orientation_q30[4] = host_imu_orientation_q30[8] = 0x3f800000;
    host_imu_accel_interval = 100u;
    host_imu_motion_threshold = 30;
    host_imu_motion_period = 1000u;
    host_imu_heading_period = 15;
    host_imu_heading = 0.0f;
    memset(host_imu_magnetic, 0, sizeof(host_imu_magnetic));
    memset(host_imu_orientation_vector, 0, sizeof(host_imu_orientation_vector));
    host_imu_raw_handle = host_imu_raw_count = host_imu_raw_started = 0u;
    host_imu_raw_active = 0u;
    host_imu_forward_divisor = 0u;
    memset(host_imu_latest_result, 0, sizeof(host_imu_latest_result));
    host_imu_mode = host_imu_aid_enabled = host_imu_compass_ready = 0u;
    host_imu_compass_reported = 0u; host_imu_head_up_armed = 1u;
    host_imu_state_zero = host_imu_state_one = host_imu_state_two = host_imu_state_three = 0u;
    host_imu_odr_accel = host_imu_odr_gyro = host_imu_odr_index = host_imu_feature_enable = 0u;
    host_imu_fifo_watermark = 0u; host_imu_interrupt_period = 0u;
    host_imu_i2c_read_status = host_imu_i2c_write_status = 0;
    memset(host_imu_i2c_read_data, 0, sizeof(host_imu_i2c_read_data));
    memset(host_imu_registers, 0, sizeof(host_imu_registers));
    host_imu_registers[0x72] = 0x81u;
    host_imu_registers[0x19] = 0x80u;
    host_imu_i2c_last_register = 0u;
    memset(host_imu_i2c_last_write, 0, sizeof(host_imu_i2c_last_write));
    memset(host_imu_fifo_mirror, 0, sizeof(host_imu_fifo_mirror));
    host_imu_i2c_last_write_size = 0u;
    host_imu_i2c_bus = host_imu_i2c_address = host_imu_i2c_count = 0u;
    host_imu_power_count = host_imu_power_sensor = host_imu_power_enabled = 0u;
    host_imu_delay_ticks = host_imu_tick = 0u;
    host_imu_context_status = host_imu_fifo_status = host_imu_configure_status = host_imu_poll_status = 0;
    memset(host_imu_poll_packet, 0, sizeof(host_imu_poll_packet)); host_imu_poll_has_packet = 0u;
    host_imu_fusion_status = -1; memset(host_imu_fusion_result, 0, sizeof(host_imu_fusion_result));
    host_imu_fifo_frame_count = 0u;
    host_imu_configure_count = 0u;
    host_imu_configure_accel_odr = host_imu_configure_gyro_odr = 0u;
    host_imu_configure_watermark = 0u;
    host_imu_configure_period_us = 0u;
    host_imu_configure_fusion_enabled = 0u;
    host_imu_configure_extended_enabled = 0u;
    memset(host_imu_configure_mounting_matrix, 0,
           sizeof(host_imu_configure_mounting_matrix));
    host_imu_extended_status = 0;
    host_imu_extended_events = 0u;
    host_imu_extended_aid_human = 0u;
    host_imu_extended_aid_device = 0u;
    host_imu_extended_read_count = 0u;
    host_imu_event_count = host_imu_event_id = 0u; host_imu_event_value = 0;
    host_imu_forward_count = 0u; memset(host_imu_forward_value, 0, sizeof(host_imu_forward_value));
    host_imu_raw_open_status = host_imu_raw_write_status = host_imu_raw_close_status = 0;
    host_imu_raw_open_count = host_imu_raw_write_count = host_imu_raw_close_count = 0u;
    host_imu_raw_written_bytes = 0u; memset(host_imu_raw_last_path, 0, sizeof(host_imu_raw_last_path));
    host_imu_who_value = 0xe9u; host_mag_who_value = 0x90u;
    host_imu_who_status = host_mag_who_status = 0; host_imu_aid_changed_count = 0u;
}

int32_t open_cfw_retained_imu_i2c_read(
    uint32_t bus, uint32_t address, const void *register_data,
    uint32_t register_size, void *data, uint32_t size)
{
    host_imu_i2c_bus = bus;
    host_imu_i2c_address = address;
    host_imu_i2c_count = register_size;
    if (register_size != 0u)
        host_imu_i2c_last_register = *(const uint8_t *)register_data;
    if (host_imu_i2c_read_status == 0) {
        uint32_t copied = size < sizeof(host_imu_i2c_read_data)
                              ? size : sizeof(host_imu_i2c_read_data);
        uint32_t available = 256u - host_imu_i2c_last_register;
        if (copied > available) copied = available;
        memcpy(data, &host_imu_registers[host_imu_i2c_last_register], copied);
    }
    return host_imu_i2c_read_status;
}
int32_t open_cfw_retained_imu_i2c_write(
    uint32_t bus, uint32_t address, const void *register_data,
    uint32_t register_size, const void *data, uint32_t size)
{
    host_imu_i2c_bus = bus;
    host_imu_i2c_address = address;
    host_imu_i2c_count = register_size;
    if (register_size != 0u)
        host_imu_i2c_last_register = *(const uint8_t *)register_data;
    host_imu_i2c_last_write_size = size < sizeof(host_imu_i2c_last_write)
                                       ? size : sizeof(host_imu_i2c_last_write);
    memcpy(host_imu_i2c_last_write, data, host_imu_i2c_last_write_size);
    if (host_imu_i2c_last_write_size <=
        256u - host_imu_i2c_last_register) {
        memcpy(&host_imu_registers[host_imu_i2c_last_register], data,
               host_imu_i2c_last_write_size);
    }
    return host_imu_i2c_write_status;
}
void open_cfw_retained_imu_power(uint32_t sensor, uint32_t enabled)
{ ++host_imu_power_count; host_imu_power_sensor = sensor; host_imu_power_enabled = enabled; }
void open_cfw_retained_imu_delay(uint32_t ticks) { host_imu_delay_ticks = ticks; }
uint32_t open_cfw_retained_imu_tick(void) { return host_imu_tick; }
int32_t open_cfw_retained_imu_vendor_context_init(void *device) { (void)device; return host_imu_context_status; }
int32_t open_cfw_retained_imu_vendor_fifo_init(void *device, uint32_t type, const void *configuration)
{ (void)device; (void)type; (void)configuration; return host_imu_fifo_status; }
int32_t open_cfw_icm45608_tdk_configure(
    void *device, uint8_t accel_odr, uint8_t gyro_odr, uint16_t watermark,
    uint32_t period_us, uint8_t fusion_enabled, uint8_t extended_enabled,
    const int8_t mounting_matrix[9])
{
    (void)device;
    ++host_imu_configure_count;
    host_imu_configure_accel_odr = accel_odr;
    host_imu_configure_gyro_odr = gyro_odr;
    host_imu_configure_watermark = watermark;
    host_imu_configure_period_us = period_us;
    host_imu_configure_fusion_enabled = fusion_enabled;
    host_imu_configure_extended_enabled = extended_enabled;
    memcpy(host_imu_configure_mounting_matrix, mounting_matrix, 9u);
    return host_imu_configure_status;
}
int32_t open_cfw_icm45608_tdk_read_fifo(
    void *device, uint8_t *buffer, uint32_t capacity, uint16_t *frame_count)
{
    (void)device; (void)buffer;
    if (capacity < (uint32_t)host_imu_fifo_frame_count * 41u)
        return -1;
    if (host_imu_fifo_status == 0)
        *frame_count = host_imu_fifo_frame_count;
    return host_imu_fifo_status;
}
int32_t open_cfw_icm45608_tdk_parse_fifo(
    void *device, const uint8_t *buffer, uint16_t frame_count)
{
    uint16_t frame;
    (void)device;
    if (host_imu_fifo_status != 0)
        return host_imu_fifo_status;
    for (frame = 0u; frame < frame_count; ++frame)
        open_cfw_imu_data_parser_callback(buffer + (uint32_t)frame * 41u);
    return 0;
}
int32_t open_cfw_icm45608_tdk_poll_registers(void *device)
{
    (void)device;
    if (host_imu_poll_status == 0 && host_imu_poll_has_packet != 0u)
        open_cfw_imu_data_parser_callback(host_imu_poll_packet);
    return host_imu_poll_status;
}
int32_t open_cfw_icm45608_tdk_read_extended_events(
    void *device, uint8_t *events, uint8_t *aid_human,
    uint8_t *aid_device)
{
    (void)device;
    ++host_imu_extended_read_count;
    if (host_imu_extended_status == 0) {
        *events = host_imu_extended_events;
        *aid_human = host_imu_extended_aid_human;
        *aid_device = host_imu_extended_aid_device;
    }
    return host_imu_extended_status;
}
int32_t open_cfw_icm45608_tdk_decode_gaf(
    void *device, const uint8_t first[9], const uint8_t second[6],
    struct open_cfw_imu_fusion_result *result)
{
    (void)device; (void)first; (void)second;
    memcpy(result, host_imu_fusion_result, sizeof(host_imu_fusion_result));
    return host_imu_fusion_status;
}
int32_t open_cfw_icm45608_tdk_mag_who_am_i(void *device, uint8_t *value)
{
    (void)device;
    if (host_mag_who_status == 0) *value = host_mag_who_value;
    return host_mag_who_status;
}
uint16_t open_cfw_retained_imu_event_source(void) { return 3u; }
int32_t open_cfw_retained_imu_event_available(void) { return 1; }
void open_cfw_retained_imu_event_dispatch(uint16_t source, uint32_t event,
                                           int32_t value, uint32_t flags)
{ (void)source; (void)flags; ++host_imu_event_count; host_imu_event_id = event; host_imu_event_value = value; }
void open_cfw_retained_imu_forward(float x, float y, float z)
{ ++host_imu_forward_count; host_imu_forward_value[0] = x; host_imu_forward_value[1] = y; host_imu_forward_value[2] = z; }
uint32_t open_cfw_retained_imu_raw_open(const char *path, const char *mode)
{ (void)mode; ++host_imu_raw_open_count; snprintf(host_imu_raw_last_path, sizeof(host_imu_raw_last_path), "%s", path); return host_imu_raw_open_status == 0 ? 7u : 0u; }
int32_t open_cfw_retained_imu_raw_write(const void *data, uint32_t item_size,
                                         uint32_t count, uint32_t handle)
{ (void)handle; (void)data; ++host_imu_raw_write_count; host_imu_raw_written_bytes += item_size * count; return host_imu_raw_write_status == 0 ? (int32_t)count : host_imu_raw_write_status; }
int32_t open_cfw_retained_imu_raw_close(uint32_t handle)
{ (void)handle; ++host_imu_raw_close_count; return host_imu_raw_close_status; }
int32_t open_cfw_retained_imu_who_am_i(void *device, uint8_t *value)
{ (void)device; if (host_imu_who_status == 0) *value = host_imu_who_value; return host_imu_who_status; }
int32_t open_cfw_retained_mag_who_am_i(uint8_t *value)
{ if (host_mag_who_status == 0) *value = host_mag_who_value; return host_mag_who_status; }
void open_cfw_retained_imu_aid_changed(void) { ++host_imu_aid_changed_count; }
