#include <stdint.h>
#include <string.h>

static uint8_t eus_control_bytes[4];
static uint8_t ess_control_bytes[4];
static uint8_t efs_control_bytes[4];
static uint8_t nus_control_bytes[4];

#define OPEN_CFW_BLE_EUS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(void *)eus_control_bytes)
#define OPEN_CFW_BLE_ESS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(void *)ess_control_bytes)
#define OPEN_CFW_BLE_EFS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(void *)efs_control_bytes)
#define OPEN_CFW_BLE_NUS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(void *)nus_control_bytes)
#define OPEN_CFW_BLE_PROFILE_CONNECTION_ROLE(id) open_cfw_test_ble_profile_connection_role(id)
#define OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() open_cfw_test_ble_profile_ota_active()
#define OPEN_CFW_BLE_PROFILE_MESSAGE_ALLOC(size) open_cfw_test_ble_profile_message_alloc(size)
#define OPEN_CFW_BLE_PROFILE_MESSAGE_SEND(handler, message) open_cfw_test_ble_profile_message_send((handler), (message))
#define OPEN_CFW_BLE_PROFILE_NOTIFY(...) open_cfw_test_ble_profile_notify(__VA_ARGS__)
#define OPEN_CFW_BLE_PROFILE_WAIT_TX_READY() open_cfw_test_ble_profile_wait_tx_ready()
#define OPEN_CFW_BLE_PROFILE_TX_COMPLETE_NOTIFY() open_cfw_test_ble_profile_tx_complete_notify()
#define OPEN_CFW_BLE_PROFILE_REMOVE_DELAYED(callback) open_cfw_test_ble_profile_remove_delayed(callback)
#define OPEN_CFW_BLE_PROFILE_EUS_RECEIVE(direction, data, length) open_cfw_test_ble_profile_eus_receive((direction), (data), (length))
#define OPEN_CFW_BLE_PROFILE_EFS_RECEIVE(data, length) open_cfw_test_ble_profile_efs_receive((data), (length))
#define OPEN_CFW_BLE_PROFILE_NUS_RECEIVE(data, length) open_cfw_test_ble_profile_nus_receive((data), (length))
#define OPEN_CFW_BLE_PROFILE_RX_TIMEOUT_CALLBACK ((void (*)(void *))(uintptr_t)0x004b81b9u)

static uint8_t role_by_connection[4];
static uint8_t ota_active;
static uint8_t allocation_fails;
static uint8_t message_storage[64];
static void *last_message;
static uint32_t words[32];

uint8_t open_cfw_test_ble_profile_connection_role(uint8_t id)
{
    return id < 4u ? role_by_connection[id] : 0xffu;
}
uint8_t open_cfw_test_ble_profile_ota_active(void) { return ota_active; }
void *open_cfw_test_ble_profile_message_alloc(uint16_t size)
{
    words[0] += 1u;
    words[1] = size;
    if (allocation_fails != 0u) return 0;
    memset(message_storage, 0, sizeof(message_storage));
    return message_storage;
}
void open_cfw_test_ble_profile_message_send(uint8_t handler, void *message)
{
    words[2] += 1u;
    words[3] = handler;
    last_message = message;
}
void open_cfw_test_ble_profile_notify(uint8_t connection, uint16_t handle, uint16_t length, const uint8_t *data)
{
    words[4] += 1u;
    words[5] = connection;
    words[6] = handle;
    words[7] = length;
    words[8] = data != 0 && length != 0u ? data[0] : 0u;
}
void open_cfw_test_ble_profile_wait_tx_ready(void) { words[9] += 1u; }
void open_cfw_test_ble_profile_tx_complete_notify(void) { words[10] += 1u; }
uint8_t open_cfw_test_ble_profile_remove_delayed(void (*callback)(void *))
{
    words[11] += 1u;
    words[12] = (uintptr_t)callback == 0x004b81b9u;
    return 1u;
}
uint8_t open_cfw_test_ble_profile_eus_receive(uint8_t direction, const uint8_t *data, uint16_t length)
{
    words[13] += 1u;
    words[14] = direction;
    words[15] = length;
    words[16] = data != 0 && length != 0u ? data[0] : 0u;
    return 0u;
}
uint8_t open_cfw_test_ble_profile_efs_receive(const uint8_t *data, uint16_t length)
{
    words[17] += 1u;
    words[18] = length;
    words[19] = data != 0 && length != 0u ? data[0] : 0u;
    return 0u;
}
void open_cfw_test_ble_profile_nus_receive(const uint8_t *data, uint16_t length)
{
    words[20] += 1u;
    words[21] = length;
    words[22] = data != 0 && length != 0u ? data[0] : 0u;
}

#include "../../components/apollo_main/core_overlay/ble_transport_profiles.c"

void open_cfw_test_ble_profile_reset(void)
{
    memset(eus_control_bytes, 0, sizeof(eus_control_bytes));
    memset(ess_control_bytes, 0, sizeof(ess_control_bytes));
    memset(efs_control_bytes, 0, sizeof(efs_control_bytes));
    memset(nus_control_bytes, 0, sizeof(nus_control_bytes));
    memset(role_by_connection, 0, sizeof(role_by_connection));
    memset(words, 0, sizeof(words));
    ota_active = 0u;
    allocation_fails = 0u;
    last_message = 0;
}
void open_cfw_test_ble_profile_set_ota(uint8_t value) { ota_active = value; }
void open_cfw_test_ble_profile_set_alloc_fail(uint8_t value) { allocation_fails = value; }
void open_cfw_test_ble_profile_set_role(uint8_t id, uint8_t value)
{
    if (id < 4u) role_by_connection[id] = value;
}
uint32_t open_cfw_test_ble_profile_word(uint8_t index) { return index < 32u ? words[index] : 0u; }
uint8_t open_cfw_test_ble_profile_control(uint8_t module, uint8_t index)
{
    const uint8_t *controls[4] = {eus_control_bytes, ess_control_bytes, efs_control_bytes, nus_control_bytes};
    return module < 4u && index < 4u ? controls[module][index] : 0xffu;
}
uint32_t open_cfw_test_ble_profile_message_word(uint8_t field)
{
    const struct open_cfw_ble_profile_message *message = (const struct open_cfw_ble_profile_message *)last_message;
    if (message == 0) return 0u;
    switch (field) {
    case 0: return message->parameter;
    case 1: return message->event;
    case 2: return message->length;
    case 3: return message->data != 0 && message->length != 0u ? message->data[0] : 0u;
    default: return 0u;
    }
}
