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
#include <zephyr/settings/settings.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/byteorder.h>
#include <zephyr/sys/reboot.h>
#include <hal/nrf_power.h>

#include "openr1/r1_peer_target.h"
#include "openr1/r1_protocol.h"
#include "openr1/r1_runtime.h"
#include "openr1_databases_zephyr.h"
#include "openr1_power_zephyr.h"
#include "openr1_storage_zephyr.h"
#include "openr1_touch_zephyr.h"

#define OPENR1_COMPANY_IDENTIFIER UINT16_C(0x5245)
#define OPENR1_NOTIFICATION_SLOTS 4u
#define OPENR1_TX1_ATTRIBUTE 4u
#define OPENR1_TX2_ATTRIBUTE 9u
#define OPENR1_FAST_INTERVAL UINT16_C(0x00a0)
#define OPENR1_SLOW_INTERVAL UINT16_C(0x0640)
#define OPENR1_FAST_DURATION_SECONDS 60u
#define OPENR1_OWNER_SETTINGS_KEY "openr1_auth/owner"
#define OPENR1_RECOVERY_REQUEST UINT8_C(0xb1)

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
    bool completes_runtime_credit;
    struct bt_gatt_notify_params parameters;
    uint8_t bytes[R1_BLE_VALUE_MAX];
} openr1_notification_slot;

static openr1_notification_slot notification_slots[OPENR1_NOTIFICATION_SLOTS];
static struct k_work advertise_work;
static struct k_work_delayable slow_advertise_work;
static struct k_work_delayable glasses_slow_work;
static struct k_work_delayable glasses_dcdc_work;
static struct k_work_delayable glasses_connection_slow_work;
static struct k_work_delayable recovery_work;
static struct k_work advertising_targets_work;
static struct k_work_delayable advertising_target_disconnect_work;
static struct k_work nv_recovery_work;
static struct k_work remove_ring_work;
static atomic_t advertising_active;
static atomic_t advertising_slow;
static atomic_t glasses_parameter_connection;
static atomic_t diagnostic_export_connection;
static atomic_t advertising_target_disconnect_connection;
static atomic_t remove_ring_pending;
static atomic_t remove_ring_failures;
static r1_owner_authorization_state owner_state;
K_MUTEX_DEFINE(runtime_mutex);
K_MUTEX_DEFINE(owner_mutex);

typedef struct {
    uint8_t first[R1_PEER_ADDRESS_SIZE];
    uint8_t second[R1_PEER_ADDRESS_SIZE];
} openr1_advertising_targets_request;

K_MSGQ_DEFINE(advertising_targets_queue,
              sizeof(openr1_advertising_targets_request), 4u, 4u);

typedef struct {
    uint16_t expected_crc;
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES];
} openr1_nv_recovery_request;

K_MSGQ_DEFINE(nv_recovery_queue, sizeof(openr1_nv_recovery_request), 2u, 4u);

static int stop_advertising(bool cancel_transition);
static void reconcile_advertising_roles(void);
static r1_tx_status transmit_event(
    const r1_tx_event *event, bool completes_runtime_credit);

static void diagnostic_export_abort(uint16_t connection) {
    if ((uint16_t)atomic_get(&diagnostic_export_connection) == connection) {
        openr1_storage_zephyr_diagnostic_export_finish();
        atomic_set(&diagnostic_export_connection,
                   (atomic_val_t)R1_INVALID_CONNECTION);
    }
}

bool openr1_bae8_zephyr_diagnostic_export_begin(
    uint16_t connection, r1_log_export_info *info) {
    if (connection == R1_INVALID_CONNECTION || info == NULL ||
        !r1_runtime_connection_is_authorized_phone(
            openr1_platform_runtime(), connection)) {
        return false;
    }
    if (!atomic_cas(
            &diagnostic_export_connection,
            (atomic_val_t)R1_INVALID_CONNECTION,
            (atomic_val_t)connection)) {
        return false;
    }
    if (!r1_runtime_connection_is_authorized_phone(
            openr1_platform_runtime(), connection) ||
        !openr1_storage_zephyr_diagnostic_export_begin(info) ||
        !r1_runtime_connection_is_authorized_phone(
            openr1_platform_runtime(), connection)) {
        diagnostic_export_abort(connection);
        return false;
    }
    return true;
}

bool openr1_bae8_zephyr_diagnostic_export_read(
    uint16_t connection, uint32_t offset, uint8_t *output, size_t length) {
    if ((uint16_t)atomic_get(&diagnostic_export_connection) != connection ||
        !r1_runtime_connection_is_authorized_phone(
            openr1_platform_runtime(), connection)) {
        diagnostic_export_abort(connection);
        return false;
    }
    return openr1_storage_zephyr_diagnostic_export_read(
        offset, output, length);
}

void openr1_bae8_zephyr_diagnostic_export_finish(uint16_t connection) {
    if ((uint16_t)atomic_get(&diagnostic_export_connection) == connection &&
        r1_runtime_connection_is_authorized_phone(
            openr1_platform_runtime(), connection)) {
        diagnostic_export_abort(connection);
    }
}

/* The recovered Nordic connection records use BLE units directly:
 * interval units are 1.25 ms and supervision timeout units are 10 ms. */
static const struct bt_le_conn_param glasses_connection_fast =
    BT_LE_CONN_PARAM_INIT(16u, 16u, 2u, 600u);
static const struct bt_le_conn_param glasses_connection_slow =
    BT_LE_CONN_PARAM_INIT(72u, 84u, 4u, 600u);

static int owner_settings_set(
    const char *name, size_t length, settings_read_cb read_callback,
    void *callback_argument) {
    if (strcmp(name, "owner") != 0) {
        return -ENOENT;
    }
    uint8_t candidate[R1_OWNER_AUTH_RECORD_BYTES];
    if (length != sizeof candidate) {
        (void)r1_owner_authorization_state_load(
            &owner_state, NULL, length);
        return 0;
    }
    const ssize_t read = read_callback(
        callback_argument, candidate, sizeof candidate);
    if (read < 0) {
        (void)r1_owner_authorization_state_load(
            &owner_state, NULL, 0u);
        return (int)read;
    }
    if ((size_t)read != sizeof candidate ||
        !r1_owner_authorization_state_load(
            &owner_state, candidate, (size_t)read)) {
        return 0;
    }
    return 0;
}

SETTINGS_STATIC_HANDLER_DEFINE(
    openr1_owner_settings, "openr1_auth", NULL, owner_settings_set, NULL, NULL);

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

typedef struct {
    const bt_addr_le_t *address;
    bool found;
} openr1_bond_query;

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

static r1_error queue_advertising_targets(
    void *context,
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]) {
    (void)context;
    if (first_target == NULL || second_target == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    openr1_advertising_targets_request request;
    memcpy(request.first, first_target, sizeof request.first);
    memcpy(request.second, second_target, sizeof request.second);
    if (k_msgq_put(&advertising_targets_queue, &request, K_NO_WAIT) != 0) {
        return R1_ERROR_CAPACITY;
    }
    (void)k_work_submit(&advertising_targets_work);
    return R1_OK;
}

static r1_error queue_nv_recovery(
    void *context,
    const uint8_t body[R1_NV_RECOVERY_BODY_BYTES],
    uint16_t expected_crc) {
    (void)context;
    if (body == NULL || expected_crc == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    openr1_nv_recovery_request request = {
        .expected_crc = expected_crc,
    };
    memcpy(request.body, body, sizeof request.body);
    if (k_msgq_put(&nv_recovery_queue, &request, K_NO_WAIT) != 0) {
        return R1_ERROR_CAPACITY;
    }
    (void)k_work_submit(&nv_recovery_work);
    return R1_OK;
}

static void nv_recovery_work_handler(struct k_work *work) {
    (void)work;
    openr1_nv_recovery_request request;
    while (k_msgq_get(&nv_recovery_queue, &request, K_NO_WAIT) == 0) {
        uint8_t changed_records = 0u;
        if (openr1_databases_zephyr_apply_local_nv_recovery(
                request.body, sizeof request.body, request.expected_crc,
                &changed_records) == R1_OK && changed_records != 0u) {
            /* Reinitialize every calibration and identity consumer from the
             * newly committed generation; no response is pending. */
            sys_reboot(SYS_REBOOT_COLD);
        }
    }
}

static r1_error queue_remove_ring(void *context) {
    (void)context;
    if (!atomic_cas(&remove_ring_pending, 0, 1)) {
        return R1_ERROR_CAPACITY;
    }
    if (k_work_submit(&remove_ring_work) < 0) {
        atomic_set(&remove_ring_pending, 0);
        return R1_ERROR_STATE;
    }
    return R1_OK;
}

static void remove_ring_work_handler(struct k_work *work) {
    (void)work;
    if (openr1_databases_zephyr_remove_ring_metadata() != R1_OK) {
        atomic_inc(&remove_ring_failures);
    }
    atomic_set(&remove_ring_pending, 0);
}

static void advertising_target_disconnect_handler(struct k_work *work) {
    (void)work;
    const uint16_t identifier = (uint16_t)atomic_get(
        &advertising_target_disconnect_connection);
    atomic_set(&advertising_target_disconnect_connection,
               (atomic_val_t)R1_INVALID_CONNECTION);
    if (identifier == R1_INVALID_CONNECTION) {
        return;
    }
    struct bt_conn *connection = lookup_connection((uint8_t)identifier);
    if (connection != NULL) {
        (void)bt_conn_disconnect(
            connection, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
        bt_conn_unref(connection);
    }
}

static void advertising_targets_work_handler(struct k_work *work) {
    (void)work;
    openr1_advertising_targets_request request;
    while (k_msgq_get(&advertising_targets_queue, &request, K_NO_WAIT) == 0) {
        if (openr1_databases_zephyr_persist_peer_targets(
                request.first, request.second) != R1_OK) {
            continue;
        }
        r1_runtime *runtime = openr1_platform_runtime();
        bool glasses_connected = false;
        uint16_t glasses_connection = R1_INVALID_CONNECTION;
        for (uint16_t identifier = 0u;
             identifier < (uint16_t)CONFIG_BT_MAX_CONN; ++identifier) {
            if (r1_runtime_connection_role(runtime, identifier) ==
                    R1_ROLE_GLASSES) {
                glasses_connected = true;
                glasses_connection = identifier;
                break;
            }
        }
        uint8_t peer[R1_PEER_ADDRESS_SIZE] = {0u};
        bool peer_available = false;
        if (glasses_connected) {
            struct bt_conn *connection = lookup_connection(
                (uint8_t)glasses_connection);
            if (connection != NULL) {
                const bt_addr_le_t *address = bt_conn_get_dst(connection);
                if (address != NULL) {
                    memcpy(peer, address->a.val, sizeof peer);
                    peer_available = true;
                }
                bt_conn_unref(connection);
            }
        }
        bool phone_occupied = false;
        bool glasses_occupied = false;
        r1_runtime_role_occupancy(
            runtime, &phone_occupied, &glasses_occupied);
        r1_connection_control_plan plan;
        if (r1_connection_control_plan_adv_start(
                glasses_connected, glasses_connection,
                peer_available, peer, request.first, request.second,
                phone_occupied, glasses_occupied, &plan) != R1_OK) {
            continue;
        }
        if (plan.schedule_disconnect) {
            atomic_set(&advertising_target_disconnect_connection,
                       (atomic_val_t)plan.disconnect_connection);
            (void)k_work_reschedule(
                &advertising_target_disconnect_work,
                K_TICKS(plan.disconnect_delay));
        }
        if (plan.start_fast_advertising) {
            (void)stop_advertising(true);
            (void)openr1_bae8_zephyr_start_advertising();
        } else if (plan.stop_advertising) {
            (void)stop_advertising(true);
        }
    }
}

static void find_bond(const struct bt_bond_info *information, void *context) {
    openr1_bond_query *query = context;
    if (bt_addr_le_eq(&information->addr, query->address)) {
        query->found = true;
    }
}

static bool connection_is_bonded(const bt_addr_le_t *address) {
    openr1_bond_query query = {
        .address = address,
        .found = false,
    };
    bt_foreach_bond(BT_ID_DEFAULT, find_bond, &query);
    return query.found;
}

static void apply_owner_authorization(struct bt_conn *connection,
                                      bool encrypted,
                                      bool permit_enrollment) {
    const uint16_t identifier = connection_id(connection);
    struct bt_conn_info information;
    if (!encrypted || bt_conn_get_info(connection, &information) != 0 ||
        information.type != BT_CONN_TYPE_LE || information.le.dst == NULL ||
        !bt_addr_le_is_identity(information.le.dst)) {
        (void)r1_runtime_set_security(
            openr1_platform_runtime(), identifier, encrypted, false, false);
        diagnostic_export_abort(identifier);
        return;
    }
    const bt_addr_le_t *identity = information.le.dst;
    const bool bonded = connection_is_bonded(identity);
    bool authorized = false;
    if (bonded && k_mutex_lock(&owner_mutex, K_FOREVER) == 0) {
        if (owner_state.loaded) {
            authorized = r1_owner_authorization_state_matches(
                &owner_state, identity->type,
                identity->a.val);
        } else if (!owner_state.corrupt && permit_enrollment) {
            uint8_t candidate[R1_OWNER_AUTH_RECORD_BYTES];
            if (r1_owner_authorization_encode(
                    identity->type, identity->a.val, candidate) == R1_OK &&
                settings_save_one(
                    OPENR1_OWNER_SETTINGS_KEY, candidate,
                    sizeof candidate) == 0) {
                authorized = r1_owner_authorization_state_load(
                    &owner_state, candidate, sizeof candidate);
            }
        }
        (void)k_mutex_unlock(&owner_mutex);
    }
    (void)r1_runtime_set_security(
        openr1_platform_runtime(), identifier, encrypted, bonded, authorized);
    if (!r1_runtime_connection_is_authorized_phone(
            openr1_platform_runtime(), identifier)) {
        diagnostic_export_abort(identifier);
    }
}

static ssize_t write_channel1(
    struct bt_conn *connection, const struct bt_gatt_attr *attribute,
    const void *buffer, uint16_t length, uint16_t offset, uint8_t flags) {
    (void)attribute;
    (void)flags;
    if (offset != 0u) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    if (buffer == NULL || length > R1_LEGACY_COMMAND_WORKSPACE_SIZE) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }
    uint8_t workspace[R1_LEGACY_COMMAND_WORKSPACE_SIZE];
    r1_legacy_command_route route = R1_LEGACY_COMMAND_ROUTE_NONE;
    const r1_error route_error = r1_legacy_command_route_frame(
        buffer, length, workspace, sizeof workspace, &route);
    if (route_error == R1_ERROR_LENGTH) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }
    /* The only live BC command is the bounded, independently authorized
     * glasses-status lifecycle. Every other legacy/factory/eAT destination
     * remains unreachable from channel 1. */
    if (route_error != R1_OK || route != R1_LEGACY_COMMAND_ROUTE_0X89) {
        return (ssize_t)length;
    }
    const bool command_valid = workspace[3] == 1u;
    const uint8_t status_bits = workspace[4];
    r1_glasses_status_plan plan;
    const r1_error error = r1_runtime_receive_glasses_status(
        openr1_platform_runtime(), connection_id(connection),
        command_valid, status_bits, &plan);
    if (error != R1_OK) {
        return BT_GATT_ERR(BT_ATT_ERR_AUTHORIZATION);
    }
    if (plan.cancel_slow_event) {
        (void)k_work_cancel_delayable(&glasses_slow_work);
    }
    if (plan.open_touch) {
        (void)openr1_touch_zephyr_acquire(
            OPENR1_TOUCH_ZEPHYR_SOURCE_WEAR);
    }
    if (plan.schedule_slow_event) {
        (void)k_work_reschedule(
            &glasses_slow_work, K_TICKS(plan.slow_delay_ticks));
    }
    if (plan.cancel_dcdc_event) {
        (void)k_work_cancel_delayable(&glasses_dcdc_work);
    }
    if (plan.disable_dcdc_now) {
        (void)openr1_power_zephyr_set_reg1(false);
    }
    if (plan.schedule_dcdc_enable) {
        (void)k_work_reschedule(
            &glasses_dcdc_work, K_TICKS(plan.dcdc_delay_ticks));
    }
    atomic_set(&glasses_parameter_connection,
               (atomic_val_t)connection_id(connection));
    if (plan.set_touch_fast_mode) {
        (void)k_work_cancel_delayable(&glasses_connection_slow_work);
        (void)bt_conn_le_param_update(
            connection, &glasses_connection_fast);
    } else if (plan.set_ble_slow_mode) {
        (void)k_work_cancel_delayable(&glasses_connection_slow_work);
        (void)k_work_reschedule(
            &glasses_connection_slow_work,
            K_TICKS(plan.ble_slow_delay_ticks));
    }
    workspace[4] = 1u;
    r1_tx_event response = {
        .connection = connection_id(connection),
        .channel = 1u,
        .length = plan.response_length,
    };
    memcpy(response.bytes, workspace, plan.response_length);
    (void)transmit_event(&response, false);
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
    if (error == R1_OK && r1_runtime_take_recovery_request(
            openr1_platform_runtime(), connection_id(connection))) {
        (void)k_work_reschedule(&recovery_work, K_MSEC(500));
    }
    (void)k_work_submit(&advertise_work);
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
    if (slot->completes_runtime_credit) {
        r1_runtime_hvn_complete(openr1_platform_runtime(), 1u);
    }
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

static r1_tx_status transmit_event(
    const r1_tx_event *event, bool completes_runtime_credit) {
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
    slot->completes_runtime_credit = completes_runtime_credit;
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

static r1_tx_status transmit(void *context, const r1_tx_event *event) {
    (void)context;
    return transmit_event(event, true);
}

static void glasses_slow_work_handler(struct k_work *work) {
    (void)work;
    (void)openr1_touch_zephyr_release(
        OPENR1_TOUCH_ZEPHYR_SOURCE_WEAR);
}

static void glasses_dcdc_work_handler(struct k_work *work) {
    (void)work;
    (void)openr1_power_zephyr_set_reg1(true);
}

static void glasses_connection_slow_work_handler(struct k_work *work) {
    (void)work;
    const uint16_t identifier =
        (uint16_t)atomic_get(&glasses_parameter_connection);
    if (identifier == R1_INVALID_CONNECTION ||
        r1_runtime_connection_role(
            openr1_platform_runtime(), identifier) != R1_ROLE_GLASSES) {
        return;
    }
    struct bt_conn *connection = lookup_connection((uint8_t)identifier);
    if (connection == NULL) {
        return;
    }
    (void)bt_conn_le_param_update(connection, &glasses_connection_slow);
    bt_conn_unref(connection);
}

static void recovery_work_handler(struct k_work *work) {
    (void)work;
    nrf_power_gpregret_set(NRF_POWER, 0u, OPENR1_RECOVERY_REQUEST);
    sys_reboot(SYS_REBOOT_COLD);
}

static void connected(struct bt_conn *connection, uint8_t error) {
    if (error != 0u) {
        return;
    }
    const uint16_t identifier = connection_id(connection);
    /* Connectable legacy advertising stops when a peripheral link is made.
     * Clear the observed state before scheduling the second-role advertiser. */
    atomic_clear(&advertising_active);
    atomic_clear(&advertising_slow);
    (void)k_work_cancel_delayable(&slow_advertise_work);
    if (r1_runtime_connect(openr1_platform_runtime(), identifier) == R1_OK) {
        (void)bt_conn_set_security(connection, BT_SECURITY_L2);
        (void)k_work_submit(&advertise_work);
    }
}

static void disconnected(struct bt_conn *connection, uint8_t reason) {
    (void)reason;
    const uint16_t identifier = connection_id(connection);
    if ((uint16_t)atomic_get(&glasses_parameter_connection) == identifier) {
        (void)k_work_cancel_delayable(&glasses_connection_slow_work);
        atomic_set(&glasses_parameter_connection,
                   (atomic_val_t)R1_INVALID_CONNECTION);
    }
    diagnostic_export_abort(identifier);
    r1_runtime_disconnect(openr1_platform_runtime(), identifier);
    (void)k_work_submit(&advertise_work);
}

static void recycled(void) {
    (void)k_work_submit(&advertise_work);
}

static void security_changed(struct bt_conn *connection, bt_security_t level,
                             enum bt_security_err error) {
    const bool secure = error == BT_SECURITY_ERR_SUCCESS &&
        level >= BT_SECURITY_L2;
    apply_owner_authorization(connection, secure, false);
}

static void identity_resolved(struct bt_conn *connection,
                              const bt_addr_le_t *private_address,
                              const bt_addr_le_t *identity) {
    (void)private_address;
    (void)identity;
    apply_owner_authorization(
        connection, bt_conn_get_security(connection) >= BT_SECURITY_L2,
        false);
}

BT_CONN_CB_DEFINE(openr1_connection_callbacks) = {
    .connected = connected,
    .disconnected = disconnected,
    .recycled = recycled,
    .identity_resolved = identity_resolved,
    .security_changed = security_changed,
};

static void pairing_complete(struct bt_conn *connection, bool bonded) {
    apply_owner_authorization(
        connection, bt_conn_get_security(connection) >= BT_SECURITY_L2,
        bonded);
}

static struct bt_conn_auth_info_cb openr1_authentication_callbacks = {
    .pairing_complete = pairing_complete,
};

typedef struct {
    bt_addr_le_t owner;
    bool valid;
} openr1_owner_revoke_context;

static void revoke_owner_connection(
    struct bt_conn *connection, void *context) {
    const openr1_owner_revoke_context *revoke = context;
    if (revoke->valid &&
        bt_addr_le_eq(bt_conn_get_dst(connection), &revoke->owner)) {
        diagnostic_export_abort(connection_id(connection));
        (void)r1_runtime_set_security(
            openr1_platform_runtime(), connection_id(connection),
            false, false, false);
        (void)bt_conn_disconnect(
            connection, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
    }
}

int openr1_bae8_zephyr_revoke_owner(void) {
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    if (k_mutex_lock(&owner_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    openr1_owner_revoke_context revoke = {0};
    uint8_t address_type = 0u;
    revoke.valid = owner_state.loaded && r1_owner_authorization_decode(
        owner_state.record, sizeof owner_state.record,
        &address_type, revoke.owner.a.val);
    revoke.owner.type = address_type;
    int error = settings_delete(OPENR1_OWNER_SETTINGS_KEY);
    if (error == -ENOENT) {
        error = 0;
    }
    if (error == 0) {
        r1_owner_authorization_state_reset(&owner_state);
    }
    (void)k_mutex_unlock(&owner_mutex);
    if (error != 0) {
        return error;
    }
    if (revoke.valid) {
        error = bt_unpair(BT_ID_DEFAULT, &revoke.owner);
        bt_conn_foreach(
            BT_CONN_TYPE_LE, revoke_owner_connection, &revoke);
    }
    return error;
}

static void hexadecimal_address_name(
    char name[19], const bt_addr_le_t *address, bool factory_mode) {
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
    if (factory_mode) {
        static const char suffix[] = "_FAC";
        memcpy(&name[output], suffix, sizeof suffix - 1u);
        output += sizeof suffix - 1u;
    }
    name[output] = '\0';
}

static int start_advertising(uint16_t interval, bool slow) {
    if (atomic_get(&advertising_active) != 0) {
        return 0;
    }
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
    const bool factory_mode = openr1_databases_zephyr_factory_mode();
    char name[19];
    hexadecimal_address_name(name, &identities[0], factory_mode);
    int error = bt_set_name(name);
    if (error != 0) {
        return error;
    }
    uint8_t scan_response[2u + 6u + R1_NV_PRODUCT_SERIAL_BYTES];
    sys_put_le16(OPENR1_COMPANY_IDENTIFIER, scan_response);
    memcpy(&scan_response[2], identities[0].a.val, 6u);
    const bool serial_provisioned =
        openr1_databases_zephyr_product_serial(&scan_response[8]);
    const size_t scan_response_length = 2u + 6u +
        (serial_provisioned ? R1_NV_PRODUCT_SERIAL_BYTES : 0u);
    const struct bt_data scan_data[] = {
        BT_DATA(BT_DATA_NAME_COMPLETE, name, strlen(name)),
        BT_DATA(BT_DATA_MANUFACTURER_DATA,
                scan_response, scan_response_length),
    };
    error = bt_le_adv_start(
        BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONNECTABLE,
                        interval, interval, NULL),
        advertising_data, ARRAY_SIZE(advertising_data),
        scan_data, ARRAY_SIZE(scan_data));
    if (error == 0 || error == -EALREADY) {
        atomic_set(&advertising_active, 1);
        if (slow) {
            atomic_set(&advertising_slow, 1);
        } else if (!factory_mode) {
            atomic_clear(&advertising_slow);
            (void)k_work_reschedule(
                &slow_advertise_work,
                K_SECONDS(OPENR1_FAST_DURATION_SECONDS));
        }
        return 0;
    }
    return error;
}

int openr1_bae8_zephyr_start_advertising(void) {
    return start_advertising(OPENR1_FAST_INTERVAL, false);
}

static int stop_advertising(bool cancel_transition) {
    if (cancel_transition) {
        (void)k_work_cancel_delayable(&slow_advertise_work);
    }
    if (atomic_get(&advertising_active) == 0) {
        atomic_clear(&advertising_slow);
        return 0;
    }
    const int error = bt_le_adv_stop();
    if (error == 0 || error == -EALREADY) {
        atomic_clear(&advertising_active);
        atomic_clear(&advertising_slow);
        return 0;
    }
    return error;
}

static bool both_product_roles_occupied(void) {
    bool phone = false;
    bool glasses = false;
    r1_runtime *runtime = openr1_platform_runtime();
    for (uint16_t connection = 0u;
         connection < (uint16_t)CONFIG_BT_MAX_CONN; ++connection) {
        const r1_peer_role role =
            r1_runtime_connection_role(runtime, connection);
        phone = phone || role == R1_ROLE_PHONE;
        glasses = glasses || role == R1_ROLE_GLASSES;
    }
    return phone && glasses;
}

static void reconcile_advertising_roles(void) {
    if (both_product_roles_occupied()) {
        (void)stop_advertising(true);
    } else if (atomic_get(&advertising_active) == 0) {
        (void)openr1_bae8_zephyr_start_advertising();
    }
}

static void advertise_work_handler(struct k_work *work) {
    (void)work;
    reconcile_advertising_roles();
}

static void slow_advertise_work_handler(struct k_work *work) {
    (void)work;
    if (both_product_roles_occupied() ||
        openr1_databases_zephyr_factory_mode() ||
        atomic_get(&advertising_active) == 0 ||
        atomic_get(&advertising_slow) != 0) {
        return;
    }
    if (stop_advertising(false) == 0) {
        (void)start_advertising(OPENR1_SLOW_INTERVAL, true);
    }
}

int openr1_bae8_zephyr_initialize(void) {
    memset(notification_slots, 0, sizeof notification_slots);
    atomic_clear(&advertising_active);
    atomic_clear(&advertising_slow);
    atomic_set(&glasses_parameter_connection,
               (atomic_val_t)R1_INVALID_CONNECTION);
    atomic_set(&diagnostic_export_connection,
               (atomic_val_t)R1_INVALID_CONNECTION);
    atomic_set(&advertising_target_disconnect_connection,
               (atomic_val_t)R1_INVALID_CONNECTION);
    atomic_clear(&remove_ring_pending);
    atomic_clear(&remove_ring_failures);
    k_msgq_purge(&advertising_targets_queue);
    k_msgq_purge(&nv_recovery_queue);
    k_work_init(&advertise_work, advertise_work_handler);
    k_work_init_delayable(
        &slow_advertise_work, slow_advertise_work_handler);
    k_work_init_delayable(&glasses_slow_work, glasses_slow_work_handler);
    k_work_init_delayable(&glasses_dcdc_work, glasses_dcdc_work_handler);
    k_work_init_delayable(
        &glasses_connection_slow_work,
        glasses_connection_slow_work_handler);
    k_work_init_delayable(&recovery_work, recovery_work_handler);
    k_work_init(&advertising_targets_work,
                advertising_targets_work_handler);
    k_work_init(&nv_recovery_work, nv_recovery_work_handler);
    k_work_init(&remove_ring_work, remove_ring_work_handler);
    k_work_init_delayable(
        &advertising_target_disconnect_work,
        advertising_target_disconnect_handler);
    r1_runtime_set_transmit(openr1_platform_runtime(), transmit, NULL);
    r1_runtime_set_lock(
        openr1_platform_runtime(), runtime_lock_provider,
        runtime_unlock_provider, NULL);
    r1_runtime_set_advertising_targets_handler(
        openr1_platform_runtime(), queue_advertising_targets, NULL);
    r1_runtime_set_nv_recovery_handler(
        openr1_platform_runtime(), queue_nv_recovery, NULL);
    r1_runtime_set_remove_ring_handler(
        openr1_platform_runtime(), queue_remove_ring, NULL);
    return bt_conn_auth_info_cb_register(&openr1_authentication_callbacks);
}

uint32_t openr1_bae8_zephyr_remove_ring_failures(void) {
    return (uint32_t)atomic_get(&remove_ring_failures);
}

typedef struct {
    bool (*diagnostic_export_begin)(
        uint16_t connection, r1_log_export_info *info);
    bool (*diagnostic_export_read)(
        uint16_t connection, uint32_t offset, uint8_t *output,
        size_t length);
    void (*diagnostic_export_finish)(uint16_t connection);
    uint32_t (*remove_ring_failure_count)(void);
} openr1_bae8_diagnostic_api;

__attribute__((used, section(".openr1_platform_api")))
static const openr1_bae8_diagnostic_api bae8_diagnostic_api = {
    .diagnostic_export_begin =
        openr1_bae8_zephyr_diagnostic_export_begin,
    .diagnostic_export_read = openr1_bae8_zephyr_diagnostic_export_read,
    .diagnostic_export_finish = openr1_bae8_zephyr_diagnostic_export_finish,
    .remove_ring_failure_count =
        openr1_bae8_zephyr_remove_ring_failures,
};
