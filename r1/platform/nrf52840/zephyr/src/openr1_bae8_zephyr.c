#include "openr1_bae8_zephyr.h"

#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/byteorder.h>

#include "openr1/r1_protocol.h"
#include "openr1/r1_runtime.h"

#define OPENR1_COMPANY_IDENTIFIER UINT16_C(0x5245)
#define OPENR1_NOTIFICATION_SLOTS 4u
#define OPENR1_TX1_ATTRIBUTE 4u
#define OPENR1_TX2_ATTRIBUTE 9u

extern r1_runtime *openr1_platform_runtime(void);

static struct bt_uuid_128 bae8_service_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0xbae80001, 0x4f05, 0x4503, 0x8e65,
                       0x3af1f7329d1f));
static struct bt_uuid_128 channel1_rx_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0xbae80010, 0x4f05, 0x4503, 0x8e65,
                       0x3af1f7329d1f));
static struct bt_uuid_128 channel1_tx_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0xbae80011, 0x4f05, 0x4503, 0x8e65,
                       0x3af1f7329d1f));
static struct bt_uuid_128 channel2_rx_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0xbae80012, 0x4f05, 0x4503, 0x8e65,
                       0x3af1f7329d1f));
static struct bt_uuid_128 channel2_tx_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0xbae80013, 0x4f05, 0x4503, 0x8e65,
                       0x3af1f7329d1f));

typedef struct {
    atomic_t busy;
    struct bt_gatt_notify_params parameters;
    uint8_t bytes[R1_BLE_VALUE_MAX];
} openr1_notification_slot;

static openr1_notification_slot notification_slots[OPENR1_NOTIFICATION_SLOTS];
static struct k_work advertise_work;
K_MUTEX_DEFINE(runtime_mutex);

static bool runtime_lock_provider(void *context) {
    (void)context;
    return !k_is_in_isr() && k_mutex_lock(&runtime_mutex, K_FOREVER) == 0;
}

static void runtime_unlock_provider(void *context) {
    (void)context;
    (void)k_mutex_unlock(&runtime_mutex);
}

typedef struct {
    uint8_t index;
    struct bt_conn *connection;
} openr1_connection_query;

static uint16_t connection_id(struct bt_conn *connection) {
    return (uint16_t)bt_conn_index(connection);
}

static void find_connection(struct bt_conn *connection, void *context) {
    openr1_connection_query *query = context;
    if (query->connection == NULL && bt_conn_index(connection) == query->index) {
        query->connection = bt_conn_ref(connection);
    }
}

static struct bt_conn *lookup_connection(uint8_t index) {
    openr1_connection_query query = {
        .index = index,
        .connection = NULL,
    };
    bt_conn_foreach(BT_CONN_TYPE_LE, find_connection, &query);
    return query.connection;
}

static ssize_t write_channel1(
    struct bt_conn *connection, const struct bt_gatt_attr *attribute,
    const void *buffer, uint16_t length, uint16_t offset, uint8_t flags) {
    (void)connection;
    (void)attribute;
    (void)buffer;
    (void)flags;
    if (offset != 0u || length > R1_BLE_VALUE_MAX) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    /* Channel 1 remains fail-closed until its bounded BC/eAT policy is live. */
    return (ssize_t)length;
}

static ssize_t write_channel2(
    struct bt_conn *connection, const struct bt_gatt_attr *attribute,
    const void *buffer, uint16_t length, uint16_t offset, uint8_t flags) {
    (void)attribute;
    (void)flags;
    if (offset != 0u) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    if (length > R1_BLE_VALUE_MAX) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }
    const r1_error error = r1_runtime_receive_eus(
        openr1_platform_runtime(), connection_id(connection), buffer, length);
    return error == R1_ERROR_LENGTH
        ? BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN)
        : (ssize_t)length;
}

static void ccc_changed(const struct bt_gatt_attr *attribute, uint16_t value) {
    (void)attribute;
    (void)value;
}

BT_GATT_SERVICE_DEFINE(openr1_bae8_service,
    BT_GATT_PRIMARY_SERVICE(&bae8_service_uuid.uuid),
    BT_GATT_CHARACTERISTIC(&channel1_rx_uuid.uuid,
        BT_GATT_CHRC_WRITE_WITHOUT_RESP, BT_GATT_PERM_WRITE,
        NULL, write_channel1, NULL),
    BT_GATT_CHARACTERISTIC(&channel1_tx_uuid.uuid,
        BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_NONE, NULL, NULL, NULL),
    BT_GATT_CCC(ccc_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
    BT_GATT_CHARACTERISTIC(&channel2_rx_uuid.uuid,
        BT_GATT_CHRC_WRITE_WITHOUT_RESP, BT_GATT_PERM_WRITE,
        NULL, write_channel2, NULL),
    BT_GATT_CHARACTERISTIC(&channel2_tx_uuid.uuid,
        BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_NONE, NULL, NULL, NULL),
    BT_GATT_CCC(ccc_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE));

static void notification_complete(struct bt_conn *connection, void *context) {
    (void)connection;
    openr1_notification_slot *slot = context;
    r1_runtime_hvn_complete(openr1_platform_runtime(), 1u);
    atomic_clear(&slot->busy);
}

static openr1_notification_slot *allocate_notification_slot(void) {
    for (size_t index = 0u; index < OPENR1_NOTIFICATION_SLOTS; ++index) {
        if (atomic_cas(&notification_slots[index].busy, 0, 1)) {
            return &notification_slots[index];
        }
    }
    return NULL;
}

static r1_tx_status transmit(void *context, const r1_tx_event *event) {
    (void)context;
    if (event == NULL || event->length > R1_BLE_VALUE_MAX ||
        (event->channel != 1u && event->channel != 2u)) {
        return R1_TX_DROP;
    }
    struct bt_conn *connection = lookup_connection((uint8_t)event->connection);
    if (connection == NULL) {
        return R1_TX_DROP;
    }
    const size_t attribute_index = event->channel == 1u
        ? OPENR1_TX1_ATTRIBUTE : OPENR1_TX2_ATTRIBUTE;
    const struct bt_gatt_attr *attribute =
        &openr1_bae8_service.attrs[attribute_index];
    if (!bt_gatt_is_subscribed(connection, attribute, BT_GATT_CCC_NOTIFY)) {
        bt_conn_unref(connection);
        return R1_TX_DROP;
    }
    openr1_notification_slot *slot = allocate_notification_slot();
    if (slot == NULL) {
        bt_conn_unref(connection);
        return R1_TX_RESOURCES;
    }
    memcpy(slot->bytes, event->bytes, event->length);
    slot->parameters = (struct bt_gatt_notify_params){
        .attr = attribute,
        .data = slot->bytes,
        .len = (uint16_t)event->length,
        .func = notification_complete,
        .user_data = slot,
    };
    const int error = bt_gatt_notify_cb(connection, &slot->parameters);
    bt_conn_unref(connection);
    if (error == 0) {
        return R1_TX_SENT;
    }
    atomic_clear(&slot->busy);
    return error == -ENOMEM ? R1_TX_RESOURCES : R1_TX_DROP;
}

static void connected(struct bt_conn *connection, uint8_t error) {
    if (error != 0u) {
        return;
    }
    const uint16_t identifier = connection_id(connection);
    if (r1_runtime_connect(openr1_platform_runtime(), identifier) == R1_OK) {
        (void)bt_conn_set_security(connection, BT_SECURITY_L2);
    }
}

static void disconnected(struct bt_conn *connection, uint8_t reason) {
    (void)reason;
    r1_runtime_disconnect(openr1_platform_runtime(), connection_id(connection));
}

static void recycled(void) {
    (void)k_work_submit(&advertise_work);
}

static void security_changed(struct bt_conn *connection, bt_security_t level,
                             enum bt_security_err error) {
    const bool secure = error == BT_SECURITY_ERR_SUCCESS &&
        level >= BT_SECURITY_L2;
    (void)r1_runtime_set_security(
        openr1_platform_runtime(), connection_id(connection),
        secure, secure, secure);
}

BT_CONN_CB_DEFINE(openr1_connection_callbacks) = {
    .connected = connected,
    .disconnected = disconnected,
    .recycled = recycled,
    .security_changed = security_changed,
};

static void hexadecimal_address_name(char name[15], const bt_addr_le_t *address) {
    static const char digits[] = "0123456789ABCDEF";
    static const char prefix[] = "EVEN R1_";
    memcpy(name, prefix, sizeof prefix - 1u);
    size_t output = sizeof prefix - 1u;
    const uint8_t selected[3] = {
        address->a.val[3], address->a.val[2], address->a.val[1]
    };
    for (size_t index = 0u; index < 3u; ++index) {
        name[output++] = digits[selected[index] >> 4u];
        name[output++] = digits[selected[index] & UINT8_C(0x0f)];
    }
    name[output] = '\0';
}

int openr1_bae8_zephyr_start_advertising(void) {
    const struct bt_data advertising_data[] = {
        BT_DATA_BYTES(BT_DATA_FLAGS,
                      BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR),
        BT_DATA_BYTES(BT_DATA_GAP_APPEARANCE, 0x40, 0x02),
    };
    bt_addr_le_t identities[CONFIG_BT_ID_MAX];
    size_t identity_count = ARRAY_SIZE(identities);
    bt_id_get(identities, &identity_count);
    if (identity_count == 0u) {
        return -ENOENT;
    }
    char name[15];
    hexadecimal_address_name(name, &identities[0]);
    int error = bt_set_name(name);
    if (error != 0) {
        return error;
    }
    uint8_t scan_response[2u + 6u];
    sys_put_le16(OPENR1_COMPANY_IDENTIFIER, scan_response);
    memcpy(&scan_response[2], identities[0].a.val, 6u);
    const struct bt_data scan_data[] = {
        BT_DATA(BT_DATA_NAME_COMPLETE, name, strlen(name)),
        BT_DATA(BT_DATA_MANUFACTURER_DATA,
                scan_response, sizeof scan_response),
    };
    return bt_le_adv_start(
                           BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONNECTABLE,
                                           UINT16_C(0x00a0),
                                           UINT16_C(0x00a0), NULL),
                           advertising_data, ARRAY_SIZE(advertising_data),
                           scan_data, ARRAY_SIZE(scan_data));
}

static void advertise_work_handler(struct k_work *work) {
    (void)work;
    (void)openr1_bae8_zephyr_start_advertising();
}

int openr1_bae8_zephyr_initialize(void) {
    memset(notification_slots, 0, sizeof notification_slots);
    k_work_init(&advertise_work, advertise_work_handler);
    r1_runtime_set_transmit(openr1_platform_runtime(), transmit, NULL);
    r1_runtime_set_lock(
        openr1_platform_runtime(), runtime_lock_provider,
        runtime_unlock_provider, NULL);
    return 0;
}
