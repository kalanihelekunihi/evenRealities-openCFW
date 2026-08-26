/*
 * OpenCFW clean-room G2 Ring protocol service.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Recreated from authenticated linked-object behavior and ABI evidence.  No
 * vendor source text is included.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_RING_SERVICE_SELECTOR
#define OPEN_CFW_RING_SERVICE_SELECTOR 0
#endif

typedef void (*open_cfw_ring_service_callback)(uint32_t argument);

#ifndef OPEN_CFW_RING_SERVICE_LAST_TOUCH_TICK
#define OPEN_CFW_RING_SERVICE_LAST_TOUCH_TICK \
    (*(volatile uint32_t *)(uintptr_t)0x20074900u)
#endif
#ifndef OPEN_CFW_RING_SERVICE_WEARING
#define OPEN_CFW_RING_SERVICE_WEARING \
    (*(volatile uint8_t *)(uintptr_t)0x2007500cu)
#endif
#ifndef OPEN_CFW_RING_SERVICE_WEAR_STARTED
#define OPEN_CFW_RING_SERVICE_WEAR_STARTED \
    (*(volatile uint32_t *)(uintptr_t)0x20074904u)
#endif
#ifndef OPEN_CFW_RING_SERVICE_BATTERY_TEMPLATE
#define OPEN_CFW_RING_SERVICE_BATTERY_TEMPLATE \
    (*(const uint32_t *)(uintptr_t)0x0078e464u)
#endif

#ifndef OPEN_CFW_RING_SERVICE_SEND_RAW
int open_cfw_retained_ring_thread_send_raw(const void *data, uint16_t length);
#define OPEN_CFW_RING_SERVICE_SEND_RAW(data, length) \
    open_cfw_retained_ring_thread_send_raw((data), (length))
#endif
#ifndef OPEN_CFW_RING_SERVICE_POST_MESSAGE
int open_cfw_retained_ring_thread_post_message(
    uint32_t event, const void *data, uint16_t length);
#define OPEN_CFW_RING_SERVICE_POST_MESSAGE(event, data, length) \
    open_cfw_retained_ring_thread_post_message((event), (data), (length))
#endif
#ifndef OPEN_CFW_RING_SERVICE_POST_EVENT
void open_cfw_retained_ring_thread_post_event(uint32_t event);
#define OPEN_CFW_RING_SERVICE_POST_EVENT(event) \
    open_cfw_retained_ring_thread_post_event((event))
#endif
#ifndef OPEN_CFW_RING_SERVICE_SET_OWNER
void open_cfw_retained_ring_set_owner(uint8_t owner);
#define OPEN_CFW_RING_SERVICE_SET_OWNER(owner) \
    open_cfw_retained_ring_set_owner((owner))
#endif
#ifndef OPEN_CFW_RING_SERVICE_IN_CASE
uint8_t open_cfw_retained_ring_in_case(void);
#define OPEN_CFW_RING_SERVICE_IN_CASE() open_cfw_retained_ring_in_case()
#endif
#ifndef OPEN_CFW_RING_SERVICE_WEAR_STATUS
uint8_t open_cfw_retained_glasses_wear_status(void);
#define OPEN_CFW_RING_SERVICE_WEAR_STATUS() \
    open_cfw_retained_glasses_wear_status()
#endif
#ifndef OPEN_CFW_RING_SERVICE_IMU_STATUS
uint8_t open_cfw_retained_glasses_imu_status(void);
#define OPEN_CFW_RING_SERVICE_IMU_STATUS() \
    open_cfw_retained_glasses_imu_status()
#endif
#ifndef OPEN_CFW_RING_SERVICE_LCD_STATUS
uint8_t open_cfw_retained_glasses_lcd_status(void);
#define OPEN_CFW_RING_SERVICE_LCD_STATUS() \
    open_cfw_retained_glasses_lcd_status()
#endif
#ifndef OPEN_CFW_RING_SERVICE_SET_PHY
void open_cfw_retained_ring_set_phy(
    uint8_t connection, uint8_t all_phys, uint8_t tx_phys,
    uint8_t rx_phys, uint16_t options);
#define OPEN_CFW_RING_SERVICE_SET_PHY(connection, all_phys, tx, rx, options) \
    open_cfw_retained_ring_set_phy((connection), (all_phys), (tx), (rx), \
                                   (options))
#endif
#ifndef OPEN_CFW_RING_SERVICE_INPUT_EVENT
void open_cfw_retained_ring_input_event(
    uint8_t source, uint8_t event, uint8_t value0, uint8_t value1);
#define OPEN_CFW_RING_SERVICE_INPUT_EVENT(source, event, value0, value1) \
    open_cfw_retained_ring_input_event((source), (event), (value0), (value1))
#endif
#ifndef OPEN_CFW_RING_SERVICE_BATTERY_REPORT
void open_cfw_retained_ring_battery_report(const uint32_t *record);
#define OPEN_CFW_RING_SERVICE_BATTERY_REPORT(record) \
    open_cfw_retained_ring_battery_report((record))
#endif
#ifndef OPEN_CFW_RING_SERVICE_TICK
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_RING_SERVICE_TICK() open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_RING_SERVICE_WEAR_DURATION_REPORT
uint8_t open_cfw_retained_ring_wear_duration_report(
    const void *field, uint8_t present, const uint32_t *duration);
#define OPEN_CFW_RING_SERVICE_WEAR_DURATION_REPORT(field, present, duration) \
    open_cfw_retained_ring_wear_duration_report((field), (present), (duration))
#endif
#ifndef OPEN_CFW_RING_SERVICE_REMOVE
uint8_t open_cfw_event_loop_remove_delayed(
    open_cfw_ring_service_callback callback);
#define OPEN_CFW_RING_SERVICE_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed((callback))
#endif
#ifndef OPEN_CFW_RING_SERVICE_PUSH
void open_cfw_event_loop_push_delayed(
    open_cfw_ring_service_callback callback, uint32_t argument, uint32_t delay);
#define OPEN_CFW_RING_SERVICE_PUSH(callback, argument, delay) \
    open_cfw_event_loop_push_delayed((callback), (argument), (delay))
#endif
#ifndef OPEN_CFW_RING_SERVICE_IS_OWNER
uint32_t open_cfw_retained_ring_is_owner(void);
#define OPEN_CFW_RING_SERVICE_IS_OWNER() open_cfw_retained_ring_is_owner()
#endif
#ifndef OPEN_CFW_RING_SERVICE_NOTIFY_CONNECT
void PB_TxEncodeNotifyRingConnectInfo(uint32_t value);
#define OPEN_CFW_RING_SERVICE_NOTIFY_CONNECT(value) \
    PB_TxEncodeNotifyRingConnectInfo((value))
#endif
#ifndef OPEN_CFW_RING_SERVICE_OWNER_RECONNECT
void open_cfw_retained_ring_owner_reconnect(void);
#define OPEN_CFW_RING_SERVICE_OWNER_RECONNECT() \
    open_cfw_retained_ring_owner_reconnect()
#endif
#ifndef OPEN_CFW_RING_SERVICE_READ_MAC
void open_cfw_retained_ring_read_mac(uint8_t mac[6], uint32_t kind);
#define OPEN_CFW_RING_SERVICE_READ_MAC(mac, kind) \
    open_cfw_retained_ring_read_mac((mac), (kind))
#endif
#ifndef OPEN_CFW_RING_SERVICE_REJECT_MAC
void open_cfw_retained_ring_reject_mac(const uint8_t mac[6]);
#define OPEN_CFW_RING_SERVICE_REJECT_MAC(mac) \
    open_cfw_retained_ring_reject_mac((mac))
#endif

#ifndef OPEN_CFW_RING_SERVICE_CONNECT_NOTIFY_CALLBACK
#define OPEN_CFW_RING_SERVICE_CONNECT_NOTIFY_CALLBACK \
    ((open_cfw_ring_service_callback)(uintptr_t)0x004bc419u)
#endif
#ifndef OPEN_CFW_RING_SERVICE_DOMINANT_CALLBACK
#define OPEN_CFW_RING_SERVICE_DOMINANT_CALLBACK \
    ((open_cfw_ring_service_callback)(uintptr_t)0x004a285du)
#endif
#ifndef OPEN_CFW_RING_SERVICE_TOUCH_ERROR_CALLBACK
#define OPEN_CFW_RING_SERVICE_TOUCH_ERROR_CALLBACK \
    ((open_cfw_ring_service_callback)(uintptr_t)0x00472589u)
#endif
#ifndef OPEN_CFW_RING_SERVICE_OWNER_CONNECT_CALLBACK
#define OPEN_CFW_RING_SERVICE_OWNER_CONNECT_CALLBACK \
    ((open_cfw_ring_service_callback)(uintptr_t)0x0047257du)
#endif
#ifndef OPEN_CFW_RING_SERVICE_WEAR_FIELD
#define OPEN_CFW_RING_SERVICE_WEAR_FIELD ((const void *)(uintptr_t)0x00060102u)
#endif

enum {
    OPEN_CFW_RING_FRAME_PREFIX = 0x1au,
    OPEN_CFW_RING_CMD_TOUCH_ENABLE = 0x85u,
    OPEN_CFW_RING_CMD_TOUCH_REPORT_TIME = 0x8au,
    OPEN_CFW_RING_CMD_BATTERY = 0x8bu,
    OPEN_CFW_RING_CMD_WEAR = 0x8cu,
    OPEN_CFW_RING_CMD_STATUS = 0x89u,
    OPEN_CFW_RING_CMD_HEARTBEAT = 0x94u,
    OPEN_CFW_RING_CMD_INVALID_MAC = 0x96u,
    OPEN_CFW_RING_TOUCH_EVENT = 0x61u,
    OPEN_CFW_RING_TOUCH_DEDUP_TICKS = 100u
};

static __attribute__((unused)) uint16_t open_cfw_ring_service_read_u16(
    const uint8_t *value)
{
    return (uint16_t)value[0] | ((uint16_t)value[1] << 8);
}

static __attribute__((unused)) void open_cfw_ring_service_zero(
    uint8_t *value, size_t length)
{
    while (length != 0u) {
        *value++ = 0u;
        --length;
    }
}

uint32_t open_cfw_ring_service_heartbeat_process(void);
uint32_t open_cfw_ring_service_touch_report_time_process(uint16_t ticks);
int32_t open_cfw_ring_service_post_touch_report_time(uint16_t ticks);
uint32_t open_cfw_ring_service_send_touch_enable(uint8_t enabled);
uint32_t open_cfw_ring_service_send_status_bits(uint8_t bit7, uint8_t bit6);
int32_t open_cfw_ring_service_post_touch_event(uint8_t event);
int32_t open_cfw_ring_service_send_glasses_status_event(void);
uint32_t open_cfw_ring_service_send_pair_request(void);
void open_cfw_ring_service_owner_connect_callback(uint32_t argument);
void open_cfw_ring_service_touch_error_callback(uint32_t argument);
uint32_t open_cfw_ring_service_set_phy_process(uint8_t connection);
void open_cfw_ring_service_post_disconnect_event(void);
int32_t open_cfw_ring_service_cmd_hid(const uint8_t *packet);
int32_t open_cfw_ring_service_cmd_touch_update(
    const uint8_t *packet, uint16_t length);
int32_t open_cfw_ring_service_cmd_battery_report(
    const uint8_t *packet, uint16_t length);
void open_cfw_ring_service_reset_wear_state(void);
void open_cfw_ring_service_cmd_wear_status(const uint8_t *packet);
void open_cfw_ring_service_cmd_package_parse(
    const uint8_t *packet, uint16_t length);

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 1
__attribute__((noinline)) uint32_t open_cfw_ring_service_heartbeat_process(void)
{
    const uint8_t frame[4] = {0u, OPEN_CFW_RING_FRAME_PREFIX,
                              OPEN_CFW_RING_CMD_HEARTBEAT, 1u};
    return (uint32_t)OPEN_CFW_RING_SERVICE_SEND_RAW(frame, sizeof(frame));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 2
__attribute__((noinline)) uint32_t
open_cfw_ring_service_touch_report_time_process(uint16_t ticks)
{
    uint8_t frame[6] = {0u, OPEN_CFW_RING_FRAME_PREFIX,
                        OPEN_CFW_RING_CMD_TOUCH_REPORT_TIME, 1u, 0u, 0u};
    frame[4] = (uint8_t)ticks;
    frame[5] = (uint8_t)(ticks >> 8);
    return (uint32_t)OPEN_CFW_RING_SERVICE_SEND_RAW(frame, sizeof(frame));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 3
__attribute__((noinline)) int32_t
open_cfw_ring_service_post_touch_report_time(uint16_t ticks)
{
    return OPEN_CFW_RING_SERVICE_POST_MESSAGE(0x1000u, &ticks, sizeof(ticks));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 4
__attribute__((noinline)) uint32_t
open_cfw_ring_service_send_touch_enable(uint8_t enabled)
{
    uint8_t frame[8] = {0u, OPEN_CFW_RING_FRAME_PREFIX,
                        OPEN_CFW_RING_CMD_TOUCH_ENABLE, 1u,
                        0u, 0xaau, 0xaau, 0xaau};
    frame[4] = enabled == 0u ? 0xffu : 0u;
    return (uint32_t)OPEN_CFW_RING_SERVICE_SEND_RAW(frame, sizeof(frame));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 5
__attribute__((noinline)) uint32_t
open_cfw_ring_service_send_status_bits(uint8_t bit7, uint8_t bit6)
{
    uint8_t frame[8] = {0u, OPEN_CFW_RING_FRAME_PREFIX,
                        OPEN_CFW_RING_CMD_STATUS, 1u, 0u, 0u, 0u, 0u};
    frame[4] = (uint8_t)((bit7 << 7) | (bit6 << 6));
    return (uint32_t)OPEN_CFW_RING_SERVICE_SEND_RAW(frame, sizeof(frame));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 6
__attribute__((noinline)) int32_t
open_cfw_ring_service_post_touch_event(uint8_t event)
{
    return OPEN_CFW_RING_SERVICE_POST_MESSAGE(0x80u, &event, sizeof(event));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 7
__attribute__((noinline)) int32_t
open_cfw_ring_service_send_glasses_status_event(void)
{
    uint8_t status[2];
    uint8_t in_case = OPEN_CFW_RING_SERVICE_IN_CASE();
    uint8_t wear = OPEN_CFW_RING_SERVICE_WEAR_STATUS();
    uint8_t imu = OPEN_CFW_RING_SERVICE_IMU_STATUS();
    uint8_t lcd = OPEN_CFW_RING_SERVICE_LCD_STATUS();

    status[0] = (imu == 0u || lcd == 2u) ? 1u : 0u;
    if (in_case == 1u) {
        status[0] = 0u;
    }
    status[1] = (in_case != 1u && wear == 1u) ? 1u : 0u;
    return OPEN_CFW_RING_SERVICE_POST_MESSAGE(0x400u, status, sizeof(status));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 8
__attribute__((noinline)) uint32_t open_cfw_ring_service_send_pair_request(void)
{
    const uint8_t frame[4] = {0u, 0x35u, 0x88u, 0u};
    return (uint32_t)OPEN_CFW_RING_SERVICE_SEND_RAW(frame, sizeof(frame));
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 9
__attribute__((noinline)) void
open_cfw_ring_service_owner_connect_callback(uint32_t argument)
{
    (void)argument;
    OPEN_CFW_RING_SERVICE_SET_OWNER(0u);
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 10
__attribute__((noinline)) void
open_cfw_ring_service_touch_error_callback(uint32_t argument)
{
    (void)argument;
    OPEN_CFW_RING_SERVICE_POST_EVENT(0x800u);
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 11
__attribute__((noinline)) uint32_t
open_cfw_ring_service_set_phy_process(uint8_t connection)
{
    OPEN_CFW_RING_SERVICE_SET_PHY(connection, 0u, 4u, 1u, 2u);
    return 0u;
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 12
__attribute__((noinline)) void open_cfw_ring_service_post_disconnect_event(void)
{
    OPEN_CFW_RING_SERVICE_POST_EVENT(0x40u);
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 13
__attribute__((noinline)) int32_t
open_cfw_ring_service_cmd_hid(const uint8_t *packet)
{
    return packet == NULL ? -1 : 0;
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 14
__attribute__((noinline)) int32_t open_cfw_ring_service_cmd_touch_update(
    const uint8_t *packet, uint16_t length)
{
    uint8_t type;
    uint32_t tick;

    if (packet == NULL) {
        return -1;
    }
    type = packet[4];
    if (length >= 11u) {
        tick = (uint32_t)packet[7] | ((uint32_t)packet[8] << 8) |
               ((uint32_t)packet[9] << 16) | ((uint32_t)packet[10] << 24);
        if (type != 8u && OPEN_CFW_RING_SERVICE_LAST_TOUCH_TICK != 0u &&
            tick - OPEN_CFW_RING_SERVICE_LAST_TOUCH_TICK <
                OPEN_CFW_RING_TOUCH_DEDUP_TICKS) {
            return 0;
        }
        OPEN_CFW_RING_SERVICE_LAST_TOUCH_TICK = tick;
    }
    if (packet[3] != 0u) {
        return 0;
    }
    switch (type) {
    case 0u: OPEN_CFW_RING_SERVICE_INPUT_EVENT(4u, 3u, 0u, 0u); break;
    case 1u: OPEN_CFW_RING_SERVICE_INPUT_EVENT(4u, 0u, 0u, 0u); break;
    case 2u: OPEN_CFW_RING_SERVICE_INPUT_EVENT(4u, 1u, 0u, 0u); break;
    case 4u:
        OPEN_CFW_RING_SERVICE_INPUT_EVENT(4u, 5u, packet[5], packet[6]);
        break;
    case 5u:
        OPEN_CFW_RING_SERVICE_INPUT_EVENT(4u, 4u, packet[5], packet[6]);
        break;
    case 8u: OPEN_CFW_RING_SERVICE_INPUT_EVENT(4u, 14u, 0u, 0u); break;
    default: break;
    }
    return 0;
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 15
__attribute__((noinline)) int32_t open_cfw_ring_service_cmd_battery_report(
    const uint8_t *packet, uint16_t length)
{
    uint32_t record[2];

    if (packet == NULL || length < 6u) {
        return -1;
    }
    record[0] = 0x00020004u;
    record[1] = (OPEN_CFW_RING_SERVICE_BATTERY_TEMPLATE & 0xffff0000u) |
                open_cfw_ring_service_read_u16(packet + 4u);
    OPEN_CFW_RING_SERVICE_BATTERY_REPORT(record);
    return 0;
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 16
__attribute__((noinline)) void open_cfw_ring_service_reset_wear_state(void)
{
    OPEN_CFW_RING_SERVICE_WEARING = 0u;
    OPEN_CFW_RING_SERVICE_WEAR_STARTED = 0u;
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 17
__attribute__((noinline)) void
open_cfw_ring_service_cmd_wear_status(const uint8_t *packet)
{
    uint8_t wearing;
    uint32_t now;
    uint32_t duration;

    if (packet == NULL) {
        return;
    }
    wearing = packet[4] != 0u ? 1u : 0u;
    if (wearing == OPEN_CFW_RING_SERVICE_WEARING) {
        return;
    }
    OPEN_CFW_RING_SERVICE_WEARING = wearing;
    if (wearing != 0u) {
        OPEN_CFW_RING_SERVICE_WEAR_STARTED = OPEN_CFW_RING_SERVICE_TICK();
    } else if (OPEN_CFW_RING_SERVICE_WEAR_STARTED != 0u) {
        now = OPEN_CFW_RING_SERVICE_TICK();
        duration = now - OPEN_CFW_RING_SERVICE_WEAR_STARTED;
        (void)OPEN_CFW_RING_SERVICE_WEAR_DURATION_REPORT(
            OPEN_CFW_RING_SERVICE_WEAR_FIELD, 1u, &duration);
        OPEN_CFW_RING_SERVICE_WEAR_STARTED = 0u;
    }
}
#endif

#if OPEN_CFW_RING_SERVICE_SELECTOR == 0 || OPEN_CFW_RING_SERVICE_SELECTOR == 18
__attribute__((noinline)) void open_cfw_ring_service_cmd_package_parse(
    const uint8_t *packet, uint16_t length)
{
    uint8_t mac[6];

    if (packet == NULL || length < 5u) {
        return;
    }
    switch (packet[2]) {
    case OPEN_CFW_RING_TOUCH_EVENT:
        (void)open_cfw_ring_service_cmd_touch_update(packet, length);
        break;
    case OPEN_CFW_RING_CMD_TOUCH_ENABLE:
        (void)OPEN_CFW_RING_SERVICE_REMOVE(
            OPEN_CFW_RING_SERVICE_CONNECT_NOTIFY_CALLBACK);
        (void)OPEN_CFW_RING_SERVICE_REMOVE(
            OPEN_CFW_RING_SERVICE_DOMINANT_CALLBACK);
        if (OPEN_CFW_RING_SERVICE_IS_OWNER() == 0u) {
            OPEN_CFW_RING_SERVICE_NOTIFY_CONNECT(0u);
        } else {
            OPEN_CFW_RING_SERVICE_OWNER_RECONNECT();
        }
        (void)open_cfw_ring_service_cmd_hid(packet);
        break;
    case OPEN_CFW_RING_CMD_TOUCH_REPORT_TIME:
        break;
    case OPEN_CFW_RING_CMD_BATTERY:
        (void)open_cfw_ring_service_cmd_battery_report(packet, length);
        break;
    case OPEN_CFW_RING_CMD_WEAR:
        open_cfw_ring_service_cmd_wear_status(packet);
        break;
    case OPEN_CFW_RING_CMD_HEARTBEAT:
        if (packet[4] == 0x20u || packet[4] == 0x40u) {
            (void)OPEN_CFW_RING_SERVICE_REMOVE(
                OPEN_CFW_RING_SERVICE_OWNER_CONNECT_CALLBACK);
            OPEN_CFW_RING_SERVICE_PUSH(
                OPEN_CFW_RING_SERVICE_OWNER_CONNECT_CALLBACK, 0u, 100u);
            (void)OPEN_CFW_RING_SERVICE_REMOVE(
                OPEN_CFW_RING_SERVICE_TOUCH_ERROR_CALLBACK);
            OPEN_CFW_RING_SERVICE_PUSH(
                OPEN_CFW_RING_SERVICE_TOUCH_ERROR_CALLBACK, 0u, 500u);
        }
        break;
    case OPEN_CFW_RING_CMD_INVALID_MAC:
        open_cfw_ring_service_zero(mac, sizeof(mac));
        OPEN_CFW_RING_SERVICE_READ_MAC(mac, 0u);
        OPEN_CFW_RING_SERVICE_REJECT_MAC(mac);
        break;
    default:
        break;
    }
}
#endif
