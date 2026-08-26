#include <stdint.h>
#include <string.h>

uint32_t host_ring_service_last_touch_tick;
uint8_t host_ring_service_wearing;
uint32_t host_ring_service_wear_started;
uint32_t host_ring_service_battery_template;
uint8_t host_ring_service_raw[16];
uint16_t host_ring_service_raw_length;
uint32_t host_ring_service_raw_count;
uint8_t host_ring_service_message[16];
uint16_t host_ring_service_message_length;
uint32_t host_ring_service_message_event;
uint32_t host_ring_service_message_count;
uint32_t host_ring_service_posted_event;
uint32_t host_ring_service_posted_event_count;
uint8_t host_ring_service_owner_set;
uint8_t host_ring_service_in_case_value;
uint8_t host_ring_service_wear_status_value;
uint8_t host_ring_service_imu_status_value;
uint8_t host_ring_service_lcd_status_value;
uint8_t host_ring_service_phy[5];
uint8_t host_ring_service_input[4];
uint32_t host_ring_service_input_count;
uint32_t host_ring_service_battery[2];
uint32_t host_ring_service_battery_count;
uint32_t host_ring_service_tick_value;
uint32_t host_ring_service_wear_duration;
uint32_t host_ring_service_wear_report_count;
uintptr_t host_ring_service_wear_field;
uint32_t host_ring_service_remove_count;
uint32_t host_ring_service_push_count;
uintptr_t host_ring_service_callbacks[8];
uint32_t host_ring_service_delays[8];
uint32_t host_ring_service_arguments[8];
uint32_t host_ring_service_owner;
uint32_t host_ring_service_notify_value;
uint32_t host_ring_service_notify_count;
uint32_t host_ring_service_reconnect_count;
uint8_t host_ring_service_mac[6];
uint8_t host_ring_service_rejected_mac[6];
uint32_t host_ring_service_reject_count;

int host_ring_service_send_raw(const void *data, uint16_t length)
{
    if (length > sizeof(host_ring_service_raw)) {
        return -1;
    }
    memcpy(host_ring_service_raw, data, length);
    host_ring_service_raw_length = length;
    ++host_ring_service_raw_count;
    return 0;
}

int host_ring_service_post_message(
    uint32_t event, const void *data, uint16_t length)
{
    if (length > sizeof(host_ring_service_message)) {
        return -1;
    }
    memcpy(host_ring_service_message, data, length);
    host_ring_service_message_length = length;
    host_ring_service_message_event = event;
    ++host_ring_service_message_count;
    return 0;
}

void host_ring_service_post_event(uint32_t event)
{
    host_ring_service_posted_event = event;
    ++host_ring_service_posted_event_count;
}

void host_ring_service_set_owner(uint8_t owner)
{
    host_ring_service_owner_set = owner;
}

uint8_t host_ring_service_in_case(void) { return host_ring_service_in_case_value; }
uint8_t host_ring_service_wear_status(void) { return host_ring_service_wear_status_value; }
uint8_t host_ring_service_imu_status(void) { return host_ring_service_imu_status_value; }
uint8_t host_ring_service_lcd_status(void) { return host_ring_service_lcd_status_value; }

void host_ring_service_set_phy(
    uint8_t connection, uint8_t all_phys, uint8_t tx_phys,
    uint8_t rx_phys, uint16_t options)
{
    host_ring_service_phy[0] = connection;
    host_ring_service_phy[1] = all_phys;
    host_ring_service_phy[2] = tx_phys;
    host_ring_service_phy[3] = rx_phys;
    host_ring_service_phy[4] = (uint8_t)options;
}

void host_ring_service_input_event(
    uint8_t source, uint8_t event, uint8_t value0, uint8_t value1)
{
    host_ring_service_input[0] = source;
    host_ring_service_input[1] = event;
    host_ring_service_input[2] = value0;
    host_ring_service_input[3] = value1;
    ++host_ring_service_input_count;
}

void host_ring_service_battery_report(const uint32_t *record)
{
    host_ring_service_battery[0] = record[0];
    host_ring_service_battery[1] = record[1];
    ++host_ring_service_battery_count;
}

uint32_t host_ring_service_tick(void) { return host_ring_service_tick_value; }

uint8_t host_ring_service_wear_duration_report(
    const void *field, uint8_t present, const uint32_t *duration)
{
    (void)present;
    host_ring_service_wear_field = (uintptr_t)field;
    host_ring_service_wear_duration = *duration;
    ++host_ring_service_wear_report_count;
    return 1u;
}

uint8_t host_ring_service_remove(void (*callback)(uint32_t))
{
    host_ring_service_callbacks[host_ring_service_remove_count] =
        (uintptr_t)callback;
    ++host_ring_service_remove_count;
    return 1u;
}

void host_ring_service_push(
    void (*callback)(uint32_t), uint32_t argument, uint32_t delay)
{
    host_ring_service_callbacks[4u + host_ring_service_push_count] =
        (uintptr_t)callback;
    host_ring_service_arguments[host_ring_service_push_count] = argument;
    host_ring_service_delays[host_ring_service_push_count] = delay;
    ++host_ring_service_push_count;
}

uint32_t host_ring_service_is_owner(void) { return host_ring_service_owner; }

void host_ring_service_notify_connect(uint32_t value)
{
    host_ring_service_notify_value = value;
    ++host_ring_service_notify_count;
}

void host_ring_service_owner_reconnect(void)
{
    ++host_ring_service_reconnect_count;
}

void host_ring_service_read_mac(uint8_t mac[6], uint32_t kind)
{
    (void)kind;
    memcpy(mac, host_ring_service_mac, 6u);
}

void host_ring_service_reject_mac(const uint8_t mac[6])
{
    memcpy(host_ring_service_rejected_mac, mac, 6u);
    ++host_ring_service_reject_count;
}

void PB_TxEncodeNotifyRingConnectInfo(uint32_t value)
{
    host_ring_service_notify_connect(value);
}
