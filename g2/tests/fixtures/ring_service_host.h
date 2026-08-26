#ifndef OPEN_CFW_RING_SERVICE_HOST_H
#define OPEN_CFW_RING_SERVICE_HOST_H

#include <stdint.h>

extern uint32_t host_ring_service_last_touch_tick;
extern uint8_t host_ring_service_wearing;
extern uint32_t host_ring_service_wear_started;
extern uint32_t host_ring_service_battery_template;

int host_ring_service_send_raw(const void *data, uint16_t length);
int host_ring_service_post_message(
    uint32_t event, const void *data, uint16_t length);
void host_ring_service_post_event(uint32_t event);
void host_ring_service_set_owner(uint8_t owner);
uint8_t host_ring_service_in_case(void);
uint8_t host_ring_service_wear_status(void);
uint8_t host_ring_service_imu_status(void);
uint8_t host_ring_service_lcd_status(void);
void host_ring_service_set_phy(
    uint8_t connection, uint8_t all_phys, uint8_t tx_phys,
    uint8_t rx_phys, uint16_t options);
void host_ring_service_input_event(
    uint8_t source, uint8_t event, uint8_t value0, uint8_t value1);
void host_ring_service_battery_report(const uint32_t *record);
uint32_t host_ring_service_tick(void);
uint8_t host_ring_service_wear_duration_report(
    const void *field, uint8_t present, const uint32_t *duration);
uint8_t host_ring_service_remove(void (*callback)(uint32_t));
void host_ring_service_push(
    void (*callback)(uint32_t), uint32_t argument, uint32_t delay);
uint32_t host_ring_service_is_owner(void);
void host_ring_service_notify_connect(uint32_t value);
void host_ring_service_owner_reconnect(void);
void host_ring_service_read_mac(uint8_t mac[6], uint32_t kind);
void host_ring_service_reject_mac(const uint8_t mac[6]);

#define OPEN_CFW_RING_SERVICE_LAST_TOUCH_TICK \
    host_ring_service_last_touch_tick
#define OPEN_CFW_RING_SERVICE_WEARING host_ring_service_wearing
#define OPEN_CFW_RING_SERVICE_WEAR_STARTED host_ring_service_wear_started
#define OPEN_CFW_RING_SERVICE_BATTERY_TEMPLATE \
    host_ring_service_battery_template
#define OPEN_CFW_RING_SERVICE_SEND_RAW(data, length) \
    host_ring_service_send_raw((data), (length))
#define OPEN_CFW_RING_SERVICE_POST_MESSAGE(event, data, length) \
    host_ring_service_post_message((event), (data), (length))
#define OPEN_CFW_RING_SERVICE_POST_EVENT(event) \
    host_ring_service_post_event((event))
#define OPEN_CFW_RING_SERVICE_SET_OWNER(owner) \
    host_ring_service_set_owner((owner))
#define OPEN_CFW_RING_SERVICE_IN_CASE() host_ring_service_in_case()
#define OPEN_CFW_RING_SERVICE_WEAR_STATUS() host_ring_service_wear_status()
#define OPEN_CFW_RING_SERVICE_IMU_STATUS() host_ring_service_imu_status()
#define OPEN_CFW_RING_SERVICE_LCD_STATUS() host_ring_service_lcd_status()
#define OPEN_CFW_RING_SERVICE_SET_PHY(connection, all_phys, tx, rx, options) \
    host_ring_service_set_phy((connection), (all_phys), (tx), (rx), (options))
#define OPEN_CFW_RING_SERVICE_INPUT_EVENT(source, event, value0, value1) \
    host_ring_service_input_event((source), (event), (value0), (value1))
#define OPEN_CFW_RING_SERVICE_BATTERY_REPORT(record) \
    host_ring_service_battery_report((record))
#define OPEN_CFW_RING_SERVICE_TICK() host_ring_service_tick()
#define OPEN_CFW_RING_SERVICE_WEAR_DURATION_REPORT(field, present, duration) \
    host_ring_service_wear_duration_report((field), (present), (duration))
#define OPEN_CFW_RING_SERVICE_REMOVE(callback) \
    host_ring_service_remove((callback))
#define OPEN_CFW_RING_SERVICE_PUSH(callback, argument, delay) \
    host_ring_service_push((callback), (argument), (delay))
#define OPEN_CFW_RING_SERVICE_IS_OWNER() host_ring_service_is_owner()
#define OPEN_CFW_RING_SERVICE_NOTIFY_CONNECT(value) \
    host_ring_service_notify_connect((value))
#define OPEN_CFW_RING_SERVICE_OWNER_RECONNECT() \
    host_ring_service_owner_reconnect()
#define OPEN_CFW_RING_SERVICE_READ_MAC(mac, kind) \
    host_ring_service_read_mac((mac), (kind))
#define OPEN_CFW_RING_SERVICE_REJECT_MAC(mac) \
    host_ring_service_reject_mac((mac))

#endif
